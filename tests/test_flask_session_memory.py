#!/usr/bin/env python3
"""
测试Flask session中的短期记忆功能
"""

import requests
import time
import json


def test_flask_session_memory():
    """测试Flask session中的短期记忆功能"""
    print("=" * 50)
    print("测试Flask session中的短期记忆功能")
    print("=" * 50)
    
    # 创建会话
    session = requests.Session()
    
    # 1. 开始新会话
    print("1. 开始新会话...")
    response = session.get("http://localhost:5001/new")
    print(f"   状态码: {response.status_code}")
    
    # 2. 发送第一条消息
    data1 = {
        'topic': '我叫小明，我最喜欢的颜色是蓝色',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("2. 发送包含姓名和颜色的消息...")
    response1 = session.post("http://localhost:5001/chat_stream", data=data1)
    print(f"   状态码: {response1.status_code}")
    
    # 收集第一条响应内容
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
    
    # 等待一段时间确保处理完成
    time.sleep(3)
    
    # 3. 检查cookies中是否有session信息
    print("3. 检查cookies中的session信息...")
    cookies = session.cookies.get_dict()
    print(f"   Cookies数量: {len(cookies)}")
    for name, value in cookies.items():
        print(f"   {name}: {value[:50]}..." if len(value) > 50 else f"   {name}: {value}")
    
    # 4. 发送第二条消息验证记忆
    data2 = {
        'topic': '我刚才告诉你我的名字和最喜欢的颜色了吗？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("4. 发送验证记忆的消息...")
    response2 = session.post("http://localhost:5001/chat_stream", data=data2)
    
    # 收集第二条响应内容
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
    has_name = "小明" in content2
    has_color = "蓝色" in content2
    
    print("\n" + "=" * 50)
    print("测试结果")
    print("=" * 50)
    print(f"记住姓名: {'✓' if has_name else '✗'}")
    print(f"记住颜色: {'✓' if has_color else '✗'}")
    
    if has_name and has_color:
        print("\n🎉 Flask session短期记忆功能测试通过！")
        return True
    else:
        print("\n⚠️  Flask session短期记忆功能测试未通过！")
        return False


if __name__ == "__main__":
    success = test_flask_session_memory()
    exit(0 if success else 1)