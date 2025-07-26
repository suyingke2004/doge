#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Reddit API凭据的正确性
"""

import praw
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_reddit_credentials():
    """测试Reddit API凭据"""
    print("测试Reddit API凭据...")
    
    # 从环境变量获取Reddit API凭据
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "news_agent by u/yourusername")
    
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:5]}...{client_secret[-5:] if client_secret else 'None'}")
    print(f"User Agent: {user_agent}")
    
    if not client_id or not client_secret:
        print("错误：未找到Reddit API凭据")
        return
    
    try:
        # 初始化Reddit实例
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # 尝试获取Reddit的只读信息
        print("正在尝试连接到Reddit...")
        subreddit = reddit.subreddit("python")
        print(f"成功连接到r/{subreddit.display_name}")
        print(f"Subreddit描述: {subreddit.public_description}")
        
    except Exception as e:
        print(f"连接Reddit时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reddit_credentials()