# voiceprint-api

基于3D-Speaker的声纹识别API服务

## 项目简介

本项目是一个基于FastAPI开发的声纹识别HTTP服务，使用3D-Speaker模型实现声纹识别功能。支持声纹注册和识别功能，并提供完整的API文档。

目前用于[xiaozhi-esp32-server](https://github.com/xinnan-tech/xiaozhi-esp32-server)项目，识别小智设备说话人

## 主要功能

1. 声纹注册
   - 输入：说话人ID和声音WAV文件
   - 输出：注册成功状态

2. 声纹识别
   - 输入：可能的说话人ID列表（逗号分隔）和声音WAV文件
   - 输出：识别到的说话人ID（未识别则返回空）

## 技术栈

- FastAPI：Web框架
- 3D-Speaker：声纹识别模型
- MySQL：数据存储

## 安装说明

1. 克隆项目
```bash
git clone https://github.com/xinnan-tech/voiceprint-api.git
cd voiceprint-api
```

2. 安装依赖
```bash
conda remove -n voiceprint-api --all -y
conda create -n voiceprint-api python=3.11 -y
conda activate voiceprint-api

pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip install -r requirements.txt
```

3. 配置数据库
- 创建数据库
```
CREATE DATABASE voiceprint_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
- 创建数据表
```
CREATE TABLE voiceprints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    speaker_id VARCHAR(50) UNIQUE,
    feature_vector LONGBLOB NOT NULL,
    INDEX idx_speaker_id (speaker_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```
- 复制 `voiceprint.yaml` 为 `data/.voiceprint.yaml`

  4. 启动
```
python app.py
```