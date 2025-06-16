import os
import yaml
import numpy as np
import torch
from fastapi import FastAPI, File, UploadFile, Form, Header, HTTPException
from fastapi.responses import JSONResponse
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from db import VoiceprintDB
import uvicorn
import logging
import soundfile as sf
import librosa
import tempfile

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# 创建临时目录用于存放上传的音频文件
TMP_DIR = "tmp"
os.makedirs(TMP_DIR, exist_ok=True)

def load_config():
    """
    加载配置文件，优先读取环境变量（适合Docker部署），否则读取本地yaml。
    """
    config_path = os.path.join("data", ".voiceprint.yaml")
    if not os.path.exists(config_path):
        logger.error("配置文件 data/.voiceprint.yaml 未找到，请先配置。")
        raise RuntimeError("请先配置 data/.voiceprint.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

try:
    config = load_config()
    API_TOKEN = config['server']['authorization']
except Exception as e:
    logger.error(f"配置加载失败: {e}")
    raise

# 初始化数据库连接
try:
    db = VoiceprintDB(config['mysql'])
    logger.info("数据库连接成功。")
except Exception as e:
    logger.error(f"数据库连接失败: {e}")
    raise

# 初始化声纹模型（线程安全，建议单进程部署，或用gunicorn单进程模式）
try:
    sv_pipeline = pipeline(
        task=Tasks.speaker_verification, model="iic/speech_campplus_sv_zh-cn_3dspeaker_16k"
    )
    logger.info("声纹模型加载成功。")
except Exception as e:
    logger.error(f"声纹模型加载失败: {e}")
    raise

def _to_numpy(x):
    """
    将torch tensor或其他类型转为numpy数组
    """
    return x.cpu().numpy() if torch.is_tensor(x) else np.asarray(x)

app = FastAPI(
    title="3D-Speaker 声纹识别API",
    description="基于3D-Speaker的声纹注册与识别服务"
)

def check_token(token: str = Header(...)):
    """
    校验接口令牌
    """
    if token != API_TOKEN:
        logger.warning("无效的接口令牌。")
        raise HTTPException(status_code=401, detail="无效的接口令牌")

def ensure_16k_wav(audio_bytes):
    """
    将任意采样率的wav bytes转为16kHz wav临时文件，返回文件路径
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=TMP_DIR) as tmpf:
        tmpf.write(audio_bytes)
        tmp_path = tmpf.name
    # 读取原采样率
    data, sr = sf.read(tmp_path)
    if sr != 16000:
        # librosa重采样，支持多通道
        if data.ndim == 1:
            data_rs = librosa.resample(data, orig_sr=sr, target_sr=16000)
        else:
            data_rs = np.vstack([librosa.resample(data[:, ch], orig_sr=sr, target_sr=16000) for ch in range(data.shape[1])]).T
        sf.write(tmp_path, data_rs, 16000)
    return tmp_path

@app.post("/register", summary="声纹注册")
async def register(
    authorization: str = Header(..., description="接口令牌", alias="authorization"),
    speaker_id: str = Form(..., description="说话人ID"),
    file: UploadFile = File(..., description="WAV音频文件")
):
    """
    注册声纹接口
    参数:
        token: 接口令牌（Header）
        speaker_id: 说话人ID
        file: 说话人音频文件（WAV）
    返回:
        注册结果
    """
    check_token(authorization)
    audio_path = None
    try:
        audio_bytes = await file.read()
        audio_path = ensure_16k_wav(audio_bytes)
        result = sv_pipeline([audio_path], output_emb=True)
        emb = _to_numpy(result["embs"][0]).astype(np.float32)
        db.save_voiceprint(speaker_id, emb)
        logger.info(f"声纹注册成功: {speaker_id}")
        return {"success": True, "msg": f"已登记: {speaker_id}"}
    except Exception as e:
        logger.error(f"声纹注册失败: {e}")
        raise HTTPException(status_code=500, detail=f"声纹注册失败: {e}")
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

@app.post("/identify", summary="声纹识别")
async def identify(
    authorization: str = Header(..., description="接口令牌", alias="authorization"),
    speaker_ids: str = Form(..., description="候选说话人ID，逗号分隔"),
    file: UploadFile = File(..., description="WAV音频文件")
):
    """
    声纹识别接口
    参数:
        token: 接口令牌（Header）
        speaker_ids: 候选说话人ID，逗号分隔
        file: 待识别音频文件（WAV）
    返回:
        识别结果（说话人ID、相似度分数）
    """
    check_token(authorization)
    candidate_ids = [x.strip() for x in speaker_ids.split(",") if x.strip()]
    if not candidate_ids:
        logger.warning("候选说话人ID不能为空。")
        raise HTTPException(status_code=400, detail="候选说话人ID不能为空")
    audio_path = None
    try:
        audio_bytes = await file.read()
        audio_path = ensure_16k_wav(audio_bytes)
        result = sv_pipeline([audio_path], output_emb=True)
        test_emb = _to_numpy(result["embs"][0]).astype(np.float32)
        voiceprints = db.get_voiceprints(candidate_ids)
        if not voiceprints:
            logger.info("未找到候选说话人声纹。")
            return {"speaker_id": "", "score": 0.0}
        similarities = {
            name: float(np.dot(test_emb, emb) / (np.linalg.norm(test_emb) * np.linalg.norm(emb)))
            for name, emb in voiceprints.items()
        }
        match_name = max(similarities, key=similarities.get)
        match_score = similarities[match_name]
        if match_score < 0.2:
            logger.info(f"未识别到说话人，最高分: {match_score}")
            return 
        logger.info(f"识别到说话人: {match_name}, 分数: {match_score}")
        return {"speaker_id": match_name, "score": match_score}
    except Exception as e:
        logger.error(f"声纹识别失败: {e}")
        raise HTTPException(status_code=500, detail=f"声纹识别失败: {e}")
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

@app.get("/", include_in_schema=False)
def root():
    """
    根路径，返回服务运行信息
    """
    return JSONResponse({"msg": "3D-Speaker voiceprint API service running."})

if __name__ == "__main__":
    try:
        logger.info(
            f"服务启动中，监听地址: {config['server']['host']}:{config['server']['port']}，"
            f"文档: http://{config['server']['host']}:{config['server']['port']}/docs"
        )
        print("="*60)
        print(f"3D-Speaker 声纹API服务已启动，访问: http://{config['server']['host']}:{config['server']['port']}/docs")
        print("="*60)
        uvicorn.run(
            "app:app",
            host=config['server']['host'],
            port=config['server']['port'],
        )
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在退出服务。")