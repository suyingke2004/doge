import pytest
from app import app


@pytest.fixture
def client():
    """创建一个测试客户端"""
    app.config['TESTING'] = True
    app.secret_key = 'test_secret_key'
    with app.test_client() as client:
        yield client


def test_root_route_renders_chat_template(client):
    """测试根路由是否渲染聊天模板"""
    response = client.get('/')
    assert response.status_code == 200
    # 检查响应中是否包含聊天相关的元素
    assert '新闻对话'.encode('utf-8') in response.data
    assert b'chat-window' in response.data


def test_new_chat_route_redirects_to_root(client):
    """测试新对话路由是否重定向到根路由"""
    response = client.get('/new')
    assert response.status_code == 302
    assert response.location == '/'


def test_chat_route_with_post_request(client):
    """测试聊天路由的POST请求"""
    response = client.post('/chat', data={
        'topic': '测试主题',
        'model_provider': 'deepseek'
    })
    # 应该重定向或返回聊天页面
    assert response.status_code == 200