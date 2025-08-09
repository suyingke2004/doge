#!/usr/bin/env python3
"""
快速验证脚本：验证记忆模块、RAG知识库和RAG检索功能
"""

import sys
import os
from collections import deque

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from tools.long_term_memory import update_long_term_memory, get_user_long_term_memory
from tools.knowledge_base_search import search_knowledge_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, LongTermMemory

def test_short_term_memory():
    """测试短期记忆功能"""
    print("测试短期记忆功能...")
    
    # 创建短期记忆
    short_term_memory = deque(maxlen=3)
    short_term_memory.append({'type': 'human', 'content': '你好'})
    short_term_memory.append({'type': 'ai', 'content': '你好！我是翻书小狗！'})
    short_term_memory.append({'type': 'human', 'content': '今天心情不好'})
    short_term_memory.append({'type': 'ai', 'content': '抱抱你，小狗在这里陪着你'})
    
    # 验证
    assert len(short_term_memory) == 3, "短期记忆长度应该为3"
    assert short_term_memory[-1]['content'] == '抱抱你，小狗在这里陪着你', "最后一条记录应该是AI的回复"
    assert short_term_memory[0]['content'] == '你好！我是翻书小狗！', "第一条记录应该是AI的欢迎语"
    
    print("✓ 短期记忆功能测试通过")
    return True

def test_long_term_memory():
    """测试长期记忆功能"""
    print("测试长期记忆功能...")
    
    # 创建内存数据库用于测试
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    try:
        user_id = "quick_test_user"
        profile_summary = "喜欢读书和散步的用户"
        emotion_trends = {"焦虑": 3, "开心": 7}
        important_events = {"2025-07-01": "开始使用翻书小狗"}

        # 更新长期记忆
        success = update_long_term_memory(
            db_session=db_session,
            user_id=user_id,
            profile_summary=profile_summary,
            emotion_trends=emotion_trends,
            important_events=important_events
        )
        
        assert success, "长期记忆更新应该成功"
        
        # 验证记录是否创建成功
        memory = get_user_long_term_memory(db_session, user_id)
        assert memory is not None, "应该能够检索到长期记忆"
        assert memory['profile_summary'] == profile_summary, "用户画像应该匹配"
        assert memory['emotion_trends'] == emotion_trends, "情绪趋势应该匹配"
        assert memory['important_events'] == important_events, "重要事件应该匹配"
        
        print("✓ 长期记忆功能测试通过")
        return True
    finally:
        db_session.close()

def test_rag_knowledge_base():
    """测试RAG知识库"""
    print("测试RAG知识库...")
    
    # 检查知识库文件是否存在
    knowledge_files = [
        "knowledge_base/sources/cbt.txt",
        "knowledge_base/sources/emotion_regulation.txt",
        "knowledge_base/sources/mindfulness.txt"
    ]
    
    for file_path in knowledge_files:
        assert os.path.exists(file_path), f"知识库文件 {file_path} 不存在"
    
    # 检查向量数据库文件
    vector_db_path = "knowledge_base/vector_db.index"
    metadata_path = "knowledge_base/metadata.npy"
    
    assert os.path.exists(vector_db_path), "向量数据库文件不存在"
    assert os.path.exists(metadata_path), "元数据文件不存在"
    
    print("✓ RAG知识库测试通过")
    return True

def test_rag_search():
    """测试RAG检索功能"""
    print("测试RAG检索功能...")
    
    # 测试相关查询的检索
    query = "我感到很焦虑，怎么办？"
    result = search_knowledge_base(query)
    
    # 验证返回结果
    assert result is not None, "检索结果不应该为None"
    assert result != "", "检索结果不应该为空"
    assert "知识库检索出错" not in result, "不应该出现检索错误"
    
    # 验证结果包含与焦虑相关的内容
    result_lower = result.lower()
    assert (
        "焦虑" in result_lower or 
        "情绪" in result_lower or 
        "调节" in result_lower
    ), "检索结果应该包含与焦虑相关的内容"
    
    print("✓ RAG检索功能测试通过")
    return True

def main():
    """主函数"""
    print("开始快速验证所有任务...")
    print("=" * 50)
    
    try:
        # 测试所有任务
        test_short_term_memory()
        test_long_term_memory()
        test_rag_knowledge_base()
        test_rag_search()
        
        print("=" * 50)
        print("✓ 所有任务验证通过！")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)