#!/usr/bin/env python3
"""
测试长期记忆读取功能
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, LongTermMemory


def test_long_term_memory_retrieval():
    """测试长期记忆读取功能"""
    # 创建数据库连接
    DATABASE_URL = "sqlite:///chat_history.db"
    engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    # 测试获取特定用户的长期记忆
    user_id = "李明"  # 使用我们之前测试的用户ID
    long_term_memory = db_session.query(LongTermMemory).filter_by(user_id=user_id).first()
    
    print(f"查询用户ID: {user_id}")
    if long_term_memory:
        print("找到长期记忆记录:")
        print(f"  用户画像: {long_term_memory.profile_summary}")
        print(f"  情绪趋势: {long_term_memory.emotion_trends}")
        print(f"  重要事件: {long_term_memory.important_events}")
    else:
        print("未找到长期记忆记录")
    
    db_session.close()


if __name__ == "__main__":
    test_long_term_memory_retrieval()