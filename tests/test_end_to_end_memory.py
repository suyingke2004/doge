#!/usr/bin/env python3
"""
端到端测试长期记忆功能
"""

import sys
import os
from collections import deque
from unittest.mock import MagicMock

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, LongTermMemory
from agent import DogAgent


def test_end_to_end_memory():
    """端到端测试长期记忆功能"""
    # 创建数据库连接
    DATABASE_URL = "sqlite:///chat_history.db"
    engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    # 获取特定用户的长期记忆
    user_id = "李明"
    long_term_memory = db_session.query(LongTermMemory).filter_by(user_id=user_id).first()
    
    print(f"测试用户: {user_id}")
    if long_term_memory:
        print("数据库中的长期记忆:")
        print(f"  用户画像: {long_term_memory.profile_summary}")
        print(f"  情绪趋势: {long_term_memory.emotion_trends}")
        print(f"  重要事件: {long_term_memory.important_events}")
    else:
        print("数据库中未找到该用户的长期记忆")
        db_session.close()
        return
    
    # 构建记忆上下文
    memory_context = {
        'short_term': [],  # 空的短期记忆
        'long_term': {
            'profile_summary': long_term_memory.profile_summary if long_term_memory else '',
            'emotion_trends': long_term_memory.emotion_trends if long_term_memory else {},
            'important_events': long_term_memory.important_events if long_term_memory else {}
        }
    }
    
    print("\n构建的记忆上下文:")
    print(f"  短期记忆: {memory_context['short_term']}")
    print(f"  长期记忆 - 用户画像: {memory_context['long_term']['profile_summary']}")
    print(f"  长期记忆 - 情绪趋势: {memory_context['long_term']['emotion_trends']}")
    print(f"  长期记忆 - 重要事件: {memory_context['long_term']['important_events']}")
    
    # 通过mock LLM配置来避免API密钥问题
    with MagicMock() as mock_llm:
        # 创建Agent实例
        dog_agent = DogAgent(
            model_provider='deepseek', 
            model_name='deepseek-chat',
            chat_history=[],
            max_iterations=5,
            memory_context=memory_context,
            db_session=db_session
        )
        
        # 检查系统提示中是否包含了长期记忆信息
        # 获取系统提示
        system_prompt = dog_agent.agent_executor.agent.runnable.first.mapper['input'].messages[0].prompt.template
        
        print("\n检查系统提示中是否包含长期记忆信息:")
        if "程序员" in system_prompt:
            print("✓ 系统提示中包含了用户的职业信息")
        else:
            print("✗ 系统提示中未包含用户的职业信息")
            
        if "焦虑" in system_prompt:
            print("✓ 系统提示中包含了用户的情绪信息")
        else:
            print("✗ 系统提示中未包含用户的情绪信息")
            
        if "deadline" in system_prompt:
            print("✓ 系统提示中包含了用户的重要事件信息")
        else:
            print("✗ 系统提示中未包含用户的重要事件信息")
        
        print(f"\n系统提示预览 (前500个字符):\n{system_prompt[:500]}...")
    
    db_session.close()


if __name__ == "__main__":
    test_end_to_end_memory()