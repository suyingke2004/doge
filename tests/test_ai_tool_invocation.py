#!/usr/bin/env python3
"""
测试AI是否会调用长期记忆工具
"""

import sys
import os
import json

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import requests
import time


def test_ai_tool_invocation():
    """测试AI是否会调用长期记忆工具"""
    base_url = "http://localhost:5001"
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    response = session.get(f"{base_url}/new")
    print(f"开始新会话: {response.status_code}")
    
    # 准备测试输入，明确提及姓名、职业和情绪状态
    test_input = "我叫王小明，是一名软件工程师。最近因为项目deadline临近感到很焦虑，已经持续一周了。"
    
    # 发送测试输入
    print(f"\n发送测试输入: {test_input}")
    response = session.post(f"{base_url}/chat_stream", data={
        'topic': test_input,
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }, stream=True)
    
    # 收集AI响应
    ai_response = ""
    tool_calls = []
    
    if response.status_code == 200:
        print("AI响应:")
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if data.get("type") == "output":
                        content = data.get("content", "")
                        ai_response += content
                        print(content, end="", flush=True)
                    elif data.get("type") == "status":
                        status = data.get("content", "")
                        tool_calls.append(status)
                        print(f"\n[状态] {status}")
                except json.JSONDecodeError:
                    text = line.decode('utf-8')
                    print(text, end="", flush=True)
                    # 检查是否包含工具调用信息
                    if "工具" in text or "调用" in text or "update_long_term_memory" in text:
                        tool_calls.append(text)
        print("\n")
    else:
        print(f"请求失败，状态码: {response.status_code}")
        return False
    
    # 等待数据库操作完成
    time.sleep(3)
    
    # 检查数据库中的记录
    print("\n=== 数据库检查 ===")
    try:
        # 连接到数据库
        conn = sqlite3.connect('/home/suyingke/programs/LLM_create/doge/chat_history.db')
        cursor = conn.cursor()
        
        # 查询最新的长期记忆记录（应该包含"王小明"作为user_id）
        cursor.execute('SELECT * FROM long_term_memory WHERE user_id = "王小明" ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        
        if row:
            print("找到了匹配的长期记忆记录:")
            print(f"ID: {row[0]}, User ID: {row[1]}")
            print(f"用户画像: {row[2]}")
            print(f"情绪趋势: {row[3]}")
            print(f"重要事件: {row[4]}")
            
            # 验证是否包含预期的信息
            has_name = "王小明" in (row[2] or "")
            has_job = "软件工程师" in (row[2] or "")
            has_anxiety = "焦虑" in (row[3] or "")  # 直接在字符串中检查
            
            print(f"\n验证结果:")
            print(f"包含姓名: {'✓' if has_name else '✗'}")
            print(f"包含职业: {'✓' if has_job else '✗'}")
            print(f"包含焦虑情绪: {'✓' if has_anxiety else '✗'}")
            
            conn.close()
            
            if has_name and has_job and has_anxiety:
                print("\n🎉 AI成功识别并更新了长期记忆！")
                return True
            else:
                print("\n⚠️  AI识别了信息但更新不完整")
                return False
        else:
            print("未找到匹配的长期记忆记录")
            conn.close()
            return False
            
    except Exception as e:
        print(f"检查数据库时出错: {e}")
        return False


if __name__ == "__main__":
    print("测试AI是否调用长期记忆工具")
    print("=" * 50)
    
    try:
        import sqlite3
        success = test_ai_tool_invocation()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 测试通过！")
            exit(0)
        else:
            print("⚠️  测试失败，AI未正确调用长期记忆工具")
            exit(1)
    except ImportError as e:
        print(f"导入模块失败: {e}")
        exit(1)