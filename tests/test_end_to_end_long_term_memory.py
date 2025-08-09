#!/usr/bin/env python3
"""
端到端测试长期记忆功能
"""

import requests
import json
import time
import sqlite3


def test_end_to_end_long_term_memory():
    """端到端测试长期记忆功能"""
    base_url = "http://localhost:5001"
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    response = session.get(f"{base_url}/new")
    print(f"开始新会话: {response.status_code}")
    
    # 发送一个明确要求更新长期记忆的对话
    print("\n=== 发送对话 ===")
    response = session.post(f"{base_url}/chat_stream", data={
        'topic': '我是一个程序员，最近因为项目 deadline 而感到焦虑，这已经持续了一周。我希望你能记住我的职业和这个问题。',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }, stream=True)
    
    print("用户输入: 我是一个程序员，最近因为项目 deadline 而感到焦虑，这已经持续了一周。我希望你能记住我的职业和这个问题。")
    print("AI响应:")
    if response.status_code == 200:
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
    
    # 等待几秒钟确保数据库操作完成
    time.sleep(5)
    
    # 检查数据库中的长期记忆记录
    print("\n=== 检查数据库 ===")
    try:
        # 连接到数据库
        conn = sqlite3.connect('/home/suyingke/programs/LLM_create/doge/chat_history.db')
        cursor = conn.cursor()
        
        # 查询长期记忆表
        cursor.execute('SELECT * FROM long_term_memory')
        rows = cursor.fetchall()
        
        print("长期记忆表内容:")
        if rows:
            for row in rows:
                print(f"ID: {row[0]}, User ID: {row[1]}")
                print(f"用户画像: {row[2]}")
                print(f"情绪趋势: {row[3]}")
                print(f"重要事件: {row[4]}")
                print("-" * 40)
        else:
            print("长期记忆表为空")
            
        conn.close()
    except Exception as e:
        print(f"检查数据库时出错: {e}")


if __name__ == "__main__":
    test_end_to_end_long_term_memory()