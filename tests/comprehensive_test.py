#!/usr/bin/env python3
"""
综合测试用例：测试记忆模块、RAG知识库和RAG检索生成功能
"""

import unittest
import sys
import os
from collections import deque
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from models import Base, LongTermMemory
from tools.long_term_memory import update_long_term_memory, get_user_long_term_memory
from scripts.process_texts import process_knowledge_base
from tools.knowledge_base_search import search_knowledge_base


class ComprehensiveTest(unittest.TestCase):
    """综合测试类"""

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

    def test_task1_short_term_memory(self):
        """任务一：测试短期记忆功能"""
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
        
        # 验证最旧的元素被移除
        self.assertEqual(short_term_memory[0]['content'], '你好！我是翻书小狗！')

    def test_task1_long_term_memory(self):
        """任务一：测试长期记忆功能"""
        user_id = "test_user_comprehensive"
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

    def test_task2_rag_knowledge_base(self):
        """任务二：测试RAG知识库建设"""
        # 这里我们验证知识库文件是否存在
        knowledge_files = [
            "knowledge_base/sources/cbt.txt",
            "knowledge_base/sources/emotion_regulation.txt",
            "knowledge_base/sources/mindfulness.txt"
        ]
        
        for file_path in knowledge_files:
            self.assertTrue(os.path.exists(file_path), f"知识库文件 {file_path} 不存在")
        
        # 检查向量数据库文件是否存在
        vector_db_path = "knowledge_base/vector_db.index"
        metadata_path = "knowledge_base/metadata.npy"
        
        # 如果文件不存在，运行处理脚本
        if not os.path.exists(vector_db_path) or not os.path.exists(metadata_path):
            # 切换到项目根目录
            original_cwd = os.getcwd()
            os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')
            try:
                process_knowledge_base()
            finally:
                os.chdir(original_cwd)
        
        # 验证向量数据库文件已创建
        self.assertTrue(os.path.exists(vector_db_path), "向量数据库文件未创建")
        self.assertTrue(os.path.exists(metadata_path), "元数据文件未创建")

    def test_task3_rag_search_and_generation(self):
        """任务三：测试RAG检索与生成"""
        # 测试相关查询的检索
        query = "我感到很焦虑，怎么办？"
        result = search_knowledge_base(query)
        
        # 验证返回结果不为空
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "")
        self.assertNotIn("知识库检索出错", result)
        
        # 验证结果包含与焦虑相关的内容
        result_lower = result.lower()
        self.assertTrue(
            "焦虑" in result_lower or 
            "情绪" in result_lower or 
            "调节" in result_lower,
            "检索结果应该包含与焦虑相关的内容"
        )
        
        # 测试不相关查询的检索
        query_unrelated = "今天晚上吃什么？"
        result_unrelated = search_knowledge_base(query_unrelated)
        
        # 验证返回结果不为空（即使不相关也会返回一些内容）
        self.assertIsNotNone(result_unrelated)
        self.assertNotEqual(result_unrelated, "")
        
        # 检查是否确实与查询不相关（这个检查比较宽松）
        # 我们不期望找到与"吃什么"直接相关的内容
        self.assertNotIn("菜谱", result_unrelated.lower())

    def test_integration_all_tasks(self):
        """集成测试：测试所有任务的协同工作"""
        # 1. 创建短期记忆
        short_term_memory = deque(maxlen=10)
        short_term_memory.append({'type': 'human', 'content': '我最近在为考试焦虑'})
        short_term_memory.append({'type': 'ai', 'content': '抱抱你，小狗知道考试会让人紧张'})
        short_term_memory.append({'type': 'human', 'content': '昨晚没睡好'})
        
        # 2. 创建长期记忆
        user_id = "integration_test_user"
        profile_summary = "为考试焦虑的学生"
        emotion_trends = {"焦虑": 7}
        important_events = {"2025-08-09": "开始为考试焦虑"}
        
        success = update_long_term_memory(
            db_session=self.db_session,
            user_id=user_id,
            profile_summary=profile_summary,
            emotion_trends=emotion_trends,
            important_events=important_events
        )
        self.assertTrue(success)
        
        # 3. 使用RAG工具检索相关信息
        query = "今天感觉压力好大"
        knowledge_result = search_knowledge_base(query)
        
        # 验证检索结果不为空
        self.assertIsNotNone(knowledge_result)
        self.assertNotEqual(knowledge_result, "")
        
        # 4. 验证结果包含与压力、焦虑相关的内容
        knowledge_lower = knowledge_result.lower()
        self.assertTrue(
            "焦虑" in knowledge_lower or 
            "压力" in knowledge_lower or 
            "情绪" in knowledge_lower or
            "调节" in knowledge_lower,
            "检索结果应该包含与压力或焦虑相关的内容"
        )


if __name__ == '__main__':
    unittest.main()