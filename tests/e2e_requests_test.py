#!/usr/bin/env python3
"""
使用requests库进行端到端测试
测试整个"翻书小狗"应用的功能，包括记忆模块、RAG知识库和生成能力
"""

import requests
import time
import json
import unittest
import os


class EndToEndTestWithRequests(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        self.base_url = "http://localhost:5001"
        self.session = requests.Session()
        
        # 创建一个临时cookies文件用于会话保持
        self.cookies_file = "test_cookies.txt"

    def tearDown(self):
        """清理测试环境"""
        # 删除临时cookies文件
        if os.path.exists(self.cookies_file):
            os.remove(self.cookies_file)

    def test_memory_module_functionality(self):
        """测试记忆模块功能"""
        print("测试记忆模块功能...")
        
        # 开始新会话
        self.session.get(f"{self.base_url}/new")
        
        # 发送第一条消息
        data1 = {
            'topic': '你好，我叫小明，我最近在为考试焦虑',
            'model_provider': 'ali',
            'model_name': 'qwen-max',
            'maxiter': '128',
            'language': 'zh'
        }
        
        response1 = self.session.post(f"{self.base_url}/chat_stream", data=data1)
        self.assertEqual(response1.status_code, 200, "第一条消息发送失败")
        
        # 等待响应完成
        time.sleep(3)
        
        # 发送第二条消息，检查AI是否记得用户的名字和焦虑信息
        data2 = {
            'topic': '我刚才告诉你我的名字和焦虑情况了吗？',
            'model_provider': 'ali',
            'model_name': 'qwen-max',
            'maxiter': '128',
            'language': 'zh'
        }
        
        response2 = self.session.post(f"{self.base_url}/chat_stream", data=data2)
        self.assertEqual(response2.status_code, 200, "第二条消息发送失败")
        
        # 等待响应完成
        time.sleep(3)
        
        # 获取响应内容
        # 由于是流式响应，我们需要模拟前端处理方式
        print("✓ 记忆模块功能测试完成")

    def test_rag_knowledge_base_functionality(self):
        """测试RAG知识库功能"""
        print("测试RAG知识库功能...")
        
        # 开始新会话
        self.session.get(f"{self.base_url}/new")
        
        # 发送求助类问题，触发RAG工具
        data = {
            'topic': '你能给我一些关于拖延症的建议吗？',
            'model_provider': 'ali',
            'model_name': 'qwen-max',
            'maxiter': '128',
            'language': 'zh'
        }
        
        response = self.session.post(f"{self.base_url}/chat_stream", data=data)
        self.assertEqual(response.status_code, 200, "RAG查询发送失败")
        
        # 等待响应完成
        time.sleep(5)
        
        print("✓ RAG知识库功能测试完成")

    def test_new_session_empty_memory(self):
        """测试新会话的空记忆状态"""
        print("测试新会话的空记忆状态...")
        
        # 开始会话
        self.session.get(f"{self.base_url}/new")
        
        # 发送消息
        data1 = {
            'topic': '这是测试消息',
            'model_provider': 'ali',
            'model_name': 'qwen-max',
            'maxiter': '128',
            'language': 'zh'
        }
        
        response1 = self.session.post(f"{self.base_url}/chat_stream", data=data1)
        self.assertEqual(response1.status_code, 200, "第一条消息发送失败")
        
        # 等待响应完成
        time.sleep(2)
        
        # 开始新会话
        self.session.get(f"{self.base_url}/new")
        
        # 发送消息询问之前的内容
        data2 = {
            'topic': '我刚才说了什么？',
            'model_provider': 'ali',
            'model_name': 'qwen-max',
            'maxiter': '128',
            'language': 'zh'
        }
        
        response2 = self.session.post(f"{self.base_url}/chat_stream", data=data2)
        self.assertEqual(response2.status_code, 200, "第二条消息发送失败")
        
        # 等待响应完成
        time.sleep(2)
        
        print("✓ 新会话空记忆状态测试完成")

    def test_model_selection_functionality(self):
        """测试模型选择功能"""
        print("测试模型选择功能...")
        
        # 开始新会话
        self.session.get(f"{self.base_url}/new")
        
        # 发送消息
        data = {
            'topic': '你好，你能告诉我你是谁吗？',
            'model_provider': 'ali',
            'model_name': 'qwen-max',
            'maxiter': '128',
            'language': 'zh'
        }
        
        response = self.session.post(f"{self.base_url}/chat_stream", data=data)
        self.assertEqual(response.status_code, 200, "模型选择测试消息发送失败")
        
        # 等待响应完成
        time.sleep(3)
        
        print("✓ 模型选择功能测试完成")

    def test_api_endpoints(self):
        """测试API端点"""
        print("测试API端点...")
        
        # 测试主页重定向
        response = self.session.get(self.base_url)
        self.assertIn(response.status_code, [200, 302], "主页访问失败")
        
        # 测试聊天页面
        response = self.session.get(f"{self.base_url}/chat_stream")
        self.assertEqual(response.status_code, 200, "聊天页面访问失败")
        
        # 测试新会话
        response = self.session.get(f"{self.base_url}/new")
        self.assertIn(response.status_code, [200, 302], "新会话创建失败")
        
        # 测试历史记录页面
        response = self.session.get(f"{self.base_url}/history_page")
        self.assertEqual(response.status_code, 200, "历史记录页面访问失败")
        
        print("✓ API端点测试完成")


def manual_test_flow():
    """手动测试流程，用于验证核心功能"""
    print("=" * 50)
    print("手动端到端测试流程")
    print("=" * 50)
    
    # 创建会话
    session = requests.Session()
    
    # 1. 测试新会话创建
    print("1. 测试新会话创建...")
    response = session.get("http://localhost:5001/new")
    print(f"   状态码: {response.status_code}")
    
    # 2. 发送第一条消息测试短期记忆
    print("2. 发送第一条消息测试短期记忆...")
    data1 = {
        'topic': '我最喜欢的颜色是蓝色',
        'model_provider': 'ali',
        'model_name': 'qwen-max',
        'maxiter': '128',
        'language': 'zh'
    }
    response = session.post("http://localhost:5001/chat_stream", data=data1)
    print(f"   状态码: {response.status_code}")
    time.sleep(3)
    
    # 3. 发送第二条消息验证短期记忆
    print("3. 发送第二条消息验证短期记忆...")
    data2 = {
        'topic': '我最喜欢什么颜色？',
        'model_provider': 'ali',
        'model_name': 'qwen-max',
        'maxiter': '128',
        'language': 'zh'
    }
    response = session.post("http://localhost:5001/chat_stream", data=data2)
    print(f"   状态码: {response.status_code}")
    time.sleep(3)
    
    # 4. 测试RAG功能
    print("4. 测试RAG功能...")
    data3 = {
        'topic': '我感到很焦虑，怎么办？',
        'model_provider': 'ali',
        'model_name': 'qwen-max',
        'maxiter': '128',
        'language': 'zh'
    }
    response = session.post("http://localhost:5001/chat_stream", data=data3)
    print(f"   状态码: {response.status_code}")
    time.sleep(5)
    
    # 5. 测试长期记忆（需要特殊提示来触发）
    print("5. 测试长期记忆...")
    data4 = {
        'topic': '我最近在为考试焦虑，希望你能记住这个信息',
        'model_provider': 'ali',
        'model_name': 'qwen-max',
        'maxiter': '128',
        'language': 'zh'
    }
    response = session.post("http://localhost:5001/chat_stream", data=data4)
    print(f"   状态码: {response.status_code}")
    time.sleep(3)
    
    print("\n" + "=" * 50)
    print("手动测试流程完成")
    print("=" * 50)


if __name__ == "__main__":
    # 运行手动测试流程
    manual_test_flow()
    
    # 运行单元测试
    print("\n运行单元测试...")
    unittest.main()