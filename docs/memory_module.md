# 记忆模块使用说明

## 概述

记忆模块为"翻书小狗"AI代理提供了短期和长期记忆功能，以增强对话的连贯性和个性化体验。

## 短期记忆

短期记忆用于存储最近的对话历史，帮助AI理解当前对话的上下文。

### 实现方式

使用Python的`collections.deque`数据结构实现，最大长度设置为10轮对话。

### 使用方法

短期记忆在`app.py`的聊天处理逻辑中自动管理：

1. 每次用户发送消息时，会自动添加到短期记忆中
2. 当短期记忆达到最大长度时，最旧的对话会被自动移除
3. 短期记忆会传递给`DogAgent`，作为对话历史的一部分

## 长期记忆

长期记忆用于存储用户的个人信息、情绪趋势和重要事件，为AI提供更深入的用户理解。

### 数据模型

在`models.py`中定义了`LongTermMemory`模型：

- `user_id`: 用户唯一标识
- `profile_summary`: 用户画像摘要
- `emotion_trends`: 情绪趋势（JSON格式）
- `important_events`: 重要事件（JSON格式）

### 使用方法

长期记忆需要手动管理：

1. 从数据库查询用户长期记忆：
   ```python
   long_term_memory = db_session.query(LongTermMemory).filter_by(user_id=user_id).first()
   ```

2. 创建或更新长期记忆：
   ```python
   long_term_memory = LongTermMemory(
       user_id=user_id,
       profile_summary="用户画像描述",
       emotion_trends={"焦虑": 3, "开心": 7},
       important_events={"2025-07-01": "开始使用翻书小狗"}
   )
   db_session.add(long_term_memory)
   db_session.commit()
   ```

## 在Agent中使用记忆

`DogAgent`类在初始化时接收`memory_context`参数，该参数包含短期和长期记忆信息，并将其整合到系统提示中。

示例：
```python
agent = DogAgent(
    model_provider="ali",
    model_name="qwen-max",
    chat_history=chat_history_messages,
    max_iterations=64,
    language="zh",
    memory_context={
        'short_term': short_term_memory,
        'long_term': {
            'profile_summary': long_term_memory.profile_summary if long_term_memory else '',
            'emotion_trends': long_term_memory.emotion_trends if long_term_memory else {},
            'important_events': long_term_memory.important_events if long_term_memory else {}
        }
    }
)
```

## 测试

运行测试以验证记忆模块功能：
```bash
python -m pytest test_memory_module.py -v
```