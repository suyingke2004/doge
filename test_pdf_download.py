#!/usr/bin/env python3
"""
测试PDF下载功能的脚本
"""

import os
import sys
from tools.content_delivery import content_delivery_tool

def test_pdf_export():
    """测试PDF导出功能"""
    # 测试内容
    content = """# 测试PDF导出功能
    
这是一个测试文档，用于验证PDF导出功能是否正常工作。

## 子标题

- 列表项1
- 列表项2
- 列表项3

> 这是一个引用块

**粗体文本** 和 *斜体文本*
"""
    
    # 调用导出PDF工具
    result = content_delivery_tool.export_pdf.invoke({
        "content": content,
        "filename": "test_document.pdf"
    })
    
    print("PDF导出结果:")
    print(result)
    
    # 检查结果是否包含下载链接
    if "下载链接" in result:
        print("✓ PDF导出成功，返回了下载链接")
        return True
    else:
        print("✗ PDF导出失败，未返回下载链接")
        return False

if __name__ == "__main__":
    test_pdf_export()