import pytest
from app import app


@pytest.fixture
def client():
    """创建一个测试客户端"""
    app.config['TESTING'] = True
    app.secret_key = 'test_secret_key'
    with app.test_client() as client:
        yield client


def test_root_route_redirects_to_chat_stream(client):
    """测试根路由是否重定向到流式聊天端点"""
    response = client.get('/')
    assert response.status_code == 302
    assert response.location == '/chat_stream'


def test_new_chat_route_redirects_to_chat_stream(client):
    """测试新对话路由是否重定向到流式聊天端点"""
    response = client.get('/new')
    assert response.status_code == 302
    assert response.location == '/chat_stream'


def test_chat_stream_get_renders_chat_template(client):
    """测试流式聊天端点的GET请求是否渲染聊天模板"""
    response = client.get('/chat_stream')
    assert response.status_code == 200
    # 检查响应中是否包含聊天相关的元素
    assert '新闻对话'.encode('utf-8') in response.data
    assert b'chat-window' in response.data


def test_chat_stream_post_returns_streaming_response(client):
    """测试流式聊天端点的POST请求返回流式响应"""
    response = client.post('/chat_stream', data={
        'topic': '测试主题',
        'model_provider': 'deepseek'
    })
    # 应该返回流式响应
    assert response.status_code == 200
    assert response.content_type == 'text/plain; charset=utf-8'