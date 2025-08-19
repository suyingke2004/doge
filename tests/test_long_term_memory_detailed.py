#!/usr/bin/env python3
"""
更直接的端到端测试，诊断长期记忆模块问题
"""

import sys
import os
from unittest.mock import MagicMock

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agent import DogAgent
from tools.long_term_memory import update_long_term_memory, get_user_long_term_memory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, LongTermMemory


def test_database_operations():
    """测试数据库操作是否正常"""
    print("=== 测试数据库操作 ===")
    
    # 创建内存数据库用于测试
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    try:
        # 测试更新长期记忆
        print("测试更新长期记忆...")
        success = update_long_term_memory(
            db_session=db_session,
            user_id='test_user_1',
            profile_summary='喜欢读书和散步的用户',
            emotion_trends={'焦虑': 3, '开心': 7},
            important_events={'2025-07-01': '开始使用翻书小狗'}
        )
        
        print(f'更新成功: {success}')
        
        # 测试获取长期记忆
        print('\n测试获取长期记忆...')
        memory = get_user_long_term_memory(db_session, 'test_user_1')
        print(f'获取到的记忆: {memory}')
        
        if memory and memory['profile_summary'] == '喜欢读书和散步的用户':
            print("✓ 数据库操作正常")
            return True
        else:
            print("✗ 数据库操作异常")
            return False
            
    except Exception as e:
        print(f"测试数据库操作时出错: {e}")
        return False
    finally:
        db_session.close()


def test_tool_call():
    """测试工具调用"""
    print("\n=== 测试工具调用 ===")
    
    # 创建内存数据库用于测试
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    try:
        # 创建工具实例
        from tools.long_term_memory_tool import UpdateLongTermMemoryTool
        tool = UpdateLongTermMemoryTool(db_session=db_session)
        
        # 调用工具
        print("调用工具更新长期记忆...")
        result = tool._run(
            user_id="test_user_2",
            profile_summary="测试用户",
            emotion_trends='{"焦虑": 5}',
            important_events='{"2025-08-10": "测试工具调用"}'
        )
        
        print(f"工具调用结果: {result}")
        
        # 验证是否成功更新
        memory = get_user_long_term_memory(db_session, 'test_user_2')
        print(f"数据库中的记录: {memory}")
        
        if "长期记忆更新成功" in result and memory:
            print("✓ 工具调用正常")
            return True
        else:
            print("✗ 工具调用异常")
            return False
            
    except Exception as e:
        print(f"测试工具调用时出错: {e}")
        return False
    finally:
        db_session.close()


def test_agent_with_mock():
    """测试带有mock的Agent"""
    print("\n=== 测试带有mock的Agent ===")
    
    try:
        # 创建数据库会话的mock
        mock_db_session = MagicMock()
        
        # 创建Agent实例
        agent = DogAgent(
            model_provider='deepseek',
            model_name='deepseek-chat',
            chat_history=[],
            max_iterations=5,
            db_session=mock_db_session
        )
        
        # 检查工具
        tool_names = [tool.name for tool in agent.tools]
        print(f"Agent注册的工具: {tool_names}")
        
        # 检查是否有长期记忆工具
        has_memory_tool = 'update_long_term_memory' in tool_names
        print(f"是否有长期记忆工具: {has_memory_tool}")
        
        if has_memory_tool:
            print("✓ Agent工具注册正常")
            return True
        else:
            print("✗ Agent工具注册异常")
            return False
            
    except Exception as e:
        print(f"测试Agent时出错: {e}")
        return False


if __name__ == "__main__":
    print("诊断长期记忆模块问题（详细版）")
    print("=" * 50)
    
    results = [
        test_database_operations(),
        test_tool_call(),
        test_agent_with_mock()
    ]
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 所有测试通过！")
        exit(0)
    else:
        print("⚠️  部分测试失败，需要进一步检查")
        exit(1)