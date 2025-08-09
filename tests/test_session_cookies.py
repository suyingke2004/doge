#!/usr/bin/env python3
"""
测试会话和cookies功能
"""

import requests
import time
import json


def test_session_persistence():
    """测试会话持久性"""
    print("=" * 50)
    print("测试会话和cookies功能")
    print("=" * 50)
    
    # 创建会话
    session = requests.Session()
    
    # 1. 开始新会话
    print("1. 开始新会话...")
    response = session.get("http://localhost:5001/new")
    print(f"   状态码: {response.status_code}")
    
    # 2. 检查cookies
    print("2. 检查cookies...")
    cookies = session.cookies.get_dict()
    print(f"   Cookies: {cookies}")
    
    # 3. 发送第一条消息
    data1 = {
        'topic': '测试消息：记住这个信息',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("3. 发送第一条消息...")
    response1 = session.post("http://localhost:5001/chat_stream", data=data1)
    print(f"   状态码: {response1.status_code}")
    
    # 收集响应
    content1 = ""
    for line in response1.iter_lines():
        if line:
            try:
                data = json.loads(line)
                if data.get("type") == "output":
                    content1 += data.get("content", "")
            except:
                pass
    
    print(f"   AI回复: {content1[:100]}...")
    
    # 等待
    time.sleep(2)
    
    # 4. 检查会话中的短期记忆
    print("4. 检查会话中的短期记忆...")
    cookies_after_first = session.cookies.get_dict()
    print(f"   发送消息后的Cookies: {cookies_after_first}")
    
    # 5. 发送第二条消息
    data2 = {
        'topic': '刚才我发了什么信息？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("5. 发送第二条消息验证记忆...")
    response2 = session.post("http://localhost:5001/chat_stream", data=data2)
    
    # 收集响应
    content2 = ""
    for line in response2.iter_lines():
        if line:
            try:
                data = json.loads(line)
                if data.get("type") == "output":
                    content2 += data.get("content", "")
            except:
                pass
    
    print(f"   状态码: {response2.status_code}")
    print(f"   AI回复: {content2[:200]}...")
    
    # 验证是否包含关键信息
    has_info = "记住" in content2 and "信息" in content2
    
    print("\n" + "=" * 50)
    print("测试结果")
    print("=" * 50)
    print(f"记住信息: {'✓' if has_info else '✗'}")
    
    if has_info:
        print("\n🎉 会话和cookies功能测试通过！")
        return True
    else:
        print("\n⚠️  会话和cookies功能测试未通过！")
        return False


if __name__ == "__main__":
    success = test_session_persistence()
    exit(0 if success else 1)