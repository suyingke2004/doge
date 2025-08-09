#!/usr/bin/env python3
"""
测试长期记忆更新工具的调用
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from agent import DogAgent


class TestLongTermMemoryToolInvocation(unittest.TestCase):
    """测试长期记忆工具的调用"""

    def test_agent_with_long_term_memory_tool(self):
        """测试Agent是否正确配置了长期记忆工具"""
        # 通过mock LLM配置来避免API密钥问题
        with patch.object(DogAgent, '_configure_llm') as mock_configure_llm:
            # 创建一个mock的LLM对象
            mock_llm = MagicMock()
            mock_configure_llm.side_effect = lambda: setattr(DogAgent, 'llm', mock_llm)
            
            # 创建数据库会话的mock
            mock_db_session = MagicMock()
            
            # 创建Agent实例，提供数据库会话
            dog_agent = DogAgent(
                model_provider='deepseek', 
                model_name='deepseek-chat',
                chat_history=[],
                max_iterations=5,
                db_session=mock_db_session
            )
            
            # 验证工具是否正确添加，包括长期记忆工具
            tool_names = [tool.name for tool in dog_agent.tools]
            self.assertIn('update_long_term_memory', tool_names)
            print(f"已添加的工具: {tool_names}")
            
            # 检查系统提示内容
            # 直接读取agent.py文件来验证提示内容
            with open(os.path.join(os.path.dirname(__file__), '..', 'agent.py'), 'r', encoding='utf-8') as f:
                agent_code = f.read()
            
            self.assertIn("如果了解到用户的个人信息", agent_code)
            self.assertIn("可以使用update_long_term_memory工具", agent_code)
            print("系统提示中包含长期记忆工具使用指导")


if __name__ == '__main__':
    unittest.main()