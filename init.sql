-- 对数据库：如果不存在则创建
CREATE DATABASE IF NOT EXISTS voiceprint_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 切换到目标数据库
USE voiceprint_db;

-- 对表：如果不存在则创建
CREATE TABLE IF NOT EXISTS voiceprints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    speaker_id VARCHAR(255) NOT NULL UNIQUE,
    feature_vector LONGBLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_speaker_id (speaker_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;