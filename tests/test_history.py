#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试历史记录功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models import Base, ChatHistory

def test_history():
    """测试历史记录功能"""
    print("测试历史记录功能...")
    
    try:
        # 数据库设置
        DATABASE_URL = "sqlite:///chat_history.db"
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        
        # 创建数据库会话
        db_session = SessionLocal()
        
        # 添加测试记录
        print("添加测试记录...")
        test_record = ChatHistory(
            session_id="test_session_1",
            user_input="测试问题",
            agent_response="测试回答"
        )
        db_session.add(test_record)
        db_session.commit()
        
        # 查询记录
        print("查询历史记录...")
        history = db_session.query(ChatHistory).order_by(desc(ChatHistory.timestamp)).limit(10).all()
        
        print(f"找到 {len(history)} 条记录:")
        for record in history:
            print(f"  用户输入: {record.user_input}")
            print(f"  AI回答: {record.agent_response}")
            print(f"  时间戳: {record.timestamp}")
            print("---")
        
        # 清理测试记录
        print("清理测试记录...")
        db_session.delete(test_record)
        db_session.commit()
        
        db_session.close()
        
        print("历史记录功能测试完成!")
        
    except Exception as e:
        print(f"测试历史记录功能时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_history()