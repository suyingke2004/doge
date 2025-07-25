#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试RSS工具的实际功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.rss_feed import rss_feed_tool

def test_rss_tool():
    """测试RSS工具的实际功能"""
    print("测试RSS工具...")
    
    try:
        # 测试实际的RSS订阅源
        result = rss_feed_tool.search_rss_feeds.invoke({"feed_url": "https://rss.cnn.com/rss/edition.rss"})
        print("CNN RSS订阅源结果:")
        print(result)
        print("\n" + "="*50 + "\n")
        
        # 测试另一个RSS订阅源
        result2 = rss_feed_tool.search_rss_feeds.invoke({"feed_url": "https://feeds.bbci.co.uk/news/rss.xml"})
        print("BBC RSS订阅源结果:")
        print(result2)
        print("\n" + "="*50 + "\n")
        
        # 测试中文RSS订阅源
        result3 = rss_feed_tool.search_rss_feeds.invoke({"feed_url": "https://feeds.feedburner.com/ruanyifeng"})
        print("阮一峰RSS订阅源结果:")
        print(result3)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rss_tool()