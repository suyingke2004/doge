#!/usr/bin/env python3
"""
模拟app.py中的记忆上下文获取过程
"""

import sys
import os
from collections import deque

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, LongTermMemory


def simulate_get_memory_context(user_id, db_session, flask_session):
    """
    模拟获取用户的短期和长期记忆上下文
    :param user_id: 用户ID
    :param db_session: 数据库会话
    :param flask_session: Flask session对象
    :return: 包含短期和长期记忆的上下文字典
    """
    # 获取短期记忆（最近10轮对话）
    short_term_memory = flask_session.get('short_term_memory', deque(maxlen=10))
    
    # 获取长期记忆
    long_term_memory = db_session.query(LongTermMemory).filter_by(user_id=user_id).first()
    
    # 打印调试信息
    print(f"获取记忆上下文 - User ID: {user_id}")
    if long_term_memory:
        print(f"长期记忆 - 用户画像: {long_term_memory.profile_summary}")
        print(f"长期记忆 - 情绪趋势: {long_term_memory.emotion_trends}")
        print(f"长期记忆 - 重要事件: {long_term_memory.important_events}")
    else:
        print("未找到长期记忆记录")
    
    return {
        'short_term': list(short_term_memory),
        'long_term': {
            'profile_summary': long_term_memory.profile_summary if long_term_memory else '',
            'emotion_trends': long_term_memory.emotion_trends if long_term_memory else {},
            'important_events': long_term_memory.important_events if long_term_memory else {}
        }
    }


def test_memory_context():
    """测试记忆上下文获取"""
    # 创建数据库连接
    DATABASE_URL = "sqlite:///chat_history.db"
    engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    # 模拟Flask session
    flask_session = {
        'short_term_memory': deque(maxlen=10)
    }
    
    # 测试获取特定用户的记忆上下文
    user_id = "李明"  # 使用我们之前测试的用户ID
    memory_context = simulate_get_memory_context(user_id, db_session, flask_session)
    
    print("\n返回的记忆上下文:")
    print(f"短期记忆: {memory_context['short_term']}")
    print(f"长期记忆 - 用户画像: {memory_context['long_term']['profile_summary']}")
    print(f"长期记忆 - 情绪趋势: {memory_context['long_term']['emotion_trends']}")
    print(f"长期记忆 - 重要事件: {memory_context['long_term']['important_events']}")
    
    db_session.close()


if __name__ == "__main__":
    test_memory_context()