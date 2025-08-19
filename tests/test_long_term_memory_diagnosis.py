#!/usr/bin/env python3
"""
诊断长期记忆模块问题的测试脚本
"""

import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agent import DogAgent
from tools.long_term_memory_tool import UpdateLongTermMemoryTool


def test_tool_registration():
    """测试工具是否正确注册"""
    print("=== 测试工具注册 ===")
    
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
        print(f"已添加的工具: {tool_names}")
        
        if 'update_long_term_memory' in tool_names:
            print("✓ 长期记忆工具已正确注册")
            return True
        else:
            print("✗ 长期记忆工具未注册")
            return False


def test_system_prompt():
    """测试系统提示词中是否包含长期记忆相关的指导"""
    print("\n=== 测试系统提示词 ===")
    
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
        
        # 检查系统提示中是否包含长期记忆相关的指导
        # 注意：在新的LangChain版本中，提示词的访问方式可能不同
        try:
            # 尝试不同的访问方式
            prompt_text = str(dog_agent.agent_executor.agent.prompt)
            if "update_long_term_memory" in prompt_text:
                print("✓ 系统提示词中包含长期记忆工具使用指导")
                return True
            else:
                print("? 无法确认系统提示词内容")
                print("提示词内容片段:", prompt_text[:500] + "..." if len(prompt_text) > 500 else prompt_text)
                return False
        except Exception as e:
            print(f"检查系统提示词时出错: {e}")
            return False


def test_tool_instance():
    """测试长期记忆工具实例"""
    print("\n=== 测试长期记忆工具实例 ===")
    
    try:
        # 创建数据库会话的mock
        mock_db_session = MagicMock()
        
        # 创建工具实例
        tool = UpdateLongTermMemoryTool(db_session=mock_db_session)
        
        print(f"工具名称: {tool.name}")
        print(f"工具描述: {tool.description[:100]}...")
        
        if tool.name == "update_long_term_memory":
            print("✓ 工具实例创建成功")
            return True
        else:
            print("✗ 工具实例创建失败")
            return False
    except Exception as e:
        print(f"创建工具实例时出错: {e}")
        return False


if __name__ == "__main__":
    print("诊断长期记忆模块问题")
    print("=" * 50)
    
    results = [
        test_tool_registration(),
        test_system_prompt(),
        test_tool_instance()
    ]
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 所有测试通过！")
        exit(0)
    else:
        print("⚠️  部分测试失败，需要进一步检查")
        exit(1)