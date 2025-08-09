#!/usr/bin/env python3
"""
直接测试DogAgent的短期记忆功能
"""

import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agent import DogAgent
from langchain_core.messages import HumanMessage, AIMessage


def test_dog_agent_memory():
    """直接测试DogAgent的短期记忆功能"""
    print("=" * 50)
    print("直接测试DogAgent的短期记忆功能")
    print("=" * 50)
    
    # 创建测试历史记录
    chat_history = [
        HumanMessage(content="我叫小明，我最喜欢的颜色是蓝色"),
        AIMessage(content="（尾巴摇得像小风扇）哇！小明！蓝色真是超级棒的颜色呢！像天空和大海一样让人心情开阔～")
    ]
    
    # 创建DogAgent实例
    agent = DogAgent(
        model_provider="deepseek",
        model_name="deepseek-chat",
        chat_history=chat_history,
        max_iterations=3
    )
    
    # 测试是否记住信息
    user_input = "我刚才告诉你我的名字和最喜欢的颜色了吗？"
    print(f"用户输入: {user_input}")
    
    try:
        response = agent.chat(user_input)
        print(f"AI回复: {response}")
        
        # 检查回复中是否包含关键信息
        has_name = "小明" in response
        has_color = "蓝色" in response
        
        print("\n" + "=" * 50)
        print("测试结果")
        print("=" * 50)
        print(f"记住姓名: {'✓' if has_name else '✗'}")
        print(f"记住颜色: {'✓' if has_color else '✗'}")
        
        if has_name and has_color:
            print("\n🎉 DogAgent短期记忆功能测试通过！")
            return True
        else:
            print("\n⚠️  DogAgent短期记忆功能测试未通过！")
            return False
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        return False


if __name__ == "__main__":
    success = test_dog_agent_memory()
    exit(0 if success else 1)