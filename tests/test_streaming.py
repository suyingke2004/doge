import pytest
import asyncio
from agent import NewsletterAgent
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_generate_newsletter_stream():
    """测试NewsletterAgent的流式输出功能"""
    # 直接测试generate_newsletter_stream方法，而不测试整个初始化过程
    agent = NewsletterAgent.__new__(NewsletterAgent)  # 创建一个不调用__init__的对象
    
    # 手动设置必要的属性
    agent.agent_executor = AsyncMock()
    agent.chat_history = []  # 添加缺失的chat_history属性
    
    # 模拟astream方法返回一个异步生成器
    async def mock_astream(input_data):
        yield {"output": "这是"}
        yield {"output": "流式"}
        yield {"output": "输出"}
        yield {"output": "的测试"}
    
    agent.agent_executor.astream = mock_astream
    
    # 收集流式输出
    chunks = []
    async for chunk in agent.generate_newsletter_stream("测试主题"):
        chunks.append(chunk)
    
    # 验证输出
    assert len(chunks) == 4
    assert "".join(chunks) == "这是流式输出的测试"

def test_method_exists():
    """测试NewsletterAgent是否具有generate_newsletter_stream方法"""
    # 检查方法是否存在
    assert hasattr(NewsletterAgent, 'generate_newsletter_stream')
    
    # 检查方法是否是异步生成器函数
    import inspect
    assert inspect.isasyncgenfunction(NewsletterAgent.generate_newsletter_stream)