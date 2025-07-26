#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试内容交付工具的实际功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.content_delivery import content_delivery_tool

def test_content_delivery():
    """测试内容交付工具的实际功能"""
    print("测试内容交付工具...")
    
    try:
        # 测试PDF导出功能
        print("\n1. 测试PDF导出功能...")
        content = "# 测试新闻通讯\n\n这是测试内容，用于验证PDF导出功能是否正常工作。\n\n## 子标题\n\n- 列表项1\n- 列表项2\n- 列表项3\n\n> 这是一个引用块\n\n**粗体文本** 和 *斜体文本*"
        result = content_delivery_tool.export_pdf.invoke({"content": content, "filename": "test_newsletter.pdf"})
        print("PDF导出结果:")
        print(result)
        
        # 测试邮件发送功能（仅在配置了API密钥时）
        print("\n2. 测试邮件发送功能...")
        # 注意：这需要在.env文件中配置SENDGRID_API_KEY和FROM_EMAIL
        # 如果未配置，会返回错误信息，这是预期的行为
        result = content_delivery_tool.send_email.invoke({
            "to_email": "test@example.com",
            "subject": "测试邮件",
            "content": "这是一封测试邮件，用于验证邮件发送功能是否正常工作。"
        })
        print("邮件发送结果:")
        print(result)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_content_delivery()