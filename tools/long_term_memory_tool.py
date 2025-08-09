import sys
import os
from langchain.tools import BaseTool
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import json

# 添加项目根目录到sys.path，确保能够正确导入
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from tools.long_term_memory import update_long_term_memory, get_user_long_term_memory


class UpdateLongTermMemoryTool(BaseTool):
    name: str = "update_long_term_memory"
    description: str = """用于更新用户的长期记忆信息。
    
    当你了解到用户的个人信息、观察到用户的情绪变化或用户分享了重要事件时，可以使用此工具更新用户的长期记忆。
    
    参数:
    - user_id: 用户的唯一标识符
    - profile_summary: (可选) 用户画像摘要，例如"喜欢读书和散步的用户"
    - emotion_trends: (可选) 情绪趋势字典，例如{"焦虑": 3, "开心": 7}
    - important_events: (可选) 重要事件字典，例如{"2025-07-01": "开始为考试焦虑"}
    
    注意:
    - 只有在确定需要更新用户信息时才使用此工具
    - 参数可以部分提供，只更新提供的字段
    - 情绪趋势和重要事件会与现有数据合并，不会覆盖
    """

    def __init__(self):
        super().__init__()

    def _run(
        self,
        user_id: str,
        profile_summary: Optional[str] = None,
        emotion_trends: Optional[str] = None,
        important_events: Optional[str] = None
    ) -> str:
        """
        更新用户的长期记忆
        
        注意：LangChain工具要求所有参数都是字符串类型，所以我们需要解析JSON字符串
        """
        try:
            # 解析JSON字符串参数
            if emotion_trends:
                emotion_trends = json.loads(emotion_trends)
            if important_events:
                important_events = json.loads(important_events)
                
            # 从工具参数中获取db_session
            # 注意：这种方法可能不适用于所有情况，我们会在Agent中特殊处理
            return "工具调用需要在Agent中特殊处理"
                
        except json.JSONDecodeError as e:
            return f"参数格式错误: {e}"
        except Exception as e:
            return f"更新长期记忆时出错: {e}"

    async def _arun(self, *args, **kwargs) -> str:
        """异步版本"""
        return self._run(*args, **kwargs)