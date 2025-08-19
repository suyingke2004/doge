#!/usr/bin/env python3
"""验证chat_history传递的测试脚本
"""

import requests
import time
import json

def verify_chat_history_passing():
    """验证chat_history是否被正确传递"""
    print("=" * 60)
    print("验证chat_history传递")
    print("=" * 60)
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    print("1. 开始新会话...")
    response = session.get("http://localhost:5001/new")
    print(f"   状态码: {response.status_code}")
    
    # 发送第一条消息
    data1 = {
        'topic': '我的名字是小张，我喜欢编程',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("\n2. 发送包含姓名和爱好的消息...")
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
    
    # 发送第二条消息，明确要求AI重复用户的信息
    data2 = {
        'topic': '请重复一遍我刚才告诉你的关于我的信息',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("\n3. 发送验证记忆的消息...")
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
    print(f"   AI回复: {content2[:300]}...")
    
    # 验证是否包含关键信息
    has_name = "小张" in content2
    has_hobby = "编程" in content2
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"记住姓名: {'✓' if has_name else '✗'}")
    print(f"记住爱好: {'✓' if has_hobby else '✗'}")
    
    if has_name and has_hobby:
        print("\n🎉 chat_history传递测试通过！")
        return True
    else:
        print("\n⚠️  chat_history传递测试未通过！")
        # 提供调试信息
        print("\n调试信息:")
        print("- 检查服务器端是否正确传递chat_history给Agent")
        print("- 验证Agent是否正确使用chat_history参数")
        print("- 确认提示模板中chat_history占位符是否正确配置")
        return False

if __name__ == "__main__":
    success = verify_chat_history_passing()
    exit(0 if success else 1)