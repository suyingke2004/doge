#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试邮件发送功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.content_delivery import content_delivery_tool
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_email_function():
    """测试邮件发送功能"""
    print("测试邮件发送功能...")
    
    # 检查环境变量
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL")
    
    if not sendgrid_api_key or not from_email:
        print("请在 .env 文件中配置 SENDGRID_API_KEY 和 FROM_EMAIL")
        print("当前配置:")
        print(f"  SENDGRID_API_KEY: {'已设置' if sendgrid_api_key else '未设置'}")
        print(f"  FROM_EMAIL: {from_email or '未设置'}")
        return
    
    print(f"使用配置:")
    print(f"  发件人邮箱: {from_email}")
    
    # 测试发送邮件
    print("\n正在发送测试邮件...")
    result = content_delivery_tool.send_email.invoke({
        "to_email": from_email,  # 发送给自己进行测试
        "subject": "新闻通讯代理测试邮件",
        "content": "这是一封来自新闻通讯代理的测试邮件。\n\n如果您收到此邮件，说明邮件发送功能配置正确。"
    })
    
    print("邮件发送结果:")
    print(result)

if __name__ == "__main__":
    test_email_function()