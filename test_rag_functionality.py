#!/usr/bin/env python3
"""
测试RAG模块的核心功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.knowledge_base_search import search_knowledge_base

def test_rag_functionality():
    """测试RAG功能"""
    print("=== 测试RAG模块功能 ===\n")
    
    # 测试焦虑相关查询
    print("1. 测试焦虑相关查询:")
    result = search_knowledge_base("我感到很焦虑，怎么办？")
    print(f"查询: 我感到很焦虑，怎么办？")
    print(f"结果: {result[:300]}...\n")
    
    # 测试拖延症相关查询
    print("2. 测试拖延症相关查询:")
    result = search_knowledge_base("如何克服拖延症？")
    print(f"查询: 如何克服拖延症？")
    print(f"结果: {result[:300]}...\n")
    
    # 测试情绪调节相关查询
    print("3. 测试情绪调节相关查询:")
    result = search_knowledge_base("如何调节负面情绪？")
    print(f"查询: 如何调节负面情绪？")
    print(f"结果: {result[:300]}...\n")
    
    # 测试不相关查询
    print("4. 测试不相关查询:")
    result = search_knowledge_base("今天天气怎么样？")
    print(f"查询: 今天天气怎么样？")
    print(f"结果: {result[:300]}...\n")

if __name__ == "__main__":
    test_rag_functionality()