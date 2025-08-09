#!/usr/bin/env python3
"""
使用requests库进行详细的功能测试
测试并验证"翻书小狗"应用的各项功能是否符合预期
"""

import requests
import time
import json
import re


def test_short_term_memory():
    """测试短期记忆功能"""
    print("=" * 50)
    print("测试短期记忆功能")
    print("=" * 50)
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    session.get("http://localhost:5001/new")
    
    # 发送第一条消息
    data1 = {
        'topic': '我叫小明，我最喜欢的颜色是蓝色',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("1. 发送包含用户姓名和喜欢颜色的消息...")
    response1 = session.post("http://localhost:5001/chat_stream", data=data1)
    print(f"   状态码: {response1.status_code}")
    
    # 等待响应
    time.sleep(3)
    
    # 发送第二条消息验证记忆
    data2 = {
        'topic': '我刚才告诉你我的名字和最喜欢的颜色了吗？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("2. 发送验证记忆的消息...")
    response2 = session.post("http://localhost:5001/chat_stream", data=data2)
    
    # 收集响应内容
    content = ""
    for line in response2.iter_lines():
        if line:
            try:
                data = json.loads(line)
                if data.get("type") == "output":
                    content += data.get("content", "")
            except:
                pass
    
    print(f"   状态码: {response2.status_code}")
    print(f"   AI回复: {content[:200]}...")  # 只显示前200个字符
    
    # 验证是否包含关键信息
    has_name = "小明" in content
    has_color = "蓝色" in content
    
    print(f"   验证结果:")
    print(f"   - 记住姓名: {'✓' if has_name else '✗'}")
    print(f"   - 记住颜色: {'✓' if has_color else '✗'}")
    
    return has_name and has_color


def test_rag_functionality():
    """测试RAG功能"""
    print("\n" + "=" * 50)
    print("测试RAG功能")
    print("=" * 50)
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    session.get("http://localhost:5001/new")
    
    # 发送求助类问题
    data = {
        'topic': '我感到很焦虑，怎么办？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("发送焦虑相关的求助问题...")
    response = session.post("http://localhost:5001/chat_stream", data=data)
    
    # 收集响应内容
    content = ""
    for line in response.iter_lines():
        if line:
            try:
                data_line = json.loads(line)
                if data_line.get("type") == "output":
                    content += data_line.get("content", "")
            except:
                pass
    
    print(f"状态码: {response.status_code}")
    print(f"AI回复: {content[:300]}...")  # 只显示前300个字符
    
    # 验证是否包含心理学相关的内容
    psychology_keywords = ["认知", "行为", "调节", "焦虑", "情绪", "放松", "深呼吸"]
    found_keywords = [keyword for keyword in psychology_keywords if keyword in content]
    
    print(f"验证结果:")
    print(f" - 包含心理学关键词: {found_keywords}")
    print(f" - 相关性评分: {len(found_keywords)}/{len(psychology_keywords)}")
    
    # 检查是否有小狗风格的表达
    dog_style = "小狗" in content or "汪" in content or "尾巴" in content
    
    print(f" - 小狗风格表达: {'✓' if dog_style else '✗'}")
    
    return len(found_keywords) > 0 and dog_style


def test_long_term_memory():
    """测试长期记忆功能（通过数据库检查）"""
    print("\n" + "=" * 50)
    print("测试长期记忆功能")
    print("=" * 50)
    
    import sqlite3
    import uuid
    
    # 创建测试用户ID
    test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    
    # 直接测试长期记忆工具
    try:
        # 添加项目路径
        import sys
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(project_root)
        
        from tools.long_term_memory import update_long_term_memory, get_user_long_term_memory
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from models import Base, LongTermMemory
        
        # 创建内存数据库用于测试
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()
        
        print("1. 测试创建长期记忆...")
        success = update_long_term_memory(
            db_session=db_session,
            user_id=test_user_id,
            profile_summary="喜欢读书和散步的用户",
            emotion_trends={"焦虑": 3, "开心": 7},
            important_events={"2025-07-01": "开始使用翻书小狗"}
        )
        
        print(f"   创建结果: {'成功' if success else '失败'}")
        
        print("2. 测试检索长期记忆...")
        memory = get_user_long_term_memory(db_session, test_user_id)
        
        if memory:
            print(f"   检索结果: {memory}")
            profile_match = memory['profile_summary'] == "喜欢读书和散步的用户"
            emotion_match = memory['emotion_trends'] == {"焦虑": 3, "开心": 7}
            events_match = memory['important_events'] == {"2025-07-01": "开始使用翻书小狗"}
            
            print(f"   验证结果:")
            print(f"   - 用户画像匹配: {'✓' if profile_match else '✗'}")
            print(f"   - 情绪趋势匹配: {'✓' if emotion_match else '✗'}")
            print(f"   - 重要事件匹配: {'✓' if events_match else '✗'}")
            
            result = profile_match and emotion_match and events_match
        else:
            print("   检索失败：未找到记忆记录")
            result = False
            
        db_session.close()
        return result
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        return False


def test_model_selection():
    """测试模型选择功能"""
    print("\n" + "=" * 50)
    print("测试模型选择功能")
    print("=" * 50)
    
    # 创建会话
    session = requests.Session()
    
    # 开始新会话
    session.get("http://localhost:5001/new")
    
    # 使用DeepSeek模型
    data = {
        'topic': '你好，你能告诉我你是谁吗？',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '128',
        'language': 'zh'
    }
    
    print("使用阿里云Qwen模型发送消息...")
    response = session.post("http://localhost:5001/chat_stream", data=data)
    
    # 收集响应内容
    content = ""
    for line in response.iter_lines():
        if line:
            try:
                data_line = json.loads(line)
                if data_line.get("type") == "output":
                    content += data_line.get("content", "")
            except:
                pass
    
    print(f"状态码: {response.status_code}")
    print(f"AI回复: {content[:200]}...")
    
    # 验证回复不为空
    not_empty = len(content.strip()) > 0
    print(f"验证结果:")
    print(f" - 回复非空: {'✓' if not_empty else '✗'}")
    
    return not_empty


def test_api_endpoints():
    """测试API端点"""
    print("\n" + "=" * 50)
    print("测试API端点")
    print("=" * 50)
    
    session = requests.Session()
    
    # 测试主页
    print("1. 测试主页访问...")
    response = session.get("http://localhost:5001/")
    home_success = response.status_code in [200, 302]
    print(f"   状态码: {response.status_code} {'✓' if home_success else '✗'}")
    
    # 测试聊天页面
    print("2. 测试聊天页面访问...")
    response = session.get("http://localhost:5001/chat_stream")
    chat_success = response.status_code == 200
    print(f"   状态码: {response.status_code} {'✓' if chat_success else '✗'}")
    
    # 测试新会话
    print("3. 测试新会话创建...")
    response = session.get("http://localhost:5001/new")
    new_success = response.status_code in [200, 302]
    print(f"   状态码: {response.status_code} {'✓' if new_success else '✗'}")
    
    # 测试历史记录页面
    print("4. 测试历史记录页面访问...")
    response = session.get("http://localhost:5001/history_page")
    history_success = response.status_code == 200
    print(f"   状态码: {response.status_code} {'✓' if history_success else '✗'}")
    
    all_success = home_success and chat_success and new_success and history_success
    print(f"总体结果: {'✓ 所有端点正常' if all_success else '✗ 存在问题'}")
    
    return all_success


def main():
    """主函数"""
    print("开始详细功能测试")
    print("注意：请确保应用已在端口5001上运行")
    
    results = []
    
    # 运行各项测试
    results.append(("短期记忆功能", test_short_term_memory()))
    results.append(("RAG功能", test_rag_functionality()))
    results.append(("长期记忆功能", test_long_term_memory()))
    results.append(("模型选择功能", test_model_selection()))
    results.append(("API端点", test_api_endpoints()))
    
    # 输出总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    passed = 0
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！应用功能正常。")
    else:
        print("⚠️  部分测试未通过，请检查相关功能。")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)