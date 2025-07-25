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


def test_app_routes_exist(client):
    """测试应用路由是否存在"""
    # 测试根路由
    response = client.get('/')
    assert response.status_code == 302  # 重定向到 /chat_stream
    
    # 测试 /chat_stream GET 请求
    response = client.get('/chat_stream')
    assert response.status_code == 200
    
    # 测试 /new 路由
    response = client.get('/new')
    assert response.status_code == 302  # 重定向到 /chat_stream


@patch('app.NewsletterAgent')
def test_single_turn_conversation(mock_agent_class, client):
    """测试单轮对话"""
    # 创建模拟代理实例
    mock_agent = MagicMock()
    mock_agent_class.return_value = mock_agent
    
    # 模拟流式响应
    async def mock_stream_generator(topic):
        yield "# 测试响应\n"
        yield "这是测试内容"
    
    mock_agent.generate_newsletter_stream = mock_stream_generator
    
    # 发送对话请求
    response = client.post('/chat_stream', data={
        'topic': '测试主题',
        'model_provider': 'deepseek'
    })
    
    # 检查响应状态
    assert response.status_code == 200


@patch('app.NewsletterAgent')
def test_empty_input_validation(mock_agent_class, client):
    """测试空输入验证"""
    # 发送空输入
    response = client.post('/chat_stream', data={
        'topic': '',
        'model_provider': 'deepseek'
    })
    
    # 检查响应状态
    assert response.status_code == 200
    assert "错误：请输入一个主题或问题。" in response.data.decode('utf-8')


def test_session_management(client):
    """测试会话管理"""
    # 开始新对话
    response = client.get('/new')
    assert response.status_code == 302
    assert response.location == '/chat_stream'