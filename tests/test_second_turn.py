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
def test_second_turn_conversation(mock_agent_class, client):
    """测试第二次对话是否能正常工作"""
    # 创建模拟代理实例
    mock_agent = MagicMock()
    mock_agent_class.return_value = mock_agent
    
    # 模拟 generate_newsletter 方法的返回值
    mock_agent.generate_newsletter.return_value = "# 测试响应\n这是测试内容"
    
    # 第一次对话
    response = client.post('/chat', data={
        'topic': 'AI技术发展',
        'model': 'openai'
    })
    
    # 检查第一次对话是否成功
    assert response.status_code == 200
    
    # 重置模拟对象的调用记录
    mock_agent.reset_mock()
    
    # 模拟 generate_newsletter_stream 方法的返回值
    async def mock_stream_generator():
        yield "这是"
        yield "流式"
        yield "响应"
    
    mock_agent.generate_newsletter_stream = mock_stream_generator
    
    # 第二次对话 - 流式
    response = client.post('/chat_stream', data={
        'topic': 'AI在医疗领域的应用',
    })
    
    # 检查第二次对话是否成功
    assert response.status_code == 200
    assert "错误：请输入一个主题或问题。" not in response.data.decode('utf-8')
    
    
def test_empty_input_in_second_turn(client):
    """测试第二次对话中空输入的情况"""
    # 第一次对话
    response = client.post('/chat', data={
        'topic': '科技新闻',
        'model': 'openai'
    })
    
    # 第二次对话 - 空输入
    response = client.post('/chat_stream', data={
        'topic': '',
    })
    
    # 应该返回错误信息
    assert response.status_code == 200
    assert "错误：请输入一个主题或问题。" in response.data.decode('utf-8')