#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试新闻网站搜索工具的实际功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.news_website_search import search_news_websites

def test_news_website_search_tool():
    """测试新闻网站搜索工具的实际功能"""
    print("测试新闻网站搜索工具...")
    
    try:
        # 测试搜索关键词
        result = search_news_websites.invoke({"query": "artificial intelligence"})
        print("搜索结果:")
        print(result)
        print("\n" + "="*50 + "\n")
        
        # 测试另一个关键词
        result2 = search_news_websites.invoke({"query": "climate change"})
        print("气候变化相关新闻搜索结果:")
        print(result2)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_news_website_search_tool()