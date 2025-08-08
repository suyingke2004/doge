#!/usr/bin/env python3
"""
测试长期记忆更新工具
"""

import unittest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from models import Base, LongTermMemory
from tools.long_term_memory import update_long_term_memory, get_user_long_term_memory


class TestLongTermMemoryTool(unittest.TestCase):
    """测试长期记忆工具"""

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

    def test_update_long_term_memory_new_user(self):
        """测试为新用户创建长期记忆"""
        user_id = "test_user_1"
        profile_summary = "喜欢读书和散步的用户"
        emotion_trends = {"焦虑": 3, "开心": 7}
        important_events = {"2025-07-01": "开始使用翻书小狗"}

        # 更新长期记忆
        success = update_long_term_memory(
            db_session=self.db_session,
            user_id=user_id,
            profile_summary=profile_summary,
            emotion_trends=emotion_trends,
            important_events=important_events
        )

        self.assertTrue(success)

        # 验证记录是否创建成功
        memory = get_user_long_term_memory(self.db_session, user_id)
        self.assertIsNotNone(memory)
        self.assertEqual(memory['profile_summary'], profile_summary)
        self.assertEqual(memory['emotion_trends'], emotion_trends)
        self.assertEqual(memory['important_events'], important_events)

    def test_update_long_term_memory_existing_user(self):
        """测试更新现有用户的长期记忆"""
        user_id = "test_user_2"
        
        # 首先创建记录
        initial_memory = LongTermMemory(
            user_id=user_id,
            profile_summary="初始用户画像",
            emotion_trends={"焦虑": 2},
            important_events={"2025-06-01": "注册账户"}
        )
        self.db_session.add(initial_memory)
        self.db_session.commit()

        # 更新记录
        success = update_long_term_memory(
            db_session=self.db_session,
            user_id=user_id,
            profile_summary="更新后的用户画像",
            emotion_trends={"开心": 8},
            important_events={"2025-07-01": "第一次深度对话"}
        )

        self.assertTrue(success)

        # 验证更新是否成功
        memory = get_user_long_term_memory(self.db_session, user_id)
        self.assertIsNotNone(memory)
        self.assertEqual(memory['profile_summary'], "更新后的用户画像")
        # 检查情绪趋势是否合并
        self.assertEqual(memory['emotion_trends'], {"焦虑": 2, "开心": 8})
        # 检查重要事件是否合并
        self.assertEqual(memory['important_events'], {
            "2025-06-01": "注册账户",
            "2025-07-01": "第一次深度对话"
        })

    def test_update_long_term_memory_partial_update(self):
        """测试部分更新长期记忆"""
        user_id = "test_user_3"
        
        # 首先创建记录
        initial_memory = LongTermMemory(
            user_id=user_id,
            profile_summary="初始用户画像",
            emotion_trends={"焦虑": 2},
            important_events={"2025-06-01": "注册账户"}
        )
        self.db_session.add(initial_memory)
        self.db_session.commit()

        # 只更新用户画像
        success = update_long_term_memory(
            db_session=self.db_session,
            user_id=user_id,
            profile_summary="更新后的用户画像"
            # 不提供其他参数
        )

        self.assertTrue(success)

        # 验证只有用户画像被更新
        memory = get_user_long_term_memory(self.db_session, user_id)
        self.assertIsNotNone(memory)
        self.assertEqual(memory['profile_summary'], "更新后的用户画像")
        # 其他字段应该保持不变
        self.assertEqual(memory['emotion_trends'], {"焦虑": 2})
        self.assertEqual(memory['important_events'], {"2025-06-01": "注册账户"})


if __name__ == '__main__':
    unittest.main()