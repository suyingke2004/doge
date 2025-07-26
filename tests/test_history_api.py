#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试历史记录API端点
"""

import sys
import os
import requests

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_history_api():
    """测试历史记录API端点"""
    print("测试历史记录API端点...")
    
    try:
        # 发送请求到历史记录API端点
        response = requests.get("http://localhost:5001/history")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API返回了 {len(data)} 条记录")
            
            if len(data) > 0:
                print("最新记录:")
                for i, record in enumerate(data[:3]):  # 只显示前3条
                    print(f"{i+1}. 用户输入: {record['user_input'][:50]}{'...' if len(record['user_input']) > 50 else ''}")
                    print(f"   AI回答: {record['agent_response'][:100]}{'...' if len(record['agent_response']) > 100 else ''}")
                    print(f"   时间戳: {record['timestamp']}")
                    print("---")
            else:
                print("没有找到历史记录")
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"测试历史记录API时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_history_api()