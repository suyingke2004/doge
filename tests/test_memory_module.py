import unittest
from collections import deque
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, LongTermMemory

class TestMemoryModule(unittest.TestCase):
    def setUp(self):
        # 创建内存数据库用于测试
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db_session = self.SessionLocal()

    def tearDown(self):
        self.db_session.close()

    def test_short_term_memory(self):
        """测试短期记忆功能"""
        # 创建一个deque作为短期记忆，最大长度为3
        short_term_memory = deque(maxlen=3)
        
        # 添加对话历史
        short_term_memory.append({'type': 'human', 'content': '你好'})
        short_term_memory.append({'type': 'ai', 'content': '你好！我是翻书小狗！'})
        short_term_memory.append({'type': 'human', 'content': '今天心情不好'})
        short_term_memory.append({'type': 'ai', 'content': '抱抱你，小狗在这里陪着你'})
        
        # 验证长度不超过3
        self.assertEqual(len(short_term_memory), 3)
        
        # 验证最新的元素在末尾
        self.assertEqual(short_term_memory[-1]['content'], '抱抱你，小狗在这里陪着你')
        
        # 验证最旧的元素被移除（第一个元素应该是"你好！我是翻书小狗！"之后的元素）
        self.assertEqual(short_term_memory[0]['content'], '你好！我是翻书小狗！')

    def test_long_term_memory_model(self):
        """测试长期记忆模型"""
        # 创建长期记忆记录
        long_term_memory = LongTermMemory(
            user_id='test_user_123',
            profile_summary='喜欢读书和散步的用户',
            emotion_trends={'焦虑': 3, '开心': 7},
            important_events={'2025-07-01': '开始使用翻书小狗'}
        )
        
        # 添加到数据库
        self.db_session.add(long_term_memory)
        self.db_session.commit()
        
        # 查询验证
        retrieved_memory = self.db_session.query(LongTermMemory).filter_by(user_id='test_user_123').first()
        self.assertIsNotNone(retrieved_memory)
        self.assertEqual(retrieved_memory.profile_summary, '喜欢读书和散步的用户')
        self.assertEqual(retrieved_memory.emotion_trends, {'焦虑': 3, '开心': 7})
        self.assertEqual(retrieved_memory.important_events, {'2025-07-01': '开始使用翻书小狗'})

if __name__ == '__main__':
    unittest.main()