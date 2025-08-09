#!/usr/bin/env python3
"""
测试RAG工具在实际场景中的表现
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from tools.knowledge_base_search import search_knowledge_base


class TestRAGRealWorldScenarios(unittest.TestCase):
    """测试RAG工具在实际场景中的表现"""

    def test_anxiety_related_queries(self):
        """测试与焦虑相关的查询"""
        queries = [
            "我感到很焦虑，怎么办？",
            "如何缓解焦虑情绪？",
            "焦虑的时候应该做什么？",
            "考试前很紧张焦虑，有什么方法吗？"
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = search_knowledge_base(query)
                self.assertIsInstance(result, str)
                self.assertGreater(len(result), 0)
                # 检查结果是否包含焦虑相关的关键词
                self.assertTrue(
                    any(keyword in result.lower() for keyword in ["焦虑", "紧张", "放松", "深呼吸", "调节"]),
                    f"查询 '{query}' 的结果应该包含与焦虑相关的建议"
                )

    def test_procrastination_related_queries(self):
        """测试与拖延症相关的查询"""
        queries = [
            "我有拖延症，怎么办？",
            "如何克服拖延症？",
            "总是拖延怎么办？",
            "怎样提高执行力？"
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = search_knowledge_base(query)
                self.assertIsInstance(result, str)
                self.assertGreater(len(result), 0)
                # 检查结果是否包含拖延症相关的关键词
                self.assertTrue(
                    any(keyword in result.lower() for keyword in ["拖延", "执行", "计划", "目标", "时间"]),
                    f"查询 '{query}' 的结果应该包含与拖延症相关的建议"
                )

    def test_irrelevant_queries(self):
        """测试不相关的查询"""
        queries = [
            "今天天气怎么样？",
            "我想吃火锅",
            "你最喜欢的颜色是什么？",
            "现在几点了？"
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = search_knowledge_base(query)
                self.assertIsInstance(result, str)
                # 对于不相关查询，可能返回空结果或相关性较低的内容
                # 我们不做强制性检查，只要确保不会出错即可


if __name__ == '__main__':
    unittest.main()