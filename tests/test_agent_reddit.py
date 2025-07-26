#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试NewsletterAgent中的Reddit工具集成
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent import NewsletterAgent

# 加载环境变量
load_dotenv()

def test_agent_with_reddit():
    """测试NewsletterAgent中的Reddit工具集成"""
    print("测试NewsletterAgent中的Reddit工具集成...")
    
    try:
        # 创建NewsletterAgent实例
        agent = NewsletterAgent(model_provider="deepseek")
        
        # 检查工具列表中是否包含Reddit搜索工具
        tool_names = [tool.name for tool in agent.tools]
        print(f"代理工具列表: {tool_names}")
        
        if "Search_Reddit" in tool_names:
            print("✓ Reddit搜索工具已成功集成到NewsletterAgent中")
        else:
            print("✗ Reddit搜索工具未找到")
            return
        
        # 测试使用代理执行Reddit搜索
        print("\n测试使用代理执行Reddit搜索...")
        response = agent.generate_newsletter("查找关于Python编程的Reddit讨论")
        print("代理响应:")
        print(response)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_with_reddit()