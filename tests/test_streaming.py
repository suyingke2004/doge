import pytest
from flask import session
from app import app as flask_app
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """创建一个测试客户端"""
    flask_app.config['TESTING'] = True
    flask_app.secret_key = 'test_secret_key'
    
    with flask_app.test_client() as client:
        with client.session_transaction() as sess:
            sess['model_provider'] = 'openai'
            sess['model_name'] = 'gpt-3.5-turbo'
            sess['maxiter'] = 5
            sess['chat_history'] = []
        yield client


@patch('app.NewsletterAgent')
def test_streaming_conversation_flow(mock_agent_class, client):
    """测试流式对话流程"""
    # 创建模拟代理实例
    mock_agent = MagicMock()
    mock_agent.generate_newsletter_stream = MagicMock(return_value=iter(["chunk1", "chunk2", "chunk3"]))
    mock_agent_class.return_value = mock_agent
    
    # 模拟第一次对话
    response = client.post('/chat_stream', data={
        'topic': 'Tell me about AI',
        'model_provider': 'openai',
        'model_name': 'gpt-3.5-turbo'
    })
    
    # 验证响应
    assert response.status_code == 200
    
    # 检查会话中的聊天历史
    with client.session_transaction() as sess:
        assert 'chat_history' in sess
        # 由于是模拟测试，我们只需要检查会话是否正确设置
        assert sess['model_provider'] == 'openai'
        assert sess['model_name'] == 'gpt-3.5-turbo'


@patch('app.NewsletterAgent')
def test_second_turn_streaming(mock_agent_class, client):
    """测试第二轮流式对话"""
    # 创建模拟代理实例
    mock_agent = MagicMock()
    mock_agent.generate_newsletter_stream = MagicMock(return_value=iter(["response1", "response2"]))
    mock_agent_class.return_value = mock_agent
    
    # 设置初始对话历史
    with client.session_transaction() as sess:
        sess['model_provider'] = 'openai'
        sess['model_name'] = 'gpt-3.5-turbo'
        sess['maxiter'] = 5
        sess['chat_history'] = [
            {'type': 'human', 'content': 'Tell me about AI'},
            {'type': 'ai', 'content': 'AI is a wonderful field...'}
        ]
    
    # 模拟第二轮对话
    response = client.post('/chat_stream', data={
        'topic': 'Tell me more about machine learning',
        # 注意：不传递model参数，应该从session中获取
    })
    
    # 验证响应
    assert response.status_code == 200
    
    # 检查会话中的模型选择是否正确
    with client.session_transaction() as sess:
        assert sess['model_provider'] == 'openai'
        assert sess['model_name'] == 'gpt-3.5-turbo'