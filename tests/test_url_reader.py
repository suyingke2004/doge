#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试URL阅读工具的实际功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.url_reader import url_reader_tool

def test_url_reader_tool():
    """测试URL阅读工具的实际功能"""
    print("测试URL阅读工具...")
    
    try:
        # 测试一个简单的网页
        result = url_reader_tool.read_url_content.invoke({"url": "https://httpbin.org/html"})
        print("测试网页结果:")
        print(result)
        print("\n" + "="*50 + "\n")
        
        # 测试另一个网页
        result2 = url_reader_tool.read_url_content.invoke({"url": "https://example.com"})
        print("Example.com结果:")
        print(result2)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_url_reader_tool()