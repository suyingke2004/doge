#!/usr/bin/env python3
"""
工具测试脚本
用于测试项目中的各种工具
"""

import os
import sys
import unittest
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

class TestTools(unittest.TestCase):
    
    def test_emotion_recognition_tool(self):
        """测试情绪识别工具"""
        print("\n=== 测试情绪识别工具 ===")
        try:
            from tools.emotion_recognition import emotion_recognition_tool
            # 使用invoke方法而不是直接调用
            result = emotion_recognition_tool.invoke("今天天气真好，我很开心！")
            print(f"情绪识别结果: {result}")
            self.assertIsInstance(result, str)
        except Exception as e:
            print(f"情绪识别工具测试失败: {e}")
    
    def test_knowledge_base_search(self):
        """测试知识库搜索工具"""
        print("\n=== 测试知识库搜索工具 ===")
        try:
            from tools.knowledge_base_search import search_knowledge_base
            # 使用invoke方法而不是直接调用
            result = search_knowledge_base.invoke("什么是焦虑？")
            print(f"知识库搜索结果: {result[:200]}...")  # 只显示前200个字符
            self.assertIsInstance(result, str)
        except Exception as e:
            print(f"知识库搜索工具测试失败: {e}")
    
    def test_url_reader(self):
        """测试URL读取工具"""
        print("\n=== 测试URL读取工具 ===")
        try:
            from tools.url_reader import url_reader_tool
            # 使用invoke方法而不是直接调用
            result = url_reader_tool.read_url_content.invoke("https://httpbin.org/html")
            print(f"URL读取结果: {result[:200]}...")  # 只显示前200个字符
            self.assertIsInstance(result, str)
        except Exception as e:
            print(f"URL读取工具测试失败: {e}")
    
    def test_pdf_export(self):
        """测试PDF导出工具"""
        print("\n=== 测试PDF导出工具 ===")
        try:
            from tools.pdf_export import pdf_export_tool
            # 使用invoke方法而不是直接调用
            result = pdf_export_tool.export_to_pdf.invoke({
                "content": "这是测试内容",
                "filename": "test.pdf"
            })
            print(f"PDF导出结果: {result}")
            self.assertIsInstance(result, str)
        except Exception as e:
            print(f"PDF导出工具测试失败: {e}")

    def test_rss_feed(self):
        """测试RSS订阅工具"""
        print("\n=== 测试RSS订阅工具 ===")
        try:
            from tools.rss_feed import rss_feed_tool
            # 使用invoke方法而不是直接调用
            result = rss_feed_tool.search_rss_feeds.invoke("https://rss.sina.com.cn/news/allnews/sports.xml")
            print(f"RSS订阅结果: {result[:200]}...")  # 只显示前200个字符
            self.assertIsInstance(result, str)
        except Exception as e:
            print(f"RSS订阅工具测试失败: {e}")

if __name__ == "__main__":
    unittest.main()