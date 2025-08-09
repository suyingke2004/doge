#!/usr/bin/env python3
"""
测试RAG工具的集成
"""

import unittest
import sys
import os
import re
from unittest.mock import patch, MagicMock

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from agent import DogAgent
from tools.knowledge_base_search import search_knowledge_base


class TestRAGIntegration(unittest.TestCase):
    """测试RAG工具集成"""

    def test_knowledge_base_search_tool(self):
        """测试知识库搜索工具"""
        # 测试相关查询
        result = search_knowledge_base("我感到很焦虑，怎么办？")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        # 检查返回结果是否包含与焦虑相关的内容
        self.assertTrue(
            any(keyword in result.lower() for keyword in ["焦虑", "情绪", "调节", "放松"]),
            "搜索结果应该包含与焦虑相关的内容"
        )
        
        # 测试不相关查询
        result = search_knowledge_base("今天晚上吃什么？")
        self.assertIsInstance(result, str)
        # 对于不相关查询，可能返回空结果或相关性较低的内容

    def test_agent_initialization(self):
        """测试Agent初始化"""
        # 通过mock LLM配置来避免API密钥问题
        with patch.object(DogAgent, '_configure_llm') as mock_configure_llm:
            # 创建一个mock的LLM对象
            mock_llm = MagicMock()
            mock_configure_llm.side_effect = lambda: setattr(DogAgent, 'llm', mock_llm)
            
            # 创建Agent实例
            dog_agent = DogAgent(
                model_provider='ali', 
                model_name='qwen-max',
                chat_history=[],
                max_iterations=5
            )
            
            # 验证工具是否正确添加
            tool_names = [tool.name for tool in dog_agent.tools]
            self.assertIn('Knowledge_Base_Search', tool_names)
            self.assertIn('Emotion_Recognition', tool_names)  # 修正工具名称

    def test_rag_tool_triggering_logic(self):
        """测试RAG工具触发逻辑（通过检查系统提示中的规则描述）"""
        # 直接从agent.py文件中读取系统提示内容进行验证
        with open(os.path.join(os.path.dirname(__file__), '..', 'agent.py'), 'r', encoding='utf-8') as f:
            agent_code = f.read()
        
        # 检查系统提示中是否包含触发RAG工具的规则描述
        self.assertIn("当用户明确表达求助意图或需要心理学专业知识时", agent_code)
        self.assertIn("进入“翻书模式”，调用search_knowledge_base工具", agent_code)
        self.assertIn("使用知识库返回的内容时，请用\"小狗翻书\"的口吻来解释这些知识", agent_code)


if __name__ == '__main__':
    unittest.main()