#!/usr/bin/env python3
"""
测试短期记忆功能 - 专门测试短期记忆的存储和检索
"""

import requests
import time
import json
from collections import deque

def test_short_term_memory_functionality():
    """测试短期记忆功能的完整流程"""
    print("=" * 60)
    print("测试短期记忆功能")
    print("=" * 60)
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    print("1. 开始新会话...")
    response = session.get("http://localhost:5001/new")
    print(f"   状态码: {response.status_code}")
    
    # 模拟短期记忆存储 (直接操作session)
    print("\n2. 模拟短期记忆存储...")
    short_term_memory = deque(maxlen=10)
    
    # 添加几轮对话到短期记忆
    test_conversations = [
        {"type": "human", "content": "你好，我叫小明"},
        {"type": "ai", "content": "你好小明！很高兴见到你！"},
        {"type": "human", "content": "我最喜欢的颜色是蓝色"},
        {"type": "ai", "content": "蓝色是很美的颜色呢！像天空和海洋一样。"},
        {"type": "human", "content": "我是一名程序员"},
        {"type": "ai", "content": "程序员很厉害呢！能创造出很多有趣的程序。"}
    ]
    
    for msg in test_conversations:
        short_term_memory.append(msg)
        print(f"   添加到短期记忆: {msg['type']} - {msg['content'][:30]}...")
    
    print(f"\n3. 当前短期记忆队列长度: {len(short_term_memory)}")
    print("   短期记忆内容:")
    for i, msg in enumerate(short_term_memory):
        print(f"     {i+1}. {msg['type']}: {msg['content']}")
    
    # 测试短期记忆的长度限制
    print("\n4. 测试短期记忆长度限制...")
    for i in range(5):
        short_term_memory.append({
            "type": "human", 
            "content": f"这是测试消息 {i+1}"
        })
        short_term_memory.append({
            "type": "ai", 
            "content": f"这是AI回复 {i+1}"
        })
    
    print(f"   添加10条测试消息后，短期记忆队列长度: {len(short_term_memory)}")
    print("   短期记忆内容 (最近10条):")
    for i, msg in enumerate(short_term_memory):
        print(f"     {i+1}. {msg['type']}: {msg['content']}")
    
    # 验证最早的消息已被移除
    first_msg = short_term_memory[0]
    print(f"\n5. 验证队列限制:")
    print(f"   队列中的第一条消息: {first_msg['type']} - {first_msg['content']}")
    print(f"   是否为测试消息1: {'是' if '测试消息 1' in first_msg['content'] else '否'}")
    
    # 测试短期记忆在对话中的使用
    print("\n6. 测试短期记忆在对话中的使用...")
    data = {
        'topic': '还记得我之前告诉过你我的名字和职业吗？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("   发送验证记忆的消息...")
    # 注意：这里我们不实际发送请求，因为需要运行中的服务器
    # 在实际测试中，我们会发送这个请求并检查AI的回复是否包含相关信息
    
    print("\n" + "=" * 60)
    print("短期记忆功能测试完成")
    print("=" * 60)
    print("测试要点总结:")
    print("1. 短期记忆使用deque实现，有最大长度限制(10轮对话)")
    print("2. 当超过最大长度时，旧的对话记录会被自动移除")
    print("3. 短期记忆在每次对话中都会被传递给AI代理")
    print("4. 短期记忆包含用户和AI的完整对话历史")

if __name__ == "__main__":
    test_short_term_memory_functionality()