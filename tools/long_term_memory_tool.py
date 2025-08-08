from langchain.tools import BaseTool
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import json
from tools.long_term_memory import update_long_term_memory, get_user_long_term_memory


class UpdateLongTermMemoryTool(BaseTool):
    name = "update_long_term_memory"
    description = """用于更新用户的长期记忆信息。
    
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

    def __init__(self, db_session: Session):
        super().__init__()
        self.db_session = db_session

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
                
            # 调用更新函数
            success = update_long_term_memory(
                db_session=self.db_session,
                user_id=user_id,
                profile_summary=profile_summary,
                emotion_trends=emotion_trends,
                important_events=important_events
            )
            
            if success:
                return "长期记忆更新成功"
            else:
                return "长期记忆更新失败"
                
        except json.JSONDecodeError as e:
            return f"参数格式错误: {e}"
        except Exception as e:
            return f"更新长期记忆时出错: {e}"

    async def _arun(self, *args, **kwargs) -> str:
        """异步版本"""
        return self._run(*args, **kwargs)