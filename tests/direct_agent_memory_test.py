#!/usr/bin/env python3
"""
直接测试Agent的短期记忆功能
"""

from agent import DogAgent
from langchain_core.messages import HumanMessage, AIMessage

def direct_agent_memory_test():
    """直接测试Agent的短期记忆功能"""
    print("=" * 60)
    print("直接测试Agent的短期记忆功能")
    print("=" * 60)
    
    # 测试1: 创建带有历史记录的Agent并验证记忆
    print("\n测试1: 验证Agent是否能记住用户信息")
    chat_history = [
        HumanMessage(content="你好，我叫小红，我是一名教师，最喜欢的颜色是粉色"),
        AIMessage(content="你好小红！很高兴认识你，教师是一个很崇高的职业呢！粉色是很可爱的颜色。")
    ]
    
    agent = DogAgent(
        model_provider="deepseek",
        model_name="deepseek-chat",
        chat_history=chat_history,
        max_iterations=5
    )
    
    # 测试是否记住用户信息
    user_input = "还记得我的名字、职业和最喜欢的颜色吗？"
    print(f"用户输入: {user_input}")
    
    response = agent.chat(user_input)
    print(f"AI回复: {response}")
    
    # 验证是否包含关键信息
    has_name = "小红" in response
    has_profession = "教师" in response
    has_color = "粉色" in response
    
    print("\n测试1结果:")
    print(f"记住姓名: {'✓' if has_name else '✗'}")
    print(f"记住职业: {'✓' if has_profession else '✗'}")
    print(f"记住颜色: {'✓' if has_color else '✗'}")
    
    test1_passed = has_name and has_profession and has_color
    
    # 测试2: 多轮对话记忆
    print("\n" + "-" * 40)
    print("测试2: 多轮对话记忆")
    
    # 添加更多对话历史
    chat_history.extend([
        HumanMessage(content="我最近在学习心理学课程"),
        AIMessage(content="哇，心理学是很有趣的学科呢！")
    ])
    
    agent2 = DogAgent(
        model_provider="deepseek",
        model_name="deepseek-chat",
        chat_history=chat_history,
        max_iterations=5
    )
    
    user_input2 = "我还告诉你我在学什么课程吗？"
    print(f"用户输入: {user_input2}")
    
    response2 = agent2.chat(user_input2)
    print(f"AI回复: {response2}")
    
    # 验证是否包含心理学信息
    has_psychology = "心理学" in response2
    
    print("\n测试2结果:")
    print(f"记住课程: {'✓' if has_psychology else '✗'}")
    
    test2_passed = has_psychology
    
    print("\n" + "=" * 60)
    print("最终测试结果")
    print("=" * 60)
    if test1_passed and test2_passed:
        print("🎉 直接Agent短期记忆功能测试通过！")
        return True
    else:
        print("⚠️  直接Agent短期记忆功能测试未通过！")
        return False

if __name__ == "__main__":
    success = direct_agent_memory_test()
    exit(0 if success else 1)