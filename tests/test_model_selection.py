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
def test_model_selection_with_provider_and_model_name(mock_agent_class, client):
    """测试使用提供商和模型名称进行模型选择"""
    # 创建模拟代理实例
    mock_agent = MagicMock()
    mock_agent_class.return_value = mock_agent
    
    # 模拟 generate_newsletter 方法的返回值
    mock_agent.generate_newsletter.return_value = "# 测试响应\n这是测试内容"
    
    # 使用提供商和模型名称进行第一次对话
    response = client.post('/chat', data={
        'topic': 'AI技术发展',
        'model_provider': 'openai',
        'model_name': 'gpt-4'
    })
    
    # 检查对话是否成功
    assert response.status_code == 200
    
    # 验证 NewsletterAgent 是否使用了正确的参数创建
    mock_agent_class.assert_called_with(
        model_provider='openai',
        model_name='gpt-4',
        chat_history=[]
    )


@patch('app.NewsletterAgent')
def test_model_selection_with_provider_only(mock_agent_class, client):
    """测试仅使用提供商进行模型选择（使用默认模型）"""
    # 创建模拟代理实例
    mock_agent = MagicMock()
    mock_agent_class.return_value = mock_agent
    
    # 模拟 generate_newsletter 方法的返回值
    mock_agent.generate_newsletter.return_value = "# 测试响应\n这是测试内容"
    
    # 仅使用提供商进行第一次对话（不提供模型名称）
    response = client.post('/chat', data={
        'topic': 'AI技术发展',
        'model_provider': 'deepseek'
    })
    
    # 检查对话是否成功
    assert response.status_code == 200
    
    # 验证 NewsletterAgent 是否使用了正确的参数创建
    mock_agent_class.assert_called_with(
        model_provider='deepseek',
        model_name=None,
        chat_history=[]
    )