#!/usr/bin/env python3
"""
修复短期记忆功能的测试脚本
"""

import requests
import time
import json

def test_fixed_short_term_memory():
    """测试修复后的短期记忆功能"""
    print("=" * 60)
    print("测试修复后的短期记忆功能")
    print("=" * 60)
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    print("1. 开始新会话...")
    response = session.get("http://localhost:5001/new")
    print(f"   状态码: {response.status_code}")
    
    # 发送第一条消息
    data1 = {
        'topic': '我叫小华，我最喜欢的颜色是绿色',
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
    
    # 发送第二条消息验证记忆
    data2 = {
        'topic': '还记得我刚才告诉你我的名字和最喜欢的颜色吗？',
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
    has_name = "小华" in content2
    has_color = "绿色" in content2
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"记住姓名: {'✓' if has_name else '✗'}")
    print(f"记住颜色: {'✓' if has_color else '✗'}")
    
    if has_name and has_color:
        print("\n🎉 修复后的短期记忆功能测试通过！")
        return True
    else:
        print("\n⚠️  修复后的短期记忆功能测试未通过！")
        # 提供调试信息
        print("\n调试信息:")
        print("- 确保服务器正确传递短期记忆给Agent")
        print("- 检查Agent是否正确使用chat_history参数")
        print("- 验证Flask会话中短期记忆是否正确存储和检索")
        return False

if __name__ == "__main__":
    success = test_fixed_short_term_memory()
    exit(0 if success else 1)