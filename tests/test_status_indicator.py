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
def test_status_indicator_streaming(mock_agent_class, client):
    """测试状态指示功能的流式处理"""
    # 创建模拟代理实例
    mock_agent = MagicMock()
    mock_agent_class.return_value = mock_agent
    
    # 模拟流式响应，包含状态消息和输出消息
    async def mock_stream_generator(_):
        yield {"type": "status", "content": "[正在调用工具: Search_News]"}
        yield {"type": "output", "content": "# 测试标题\n"}
        yield {"type": "status", "content": "[正在调用工具: Scrape_Article_Content]"}
        yield {"type": "output", "content": "这是测试内容"}
    
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
    
    # 解析响应内容
    response_data = response.get_data(as_text=True)
    lines = response_data.strip().split('\n')
    
    # 验证每一行都是有效的JSON
    for line in lines:
        if line:  # 忽略空行
            try:
                json.loads(line)
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON in response: {line}")
    
    # 验证包含状态消息和输出消息
    status_count = 0
    output_count = 0
    for line in lines:
        if line:
            message = json.loads(line)
            if message['type'] == 'status':
                status_count += 1
            elif message['type'] == 'output':
                output_count += 1
    
    assert status_count >= 2  # 应该至少有2个状态消息
    assert output_count >= 2  # 应该至少有2个输出消息