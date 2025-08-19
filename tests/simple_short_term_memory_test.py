#!/usr/bin/env python3
"""
简化版短期记忆功能测试
"""

from agent import DogAgent
from langchain_core.messages import HumanMessage, AIMessage

def simple_short_term_memory_test():
    """简化版短期记忆功能测试"""
    print("=" * 60)
    print("简化版短期记忆功能测试")
    print("=" * 60)
    
    # 创建带有历史记录的Agent
    chat_history = [
        HumanMessage(content="你好，我叫小明，我是一名程序员"),
        AIMessage(content="你好小明！很高兴认识你，程序员是一个很有趣的职业呢！")
    ]
    
    agent = DogAgent(
        model_provider="deepseek",
        model_name="deepseek-chat",
        chat_history=chat_history,
        max_iterations=5
    )
    
    # 测试是否记住用户信息
    user_input = "还记得我的名字和职业吗？"
    print(f"用户输入: {user_input}")
    
    response = agent.chat(user_input)
    print(f"AI回复: {response}")
    
    # 验证是否包含关键信息
    has_name = "小明" in response
    has_profession = "程序员" in response
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"记住姓名: {'✓' if has_name else '✗'}")
    print(f"记住职业: {'✓' if has_profession else '✗'}")
    
    if has_name and has_profession:
        print("\n🎉 简化版短期记忆功能测试通过！")
        return True
    else:
        print("\n⚠️  简化版短期记忆功能测试未通过！")
        return False

if __name__ == "__main__":
    success = simple_short_term_memory_test()
    exit(0 if success else 1)