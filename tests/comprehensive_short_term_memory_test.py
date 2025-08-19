#!/usr/bin/env python3
"""
全面测试短期记忆功能
"""

import requests
import time
import json

def comprehensive_short_term_memory_test():
    """全面测试短期记忆功能"""
    print("=" * 60)
    print("全面测试短期记忆功能")
    print("=" * 60)
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    print("1. 开始新会话...")
    response = session.get("http://localhost:5001/new")
    print(f"   状态码: {response.status_code}")
    
    # 第一轮对话 - 提供用户信息
    data1 = {
        'topic': '你好，我叫小王，我是一名设计师，最喜欢的颜色是橙色',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("\n2. 第一轮对话 - 提供用户信息...")
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
    
    # 第二轮对话 - 验证记忆
    data2 = {
        'topic': '你还记得我的名字和职业吗？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("\n3. 第二轮对话 - 验证记忆...")
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
    
    # 第三轮对话 - 验证更详细的记忆
    data3 = {
        'topic': '我刚才说的最喜欢的颜色是什么来着？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("\n4. 第三轮对话 - 验证更详细的记忆...")
    response3 = session.post("http://localhost:5001/chat_stream", data=data3)
    
    # 收集第三条响应内容
    content3 = ""
    for line in response3.iter_lines():
        if line:
            try:
                data = json.loads(line)
                if data.get("type") == "output":
                    content3 += data.get("content", "")
            except:
                pass
    
    print(f"   状态码: {response3.status_code}")
    print(f"   AI回复: {content3[:300]}...")
    
    # 验证是否包含关键信息
    has_name = "小王" in content2 or "小王" in content3
    has_profession = "设计师" in content2 or "设计师" in content3
    has_color = "橙色" in content2 or "橙色" in content3
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"记住姓名: {'✓' if has_name else '✗'}")
    print(f"记住职业: {'✓' if has_profession else '✗'}")
    print(f"记住颜色: {'✓' if has_color else '✗'}")
    
    if has_name and has_profession and has_color:
        print("\n🎉 全面短期记忆功能测试通过！")
        return True
    else:
        print("\n⚠️  全面短期记忆功能测试未通过！")
        # 提供调试信息
        print("\n调试信息:")
        print("- 检查服务器端是否正确传递chat_history给Agent")
        print("- 验证Agent是否正确使用chat_history参数")
        print("- 确认提示模板中chat_history占位符是否正确配置")
        print("- 检查Flask会话中短期记忆是否正确存储和检索")
        return False

if __name__ == "__main__":
    success = comprehensive_short_term_memory_test()
    exit(0 if success else 1)