# 3D-Speaker 声纹识别API

基于3D-Speaker模型的声纹识别服务，提供声纹注册、识别、删除等功能。

## 🚀 新版本特性

### 架构重构
- **模块化设计**: 清晰的目录结构，便于维护和扩展
- **高并发支持**: 使用gunicorn + gevent，支持高并发访问
- **配置管理**: 统一的配置管理，支持环境变量和配置文件
- **日志系统**: 完善的日志记录和监控
- **错误处理**: 统一的异常处理和错误响应

### 性能优化
- **连接池**: 数据库连接池，提高并发性能
- **异步处理**: 支持异步音频处理
- **内存管理**: 优化的内存使用和临时文件清理
- **缓存策略**: 模型预加载，减少响应时间

## 📁 项目结构

```
voiceprint-api/
├── app/                          # 应用主目录
│   ├── main.py                   # FastAPI应用入口
│   ├── core/                     # 核心模块
│   │   ├── config.py             # 配置管理
│   │   ├── security.py           # 安全认证
│   │   └── logging.py            # 日志配置
│   ├── api/                      # API模块
│   │   ├── v1/                   # API v1版本
│   │   │   ├── endpoints/        # API端点
│   │   │   │   ├── voiceprint.py # 声纹相关API
│   │   │   │   └── health.py     # 健康检查API
│   │   │   └── api.py            # API路由
│   │   └── dependencies.py       # API依赖
│   ├── models/                   # 数据模型
│   │   └── voiceprint.py         # 声纹数据模型
│   ├── services/                 # 业务服务
│   │   └── voiceprint_service.py # 声纹识别服务
│   ├── database/                 # 数据库模块
│   │   ├── connection.py         # 数据库连接
│   │   └── voiceprint_db.py      # 声纹数据库操作
│   └── utils/                    # 工具模块
│       └── audio_utils.py        # 音频处理工具
├── data/                       # 配置文件
│   └── .voiceprint.yaml           # 主配置文件
├── tmp/                          # 临时文件目录
├── start_server.py               # 生产环境启动脚本
├── requirements.txt              # Python依赖
├── Dockerfile                    # Docker配置
└── README.md                     # 项目文档
```

## 🛠️ 安装和配置

### 1. 环境要求
- Python 3.9+
- MySQL 5.7+
- 至少4GB内存（用于模型加载）

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 数据库配置
创建MySQL数据库和表：
```sql
CREATE DATABASE voiceprint_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE voiceprint_db;

CREATE TABLE voiceprints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    speaker_id VARCHAR(255) NOT NULL UNIQUE,
    feature_vector LONGBLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_speaker_id (speaker_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 4. 配置文件
复制voiceprint.yaml到data目录，并编辑 `data/.voiceprint.yaml`：
```yaml
mysql:
  host: "127.0.0.1"
  port: 3306
  user: "root"
  password: "your_password"
  database: "voiceprint_db"
```

## 🚀 启动服务

### 开发环境
```bash
python -m app.main
```

### 生产环境
```bash
python start_server.py
```

### Docker部署
```bash
docker build -t voiceprint-api .
docker run -d -p 8005:8005 --name voiceprint-api voiceprint-api
```

## 📚 API文档

启动服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8005/docs
- ReDoc: http://localhost:8005/redoc

### 主要API接口

#### 1. 声纹注册
```http
POST /api/v1/voiceprint/register
Content-Type: multipart/form-data
Authorization: Bearer <your_token>

speaker_id: user_001
file: audio.wav
```

#### 2. 声纹识别
```http
POST /api/v1/voiceprint/identify
Content-Type: multipart/form-data
Authorization: Bearer <your_token>

speaker_ids: user_001,user_002,user_003
file: audio.wav
```

#### 3. 删除声纹
```http
DELETE /api/v1/voiceprint/{speaker_id}
Authorization: Bearer <your_token>
```

#### 4. 获取所有说话人
```http
GET /api/v1/voiceprint/speakers
Authorization: Bearer <your_token>
```

#### 5. 健康检查
```http
GET /api/v1/health
```

## 🔧 高并发配置

### 1. 系统级优化
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 增加网络连接数
echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
sysctl -p
```

### 2. 数据库优化
```sql
-- 增加连接数
SET GLOBAL max_connections = 1000;
SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB
```

### 3. 应用级优化
- 使用连接池管理数据库连接
- 异步处理音频文件
- 合理的超时设置
- 内存监控和清理

## 📊 监控和日志

### 日志文件
- 应用日志: `voiceprint_api.log`
- 访问日志: stdout
- 错误日志: stderr

### 监控指标
- 请求响应时间
- 并发连接数
- 内存使用情况
- 数据库连接状态

## 🔒 安全特性

- API令牌认证
- 文件类型验证
- 音频文件大小限制
- 临时文件自动清理
- CORS配置

## 🐛 故障排除

### 常见问题

1. **模型加载失败**
   - 检查网络连接
   - 确保有足够的内存
   - 检查modelscope版本

2. **数据库连接失败**
   - 检查数据库配置
   - 确保数据库服务运行
   - 检查网络连接

3. **音频处理失败**
   - 检查音频文件格式
   - 确保音频文件完整
   - 检查磁盘空间

### 日志查看
```bash
# 查看应用日志
tail -f voiceprint_api.log

# 查看Docker日志
docker logs -f voiceprint-api
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。