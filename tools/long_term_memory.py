import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from models import LongTermMemory


def update_long_term_memory(
    db_session: Session,
    user_id: str,
    profile_summary: Optional[str] = None,
    emotion_trends: Optional[Dict[str, Any]] = None,
    important_events: Optional[Dict[str, Any]] = None
) -> bool:
    """
    更新用户的长期记忆
    
    Args:
        db_session: 数据库会话
        user_id: 用户ID
        profile_summary: 用户画像摘要
        emotion_trends: 情绪趋势字典
        important_events: 重要事件字典
    
    Returns:
        bool: 更新是否成功
    """
    try:
        # 查找现有记录
        long_term_memory = db_session.query(LongTermMemory).filter_by(user_id=user_id).first()
        
        # 如果记录不存在，创建新记录
        if not long_term_memory:
            long_term_memory = LongTermMemory(user_id=user_id)
            db_session.add(long_term_memory)
        
        # 更新字段（如果提供了新值）
        if profile_summary is not None:
            long_term_memory.profile_summary = profile_summary
            
        if emotion_trends is not None:
            # 合并现有情绪趋势和新趋势
            if long_term_memory.emotion_trends:
                existing_trends = long_term_memory.emotion_trends.copy()
                existing_trends.update(emotion_trends)
                long_term_memory.emotion_trends = existing_trends
            else:
                long_term_memory.emotion_trends = emotion_trends
                
        if important_events is not None:
            # 合并现有重要事件和新事件
            if long_term_memory.important_events:
                existing_events = long_term_memory.important_events.copy()
                existing_events.update(important_events)
                long_term_memory.important_events = existing_events
            else:
                long_term_memory.important_events = important_events
        
        # 提交更改
        db_session.commit()
        return True
        
    except Exception as e:
        # 回滚更改
        db_session.rollback()
        print(f"更新长期记忆时出错: {e}")
        return False


def get_user_long_term_memory(db_session: Session, user_id: str) -> Optional[Dict[str, Any]]:
    """
    获取用户的长期记忆
    
    Args:
        db_session: 数据库会话
        user_id: 用户ID
    
    Returns:
        Dict: 用户的长期记忆信息，如果未找到则返回None
    """
    try:
        long_term_memory = db_session.query(LongTermMemory).filter_by(user_id=user_id).first()
        
        if long_term_memory:
            return {
                'profile_summary': long_term_memory.profile_summary,
                'emotion_trends': long_term_memory.emotion_trends,
                'important_events': long_term_memory.important_events
            }
        return None
        
    except Exception as e:
        print(f"获取长期记忆时出错: {e}")
        return None