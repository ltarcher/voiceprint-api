# 第一阶段：构建Python依赖
FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 第二阶段：生产镜像
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends libopus0 ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制Python依赖
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# 复制应用代码
COPY . .

# 创建临时目录
RUN mkdir -p /app/tmp

# 启动应用
CMD ["python", "app.py"]