import json
import pytest
from app import app
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """创建一个测试客户端"""
    app.config['TESTING'] = True
    app.secret_key = 'test_secret_key'
    with app.test_client() as client:
        yield client


@patch('app.NewsletterAgent')
def test_status_indicator_parsing(mock_agent_class, client):
    """测试状态指示功能的完整解析流程"""
    # 创建模拟代理实例
    mock_agent = MagicMock()
    mock_agent_class.return_value = mock_agent
    
    # 模拟流式响应，包含多行JSON消息
    async def mock_stream_generator(_):
        # 发送多行JSON消息来模拟真实场景
        yield {"type": "status", "content": "[正在调用工具: Search_News]"}
        yield {"type": "output", "content": "# 新闻标题\n\n"}
        yield {"type": "status", "content": "[正在调用工具: Scrape_Article_Content]"}
        yield {"type": "output", "content": "这是新闻内容摘要。\n"}
        yield {"type": "status", "content": "[正在调用工具: Search_Reddit]"}
        yield {"type": "output", "content": "这是Reddit讨论摘要。"}
    
    mock_agent.generate_newsletter_stream = mock_stream_generator
    
    # 发送请求
    response = client.post('/chat_stream', data={
        'topic': '测试主题',
        'model_provider': 'openai',
        'model_name': 'gpt-3.5-turbo'
    })
    
    # 检查响应
    assert response.status_code == 200
    assert response.content_type == 'text/plain; charset=utf-8'
    
    # 获取响应数据
    response_data = response.get_data(as_text=True)
    
    # 验证响应包含换行符分隔的JSON对象
    lines = response_data.strip().split('\n')
    assert len(lines) >= 6  # 应该至少有6行（每条消息一行）
    
    # 验证每行都是有效的JSON
    parsed_messages = []
    for line in lines:
        if line.strip():  # 忽略空行
            try:
                message = json.loads(line)
                parsed_messages.append(message)
                assert 'type' in message
                assert 'content' in message
                assert message['type'] in ['status', 'output']
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON in response: {line}")
    
    # 验证消息类型和内容
    status_count = sum(1 for msg in parsed_messages if msg['type'] == 'status')
    output_count = sum(1 for msg in parsed_messages if msg['type'] == 'output')
    
    assert status_count >= 3  # 应该至少有3个状态消息
    assert output_count >= 3  # 应该至少有3个输出消息
    
    # 验证特定状态消息
    status_contents = [msg['content'] for msg in parsed_messages if msg['type'] == 'status']
    assert any("[正在调用工具: Search_News]" in content for content in status_contents)
    assert any("[正在调用工具: Scrape_Article_Content]" in content for content in status_contents)
    assert any("[正在调用工具: Search_Reddit]" in content for content in status_contents)
    
    # 验证输出消息内容
    output_contents = [msg['content'] for msg in parsed_messages if msg['type'] == 'output']
    assert any("新闻标题" in content for content in output_contents)
    assert any("新闻内容摘要" in content for content in output_contents)
    assert any("Reddit讨论摘要" in content for content in output_contents)


@patch('app.NewsletterAgent')
def test_status_indicator_with_error(mock_agent_class, client):
    """测试状态指示功能在错误情况下的处理"""
    # 创建模拟代理实例
    mock_agent = MagicMock()
    mock_agent_class.return_value = mock_agent
    
    # 模拟流式响应，包含错误消息
    async def mock_stream_generator(_):
        yield {"type": "status", "content": "[正在调用工具: Search_News]"}
        yield {"type": "output", "content": "# 测试标题\n"}
        yield {"type": "output", "content": "测试内容"}
        yield {"type": "output", "content": "\n\n[发生错误: 网络连接问题]"}
    
    mock_agent.generate_newsletter_stream = mock_stream_generator
    
    # 发送请求
    response = client.post('/chat_stream', data={
        'topic': '测试主题',
        'model_provider': 'openai',
        'model_name': 'gpt-3.5-turbo'
    })
    
    # 检查响应
    assert response.status_code == 200
    
    # 获取响应数据
    response_data = response.get_data(as_text=True)
    lines = response_data.strip().split('\n')
    
    # 验证包含错误消息
    parsed_messages = []
    for line in lines:
        if line.strip():
            try:
                message = json.loads(line)
                parsed_messages.append(message)
            except json.JSONDecodeError:
                pass  # 忽略非JSON行
    
    # 验证包含错误消息
    output_contents = [msg['content'] for msg in parsed_messages if msg['type'] == 'output']
    assert any("[发生错误: 网络连接问题]" in content for content in output_contents)