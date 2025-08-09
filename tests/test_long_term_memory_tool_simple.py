#!/usr/bin/env python3
"""
测试长期记忆工具
"""

import sys
import os
from unittest.mock import MagicMock

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from tools.long_term_memory_tool import UpdateLongTermMemoryTool
from tools.long_term_memory import update_long_term_memory


def test_long_term_memory_tool():
    """测试长期记忆工具"""
    # 创建数据库会话的mock
    mock_db_session = MagicMock()
    
    # 创建工具实例
    tool = UpdateLongTermMemoryTool(db_session=mock_db_session)
    
    # 验证工具属性
    print(f"工具名称: {tool.name}")
    print(f"工具是否有db_session属性: {hasattr(tool, 'db_session')}")
    
    # 测试运行工具
    result = tool._run(
        user_id="test_user",
        profile_summary="测试用户",
        emotion_trends='{"焦虑": 5}',
        important_events='{"2025-08-10": "测试长期记忆功能"}'
    )
    
    print(f"工具运行结果: {result}")


if __name__ == "__main__":
    test_long_term_memory_tool()