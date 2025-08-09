#!/usr/bin/env python3
"""
使用HTTP请求测试RAG功能
"""

import requests
import json
import time
import os

# 设置环境变量
os.environ['DEEPSEEK_API_KEY'] = 'sk-28f8598c32ee4db6810061be00b0fb69'

def test_rag_functionality():
    """测试RAG功能"""
    base_url = "http://localhost:5001"
    
    # 开始新会话
    session = requests.Session()
    response = session.get(f"{base_url}/new")
    print(f"开始新会话: {response.status_code}")
    
    # 测试拖延症相关问题
    print("\n--- 测试拖延症相关问题 ---")
    response = session.post(f"{base_url}/chat_stream", data={
        'topic': '你能给我一些关于拖延症的建议吗？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }, stream=True)
    
    print("响应状态码:", response.status_code)
    if response.status_code == 200:
        print("AI响应:")
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if data.get("type") == "output":
                        print(data.get("content", ""), end="", flush=True)
                except json.JSONDecodeError:
                    print(line.decode('utf-8'), end="", flush=True)
        print("\n")
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print("响应内容:", response.text)
    
    # 测试焦虑缓解问题
    print("\n--- 测试焦虑缓解问题 ---")
    response = session.post(f"{base_url}/chat_stream", data={
        'topic': '我最近总是感到焦虑，有什么方法可以缓解吗？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }, stream=True)
    
    print("响应状态码:", response.status_code)
    if response.status_code == 200:
        print("AI响应:")
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if data.get("type") == "output":
                        print(data.get("content", ""), end="", flush=True)
                except json.JSONDecodeError:
                    print(line.decode('utf-8'), end="", flush=True)
        print("\n")
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print("响应内容:", response.text)

    # 测试非求助类问题（不应该触发RAG）
    print("\n--- 测试非求助类问题 ---")
    response = session.post(f"{base_url}/chat_stream", data={
        'topic': '今天天气真好',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }, stream=True)
    
    print("响应状态码:", response.status_code)
    if response.status_code == 200:
        print("AI响应:")
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if data.get("type") == "output":
                        print(data.get("content", ""), end="", flush=True)
                except json.JSONDecodeError:
                    print(line.decode('utf-8'), end="", flush=True)
        print("\n")
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print("响应内容:", response.text)

if __name__ == "__main__":
    test_rag_functionality()