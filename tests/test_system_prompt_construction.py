#!/usr/bin/env python3
"""
测试Agent中系统提示的构建
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


def test_system_prompt_construction():
    """测试系统提示的构建"""
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
    
    # 模拟Agent中的系统提示构建逻辑
    memory_info = ""
    if memory_context:
        short_term = memory_context.get('short_term', [])
        long_term = memory_context.get('long_term', {})
        
        # 格式化短期记忆
        if short_term:
            memory_info += "\n最近的对话历史：\n"
            for msg in short_term:
                role = "用户" if msg['type'] == 'human' else "小狗"
                memory_info += f"{role}: {msg['content']}\n"
        
        # 格式化长期记忆
        if long_term:
            memory_info += "\n关于用户的信息：\n"
            if long_term.get('profile_summary'):
                memory_info += f"用户画像: {long_term['profile_summary']}\n"
            if long_term.get('emotion_trends'):
                memory_info += f"情绪趋势: {long_term['emotion_trends']}\n"
            if long_term.get('important_events'):
                memory_info += f"重要事件: {long_term['important_events']}\n"
    
    print("\n构建的记忆信息:")
    print(repr(memory_info))
    
    # 检查是否包含了长期记忆信息
    print("\n检查构建的记忆信息是否包含长期记忆内容:")
    if "程序员" in memory_info:
        print("✓ 包含了用户的职业信息")
    else:
        print("✗ 未包含用户的职业信息")
        
    if "焦虑" in memory_info:
        print("✓ 包含了用户的情绪信息")
    else:
        print("✗ 未包含用户的情绪信息")
        
    if "deadline" in memory_info:
        print("✓ 包含了用户的重要事件信息")
    else:
        print("✗ 未包含用户的重要事件信息")
    
    db_session.close()


if __name__ == "__main__":
    test_system_prompt_construction()