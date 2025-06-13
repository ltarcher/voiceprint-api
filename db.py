import pymysql
import numpy as np

class VoiceprintDB:
    """
    声纹数据库操作类，负责声纹特征的存储与读取。
    """

    def __init__(self, config):
        """
        初始化数据库连接。

        :param config: dict，包含数据库连接信息（host, port, user, password, database）
        """
        self.conn = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4',
            autocommit=True
        )

    def save_voiceprint(self, speaker_id, emb):
        """
        保存或更新声纹特征。

        :param speaker_id: str，说话人ID
        :param emb: np.ndarray，声纹特征向量
        """
        with self.conn.cursor() as cursor:
            sql = """
            INSERT INTO voiceprints (speaker_id, feature_vector)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE feature_vector=VALUES(feature_vector)
            """
            cursor.execute(sql, (speaker_id, emb.tobytes()))

    def get_voiceprints(self, speaker_ids=None):
        """
        获取指定说话人ID的声纹特征（如未指定则获取全部）。

        :param speaker_ids: list[str]，说话人ID列表
        :return: dict，{speaker_id: np.ndarray}
        """
        with self.conn.cursor() as cursor:
            if speaker_ids:
                format_strings = ','.join(['%s'] * len(speaker_ids))
                sql = f"SELECT speaker_id, feature_vector FROM voiceprints WHERE speaker_id IN ({format_strings})"
                cursor.execute(sql, tuple(speaker_ids))
            else:
                sql = "SELECT speaker_id, feature_vector FROM voiceprints"
                cursor.execute(sql)
            results = cursor.fetchall()
            # 将数据库中的二进制特征转为numpy数组
            return {row[0]: np.frombuffer(row[1], dtype=np.float32) for row in results}