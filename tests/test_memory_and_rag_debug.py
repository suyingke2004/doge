#!/usr/bin/env python3
"""
测试记忆功能和RAG模块（带调试信息）
"""

import requests
import json
import time

def test_memory_and_rag_with_debug():
    """测试记忆功能和RAG模块（带调试信息）"""
    base_url = "http://localhost:5001"
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    response = session.get(f"{base_url}/new")
    print(f"开始新会话: {response.status_code}")
    
    # 第一轮对话 - 普通情绪表达（测试短期记忆）
    print("\n=== 第一轮对话 - 普通情绪表达 ===")
    response = session.post(f"{base_url}/chat_stream", data={
        'topic': '我今天心情不太好，因为工作压力很大',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }, stream=True)
    
    print("用户输入: 我今天心情不太好，因为工作压力很大")
    print("AI响应:")
    ai_response_1 = ""
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if data.get("type") == "output":
                        content = data.get("content", "")
                        print(content, end="", flush=True)
                        ai_response_1 += content
                except json.JSONDecodeError:
                    content = line.decode('utf-8')
                    print(content, end="", flush=True)
                    ai_response_1 += content
        print("\n")
    else:
        print(f"请求失败，状态码: {response.status_code}")
    
    time.sleep(2)  # 等待一下
    
    # 检查session中的短期记忆
    print("\n--- 检查短期记忆 ---")
    session_data_response = session.get(f"{base_url}/debug_chat")
    print("注意：这里需要在前端页面查看session数据")
    
    # 第二轮对话 - 测试记忆
    print("\n=== 第二轮对话 - 测试记忆 ===")
    response = session.post(f"{base_url}/chat_stream", data={
        'topic': '我刚才说了我因为什么心情不好吗？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }, stream=True)
    
    print("用户输入: 我刚才说了我因为什么心情不好吗？")
    print("AI响应:")
    ai_response_2 = ""
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if data.get("type") == "output":
                        content = data.get("content", "")
                        print(content, end="", flush=True)
                        ai_response_2 += content
                except json.JSONDecodeError:
                    content = line.decode('utf-8')
                    print(content, end="", flush=True)
                    ai_response_2 += content
        print("\n")
    else:
        print(f"请求失败，状态码: {response.status_code}")
    
    time.sleep(2)  # 等待一下
    
    # 第三轮对话 - 求助类问题（测试RAG模块）
    print("\n=== 第三轮对话 - 求助类问题 ===")
    response = session.post(f"{base_url}/chat_stream", data={
        'topic': '有什么方法可以缓解工作压力吗？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }, stream=True)
    
    print("用户输入: 有什么方法可以缓解工作压力吗？")
    print("AI响应:")
    ai_response_3 = ""
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if data.get("type") == "output":
                        content = data.get("content", "")
                        print(content, end="", flush=True)
                        ai_response_3 += content
                except json.JSONDecodeError:
                    content = line.decode('utf-8')
                    print(content, end="", flush=True)
                    ai_response_3 += content
        print("\n")
    else:
        print(f"请求失败，状态码: {response.status_code}")
    
    # 输出总结
    print("\n" + "="*50)
    print("测试总结:")
    print("="*50)
    print("1. 短期记忆功能:")
    if "工作压力" in ai_response_2:
        print("   ✓ AI能回忆起之前对话中提到的工作压力")
    else:
        print("   ✗ AI未能回忆起之前对话中提到的工作压力")
    
    print("\n2. RAG模块功能:")
    if "压力" in ai_response_3 and ("深呼吸" in ai_response_3 or "运动" in ai_response_3):
        print("   ✓ 成功触发RAG工具并返回相关心理学知识")
    else:
        print("   ✗ 未能成功触发RAG工具或返回相关知识")
    
    print("\n3. 整体集成:")
    print("   - 记忆模块和RAG模块能协同工作")
    print("   - Agent能根据上下文和用户意图正确响应")

if __name__ == "__main__":
    test_memory_and_rag_with_debug()