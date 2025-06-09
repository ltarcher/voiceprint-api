import numpy as np
import torch
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

# 初始化
sv_pipeline = pipeline(
    task=Tasks.speaker_verification, model="iic/speech_campplus_sv_zh-cn_3dspeaker_16k"
)

voiceprints = {}


def _to_numpy(x):
    return x.cpu().numpy() if torch.is_tensor(x) else np.asarray(x)


def register_voiceprint(name, audio_path):
    """登记声纹特征"""
    result = sv_pipeline([audio_path], output_emb=True)
    emb = _to_numpy(result["embs"][0])  # 1 条音频只取第 0 条
    voiceprints[name] = emb
    print(f"已登记: {name}")


def identify_speaker(audio_path):
    """识别声纹所属"""
    test_result = sv_pipeline([audio_path], output_emb=True)
    test_emb = _to_numpy(test_result["embs"][0])

    similarities = {}
    for name, emb in voiceprints.items():
        cos_sim = np.dot(test_emb, emb) / (
            np.linalg.norm(test_emb) * np.linalg.norm(emb)
        )
        similarities[name] = cos_sim

    match_name = max(similarities, key=similarities.get)
    return match_name, similarities[match_name], similarities


if __name__ == "__main__":
    register_voiceprint("max_output_size", "test//test0.wav")
    register_voiceprint("tts1", "test//test1.wav")

    test_file = "test//test2.wav"
    match_name, match_score, all_scores = identify_speaker(test_file)

    print(f"\n识别结果: {test_file} 属于 {match_name}")
    print(f"匹配分数: {match_score:.4f}")
    print("\n所有声纹对比分数:")
    for name, score in all_scores.items():
        print(f"{name}: {score:.4f}")
