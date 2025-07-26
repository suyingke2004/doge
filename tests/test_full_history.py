#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试完整的聊天历史记录功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models import Base, ChatHistory

def test_full_history():
    """测试完整的聊天历史记录功能"""
    print("测试完整的聊天历史记录功能...")
    
    try:
        # 数据库设置
        DATABASE_URL = "sqlite:///chat_history.db"
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        
        # 创建数据库会话
        db_session = SessionLocal()
        
        # 查询所有记录
        print("查询所有历史记录...")
        history = db_session.query(ChatHistory).order_by(desc(ChatHistory.timestamp)).all()
        
        print(f"找到 {len(history)} 条记录:")
        for i, record in enumerate(history):
            print(f"{i+1}. 用户输入: {record.user_input[:50]}{'...' if len(record.user_input) > 50 else ''}")
            print(f"   AI回答: {record.agent_response[:100]}{'...' if len(record.agent_response) > 100 else ''}")
            print(f"   会话ID: {record.session_id}")
            print(f"   时间戳: {record.timestamp}")
            print("---")
        
        db_session.close()
        
        print("完整历史记录功能测试完成!")
        
    except Exception as e:
        print(f"测试完整历史记录功能时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_history()