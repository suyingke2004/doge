#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Reddit工具的实际功能（使用更通用的关键词）
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.reddit_search import reddit_search_tool

def test_reddit_tool():
    """测试Reddit工具的实际功能"""
    print("测试Reddit工具...")
    
    try:
        # 测试实际的Reddit搜索（使用更通用的关键词）
        result = reddit_search_tool.search_reddit.invoke({"query": "Python"})
        print("搜索结果 (关键词: Python):")
        print(result)
        print("\n" + "="*50 + "\n")
        
        # 测试另一个查询
        result2 = reddit_search_tool.search_reddit.invoke({"query": "artificial intelligence"})
        print("第二次搜索结果 (关键词: artificial intelligence):")
        print(result2)
        print("\n" + "="*50 + "\n")
        
        # 测试中文关键词
        result3 = reddit_search_tool.search_reddit.invoke({"query": "机器学习"})
        print("第三次搜索结果 (关键词: 机器学习):")
        print(result3)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reddit_tool()