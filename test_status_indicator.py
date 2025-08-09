#!/usr/bin/env python3
"""
使用requests库测试工具调用状态栏功能
"""

import requests
import json
import time

def test_status_indicator():
    """测试状态指示器功能"""
    print("=" * 50)
    print("测试状态指示器功能")
    print("=" * 50)
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    print("1. 开始新会话...")
    response = session.get("http://localhost:5001/new")
    print(f"   状态码: {response.status_code}")
    
    # 发送一个可能触发工具调用的消息
    data = {
        'topic': '我感到很焦虑，怎么办？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("2. 发送可能触发工具调用的消息...")
    response = session.post("http://localhost:5001/chat_stream", data=data, stream=True)
    print(f"   状态码: {response.status_code}")
    
    # 收集响应内容，特别关注状态信息
    content = ""
    status_messages = []
    
    if response.status_code == 200:
        print("3. 读取流式响应...")
        try:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "status":
                            status_messages.append(data.get("content", ""))
                            print(f"   [状态] {data.get('content')}")
                        elif data.get("type") == "output":
                            content += data.get("content", "")
                    except json.JSONDecodeError:
                        # 处理非JSON行
                        content += line.decode('utf-8')
        except Exception as e:
            print(f"   读取响应时出错: {e}")
    
    print(f"\n4. 收集到的状态消息数量: {len(status_messages)}")
    for i, msg in enumerate(status_messages, 1):
        print(f"   状态消息 {i}: {msg}")
    
    print(f"\n5. AI回复内容预览:")
    print(f"   {content[:300]}...")
    
    return len(status_messages) > 0

def main():
    """主函数"""
    print("开始测试状态指示器功能")
    print("注意：请确保应用已在端口5001上运行")
    
    try:
        success = test_status_indicator()
        if success:
            print("\n✅ 状态指示器功能测试通过！")
        else:
            print("\n⚠️  未检测到状态消息，可能需要进一步调试。")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    main()