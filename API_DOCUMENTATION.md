# API 文档：翻书小狗后台服务

## 1. 对话核心接口

处理用户发送的每一条消息，并返回小狗的完整回复

- 接口名称: /api/chat
- 请求方式: POST
- 描述: 接收用户输入，后端进行情绪识别、RAG查询、回复生成，并返回所有必要信息。
- 请求参数:
```json
{
  "user_id": "string",
  "user_message": "string"
}
```
- 返回参数:
```json
{
  "status": "success",
  "code": 200,
  "message": "OK",
  "response_data": {
    "text_blocks": [
      {
        "order": 1,
        "type": "emotion_feedback",
        "content": "(等你说完，立刻凑得更近，尾巴慢下来但还在轻轻晃) 哇！吃到喜欢的饭一定超开心吧..."
      },
      {
        "order": 2,
        "type": "rag_knowledge",
        "content": "（突然转身跑到垫子上，叼来一本封面画着骨头的小本子...）我翻了翻这本'心理学xx'..."
      },
      {
        "order": 3,
        "type": "dog_literature",
        "content": "（突然站起来，前爪搭在你膝盖上，舌头舔舔你的手）你的不开心呀，小狗用尾巴给你扫扫..."
      }
    ],
    "action": {
      "code": "wagging_tail",
      "display": "摇尾巴"
    },
    "emotion_type": "anxiety",
    "intensity": 7,
    "timestamp": "2025-08-12T10:20:30Z"
  }
}
```

## 2. 历史记录接口

用于获取用户的历史对话记录，以实现次日回访和情绪趋势分析。

- 接口名称: /api/history
- 请求方式: GET
- 描述: 获取用户的历史对话记录，支持分页查询。
- 请求参数:
```json
{
  "user_id": "string",
  "limit": "integer", 
  "offset": "integer"
}
```
- 返回参数:
```json
{
  "status": "success",
  "code": 200,
  "message": "OK",
  "response_data": {
    "total": "integer",
    "history_list": [
      {
        "user_message": "string",
        "dog_response": "string",
        "emotion_type": "anxiety",
        "intensity": 7,
        "action": {
          "code": "wagging_tail",
          "display": "摇尾巴"
        },
        "timestamp": "2025-08-12T10:20:30Z"
      }
    ]
  }
}
```

## 3. 用户注册接口

用于新用户注册账号

- 接口名称: /api/user/register
- 请求方式: POST
- 描述: 创建新用户账号，返回用户ID和访问令牌。
- 请求参数:
```json
{
  "username": "string",
  "password": "string",
  "email": "string"
}
```
- 返回参数:
```json
{
  "status": "success",
  "code": 200,
  "message": "注册成功",
  "response_data": {
    "user_id": "string",
    "access_token": "string",
    "expires_in": "integer"
  }
}
```

## 4. 日记功能接口（MVP暂时不上该功能）

用于用户提交晚安日记，并获取相应的知识卡片。

- 接口名称: /api/diary
- 请求方式: POST
- 描述: 用户提交晚安日记，并返回一个知识卡片。
- 请求参数:
```json
{
  "user_id": "string",
  "diary_content": "string"
}
```
- 返回参数:
```json
{
  "status": "success",
  "code": 200,
  "message": "OK",
  "response_data": {
    "knowledge_card": "string",
    "card_type": "psychology_tip",
    "send_status": "pending_delivery"
  }
}
```

## 5. 长期记忆更新接口

用于更新用户的长期记忆信息，包括用户画像、情绪趋势和重要事件。

- 接口名称: /api/memory/update
- 请求方式: POST
- 描述: 更新用户的长期记忆信息。
- 请求参数:
```json
{
  "user_id": "string",
  "profile_summary": "string", 
  "emotion_trends": {
    "anxiety": 7,
    "happiness": 3
  },
  "important_events": {
    "2025-08-12": "开始使用翻书小狗"
  }
}
```
- 返回参数:
```json
{
  "status": "success",
  "code": 200,
  "message": "长期记忆更新成功"
}
```

## 6. 知识库搜索接口

根据用户问题从心理学知识库中检索相关信息。

- 接口名称: /api/knowledge/search
- 请求方式: POST
- 描述: 根据用户问题从心理学知识库中检索相关信息。
- 请求参数:
```json
{
  "query": "string"
}
```
- 返回参数:
```json
{
  "status": "success",
  "code": 200,
  "message": "OK",
  "response_data": {
    "knowledge_context": "string"
  }
}
```

## 7. 情绪识别接口

分析用户输入的情绪类别和强度。

- 接口名称: /api/emotion/recognize
- 请求方式: POST
- 描述: 分析用户输入的情绪类别和强度。
- 请求参数:
```json
{
  "text": "string"
}
```
- 返回参数:
```json
{
  "status": "success",
  "code": 200,
  "message": "OK",
  "response_data": {
    "emotion_type": "anxiety",
    "intensity": 7
  }
}
```

## 8. PDF报告生成接口

生成用户对话历史的PDF报告。

- 接口名称: /api/report/generate
- 请求方式: POST
- 描述: 生成用户对话历史的PDF报告。
- 请求参数:
```json
{
  "user_id": "string"
}
```
- 返回参数:
```json
{
  "status": "success",
  "code": 200,
  "message": "OK",
  "response_data": {
    "pdf_url": "string"
  }
}
```