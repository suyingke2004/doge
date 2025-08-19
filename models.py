from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # 关联会话
    sessions = relationship("ChatSession", back_populates="user")
    
    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}')>"

class ChatSession(Base):
    __tablename__ = 'chat_session'
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey('user.id'))
    start_time = Column(DateTime, default=datetime.utcnow)
    # 添加一个字段来存储第一个用户问题作为会话标题
    title = Column(String(200), nullable=True)
    
    # 关联用户和消息
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(id='{self.id}', start_time='{self.start_time}')>"

class ChatMessage(Base):
    __tablename__ = 'chat_message'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), ForeignKey('chat_session.id'), nullable=False)
    message_type = Column(String(10), nullable=False)  # 'human' or 'ai'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(session_id='{self.session_id}', type='{self.message_type}')>"

class LongTermMemory(Base):
    __tablename__ = 'long_term_memory'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)  # 用户ID，可以关联到会话或其他用户标识
    profile_summary = Column(Text)  # 用户画像摘要
    emotion_trends = Column(JSON)   # 情绪趋势，存储为JSON格式
    important_events = Column(JSON) # 重要事件，存储为JSON格式
    
    def __repr__(self):
        return f"<LongTermMemory(user_id='{self.user_id}')>"