#!/usr/bin/env python3
"""
检查数据库中的聊天记录
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, ChatSession, ChatMessage

def check_database():
    """检查数据库中的聊天记录"""
    # 创建数据库连接
    DATABASE_URL = "sqlite:///chat_history.db"
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    try:
        # 查询所有会话
        sessions = db_session.query(ChatSession).all()
        print("=" * 50)
        print("数据库中的聊天会话:")
        print("=" * 50)
        
        if not sessions:
            print("未找到任何会话记录")
            return
            
        for session in sessions:
            print(f"会话ID: {session.id}")
            print(f"开始时间: {session.start_time}")
            print(f"标题: {session.title}")
            print("-" * 30)
            
            # 查询该会话的所有消息
            messages = db_session.query(ChatMessage).filter_by(session_id=session.id).order_by(ChatMessage.timestamp).all()
            for i, message in enumerate(messages, 1):
                print(f"消息 {i}:")
                print(f"  类型: {message.message_type}")
                print(f"  内容: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")
                print(f"  时间: {message.timestamp}")
                print()
                
    finally:
        db_session.close()

if __name__ == "__main__":
    check_database()