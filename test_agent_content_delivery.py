#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试NewsletterAgent中的内容交付工具集成
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent import NewsletterAgent

# 加载环境变量
load_dotenv()

def test_agent_with_content_delivery():
    """测试NewsletterAgent中的内容交付工具集成"""
    print("测试NewsletterAgent中的内容交付工具集成...")
    
    try:
        # 创建NewsletterAgent实例
        agent = NewsletterAgent(model_provider="deepseek")
        
        # 检查工具列表中是否包含内容交付工具
        tool_names = [tool.name for tool in agent.tools]
        print(f"代理工具列表: {tool_names}")
        
        required_tools = ["Send_Email", "Export_PDF"]
        missing_tools = [tool for tool in required_tools if tool not in tool_names]
        
        if not missing_tools:
            print("✓ 内容交付工具已成功集成到NewsletterAgent中")
        else:
            print(f"✗ 以下内容交付工具未找到: {missing_tools}")
            return
        
        # 测试使用代理执行内容导出
        print("\n测试使用代理执行PDF导出...")
        response = agent.generate_newsletter("请将以下内容导出为PDF文件: # AI新闻\n\n这是关于AI的最新新闻。")
        print("代理响应:")
        print(response)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_with_content_delivery()