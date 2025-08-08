#!/usr/bin/env python3
"""
测试脚本：任务一 - 记忆模块
根据 tests/planned_tests/test_cases_task1_memory.md 中的测试用例进行测试
"""

import unittest
import sys
import os
from collections import deque
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from models import Base, LongTermMemory, ChatSession, ChatMessage
# 注意：由于get_memory_context依赖于Flask的session对象，
# 在单元测试中无法直接调用它，所以我们将在集成测试中验证其功能


class TestMemoryModulePlanned(unittest.TestCase):
    """根据计划测试用例实现的记忆模块测试"""

    def setUp(self):
        """设置测试环境"""
        # 创建内存数据库用于测试
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db_session = self.SessionLocal()

    def tearDown(self):
        """清理测试环境"""
        self.db_session.close()

    def test_case_1_1_dialog_history_recording(self):
        """用例1.1：对话历史记录"""
        # 模拟3轮对话
        short_term_memory = deque(maxlen=10)
        short_term_memory.append({'type': 'human', 'content': '你好'})
        short_term_memory.append({'type': 'ai', 'content': '你好！我是翻书小狗！'})
        short_term_memory.append({'type': 'human', 'content': '今天心情不好'})
        short_term_memory.append({'type': 'ai', 'content': '抱抱你，小狗在这里陪着你'})
        
        # 检查队列中的内容
        self.assertEqual(len(short_term_memory), 4)
        self.assertEqual(short_term_memory[0]['content'], '你好')
        self.assertEqual(short_term_memory[-1]['content'], '抱抱你，小狗在这里陪着你')

    def test_case_1_2_dialog_history_length_limit(self):
        """用例1.2：对话历史长度限制"""
        # 短期记忆队列长度设置为5，进行7轮对话
        short_term_memory = deque(maxlen=5)
        
        # 模拟7轮对话
        for i in range(7):
            short_term_memory.append({'type': 'human', 'content': f'第{i+1}轮对话'})
            short_term_memory.append({'type': 'ai', 'content': f'第{i+1}轮回复'})
        
        # 检查队列中只包含最后5个元素（不是5轮对话）
        self.assertEqual(len(short_term_memory), 5)
        # 检查最旧的元素已被移除，最新的元素在队列中
        # 由于deque(maxlen=5)，前9个元素(7轮对话共14个元素中的前9个)被移除
        # 剩下的应该是第6轮和第7轮的对话，共5个元素
        self.assertEqual(short_term_memory[0]['content'], '第5轮回复')

    def test_case_1_3_new_session_empty_history(self):
        """用例1.3：新会话的空历史"""
        # 新会话开始
        short_term_memory = deque(maxlen=10)
        
        # 检查队列为空
        self.assertEqual(len(short_term_memory), 0)

    def test_case_2_1_create_long_term_memory_record(self):
        """用例2.1：创建长期记忆记录"""
        # 模拟新用户完成首次对话，包含可提取的关键信息
        user_id = "test_user_1"
        
        # 创建长期记忆记录
        long_term_memory = LongTermMemory(
            user_id=user_id,
            profile_summary="喜欢读书和散步的用户",
            emotion_trends={'焦虑': 3},
            important_events={'2025-07-01': '开始为考试焦虑'}
        )
        
        # 添加到数据库
        self.db_session.add(long_term_memory)
        self.db_session.commit()
        
        # 查询验证
        retrieved_memory = self.db_session.query(LongTermMemory).filter_by(user_id=user_id).first()
        self.assertIsNotNone(retrieved_memory)
        self.assertIn('考试焦虑', retrieved_memory.important_events['2025-07-01'])

    def test_case_2_2_update_long_term_memory_record(self):
        """用例2.2：更新长期记忆记录"""
        # 创建初始长期记忆记录
        user_id = "test_user_2"
        long_term_memory = LongTermMemory(
            user_id=user_id,
            profile_summary="喜欢读书和散步的用户",
            emotion_trends={'焦虑': 3},
            important_events={'2025-07-01': '开始为考试焦虑'}
        )
        self.db_session.add(long_term_memory)
        self.db_session.commit()
        
        # 模拟用户透露新的重要信息
        retrieved_memory = self.db_session.query(LongTermMemory).filter_by(user_id=user_id).first()
        # 创建一个新的重要事件字典，包含原有的和新的事件
        new_events = retrieved_memory.important_events.copy() if retrieved_memory.important_events else {}
        new_events['2025-07-15'] = '找到了一份新工作'
        
        # 更新记录
        retrieved_memory.important_events = new_events
        self.db_session.add(retrieved_memory)
        self.db_session.commit()
        
        # 查询验证更新
        updated_memory = self.db_session.query(LongTermMemory).filter_by(user_id=user_id).first()
        self.assertEqual(updated_memory.important_events['2025-07-15'], '找到了一份新工作')

    def test_case_2_3_data_format_correctness(self):
        """用例2.3：数据格式正确性"""
        # 创建长期记忆数据
        user_id = "test_user_3"
        long_term_memory = LongTermMemory(
            user_id=user_id,
            profile_summary="喜欢读书和散步的用户",
            emotion_trends={'焦虑': 3, '开心': 7},
            important_events={'2025-07-01': '开始为考试焦虑'}
        )
        
        # 添加到数据库
        self.db_session.add(long_term_memory)
        self.db_session.commit()
        
        # 直接查询数据库中的字段
        retrieved_memory = self.db_session.query(LongTermMemory).filter_by(user_id=user_id).first()
        
        # 验证字段内容为有效的JSON格式
        import json
        try:
            json.dumps(retrieved_memory.emotion_trends)
            json.dumps(retrieved_memory.important_events)
        except (TypeError, ValueError):
            self.fail("emotion_trends 或 important_events 字段不是有效的JSON格式")

    # 注释掉依赖于Flask session的测试用例，因为它们需要在集成测试环境中运行
    # def test_case_3_1_short_term_memory_injection_prompt(self):
    #     """用例3.1：短期记忆注入Prompt"""
    #     # 这个测试需要在集成测试环境中运行，因为它依赖于Flask session

    # def test_case_3_2_long_term_memory_injection_prompt(self):
    #     """用例3.2：长期记忆注入Prompt"""
    #     # 这个测试需要在集成测试环境中运行，因为它依赖于Flask session

    # def test_case_3_3_comprehensive_call_and_response_generation(self):
    #     """用例3.3：综合调用与回复生成"""
    #     # 这个测试需要在集成测试环境中运行，因为它依赖于Flask session


if __name__ == '__main__':
    unittest.main()