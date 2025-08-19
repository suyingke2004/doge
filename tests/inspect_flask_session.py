#!/usr/bin/env python3
"""
检查Flask会话内容的测试脚本
"""

import requests
import time
import json

def inspect_flask_session():
    """检查Flask会话内容"""
    print("=" * 60)
    print("检查Flask会话内容")
    print("=" * 60)
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    print("1. 开始新会话...")
    response = session.get("http://localhost:5001/new")
    print(f"   状态码: {response.status_code}")
    
    # 发送第一条消息
    data1 = {
        'topic': '我叫小李，我最喜欢的颜色是紫色',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("\n2. 发送包含姓名和颜色的消息...")
    response1 = session.post("http://localhost:5001/chat_stream", data=data1)
    
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
    
    print(f"   状态码: {response1.status_code}")
    print(f"   AI回复: {content1[:200]}...")
    
    # 等待一段时间确保处理完成
    time.sleep(3)
    
    # 尝试获取会话信息（需要服务器端支持）
    print("\n3. 检查会话状态...")
    # 这里可以添加一个特殊的调试端点来检查会话内容
    # 但由于当前实现中没有这样的端点，我们只能通过观察AI的行为来推断
    
    print("\n请查看服务器端的调试输出以获取更多信息。")

if __name__ == "__main__":
    inspect_flask_session()