#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化数据库脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from sqlalchemy import create_engine
from models import Base

def init_db():
    """初始化数据库"""
    print("初始化数据库...")
    
    try:
        # 数据库设置
        DATABASE_URL = "sqlite:///chat_history.db"
        engine = create_engine(DATABASE_URL, echo=False)
        
        # 创建所有表
        Base.metadata.create_all(engine)
        
        print("数据库初始化成功!")
        
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_db()