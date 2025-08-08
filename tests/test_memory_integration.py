#!/usr/bin/env python3
"""
通过HTTP请求测试记忆模块功能
"""

import requests
import time
import unittest
import json


class TestMemoryModuleIntegration(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        self.base_url = "http://localhost:5001"
        self.session = requests.Session()

    def test_short_term_memory_in_conversation(self):
        """测试短期记忆在对话中的作用"""
        # 开始新会话
        self.session.get(f"{self.base_url}/new")
        
        # 发送第一条消息
        response = self.session.post(f"{self.base_url}/chat_stream", data={
            'topic': '我最喜欢的动物是小狗',
            'model_provider': 'deepseek',
            'model_name': 'deepseek-chat',
            'maxiter': '128',
            'language': 'zh'
        })
        
        # 等待响应
        time.sleep(2)
        
        # 发送第二条消息，提及第一条消息中的内容
        response = self.session.post(f"{self.base_url}/chat_stream", data={
            'topic': '我刚才说了我最喜欢什么动物吗？',
            'model_provider': 'deepseek',
            'model_name': 'deepseek-chat',
            'maxiter': '128',
            'language': 'zh'
        })
        
        # 收集响应内容
        content = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if data.get("type") == "output":
                        content += data.get("content", "")
                except:
                    pass
        
        # 转换为小写进行检查
        content_lower = content.lower()
        
        # 验证AI是否提到了相关话题
        self.assertTrue("小狗" in content or "动物" in content_lower, 
                       "AI应该记得用户提到的动物话题")

    def test_new_session_empty_memory(self):
        """测试新会话的空记忆状态"""
        # 开始新会话
        self.session.get(f"{self.base_url}/new")
        
        # 发送消息
        response = self.session.post(f"{self.base_url}/chat_stream", data={
            'topic': '这是测试消息',
            'model_provider': 'deepseek',
            'model_name': 'deepseek-chat',
            'maxiter': '128',
            'language': 'zh'
        })
        
        # 等待响应
        time.sleep(2)
        
        # 开始另一个新会话
        self.session.get(f"{self.base_url}/new")
        
        # 发送消息询问之前的内容
        response = self.session.post(f"{self.base_url}/chat_stream", data={
            'topic': '我刚才说了什么？',
            'model_provider': 'deepseek',
            'model_name': 'deepseek-chat',
            'maxiter': '128',
            'language': 'zh'
        })
        
        # 收集响应内容
        content = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if data.get("type") == "output":
                        content += data.get("content", "")
                except:
                    pass
        
        # 验证AI不记得之前的内容
        self.assertNotIn("测试消息", content, "新会话中AI不应该记得之前的内容")

    def test_database_storage(self):
        """测试数据库中的消息存储"""
        import sqlite3
        import os
        
        # 检查数据库文件是否存在
        db_path = "/home/suyingke/programs/LLM_create/doge/chat_history.db"
        self.assertTrue(os.path.exists(db_path), "数据库文件应该存在")
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_message'")
        result = cursor.fetchone()
        self.assertIsNotNone(result, "chat_message表应该存在")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_session'")
        result = cursor.fetchone()
        self.assertIsNotNone(result, "chat_session表应该存在")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='long_term_memory'")
        result = cursor.fetchone()
        self.assertIsNotNone(result, "long_term_memory表应该存在")
        
        # 关闭数据库连接
        conn.close()


if __name__ == "__main__":
    unittest.main()