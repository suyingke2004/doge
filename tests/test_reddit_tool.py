import os
import sys
import unittest
from unittest.mock import patch, MagicMock
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.reddit_search import RedditSearchTool

class TestRedditSearchTool(unittest.TestCase):
    """测试Reddit搜索工具"""

    @patch('tools.reddit_search.praw.Reddit')
    @patch('tools.reddit_search.os.getenv')
    def test_search_reddit_success(self, mock_getenv, mock_reddit):
        """测试成功搜索Reddit"""
        # 模拟环境变量
        def getenv_side_effect(key, default=None):
            env_vars = {
                "REDDIT_CLIENT_ID": "test_client_id",
                "REDDIT_CLIENT_SECRET": "test_client_secret",
                "REDDIT_USER_AGENT": "test_user_agent"
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect
        
        # 模拟Reddit API响应
        mock_submission = MagicMock()
        mock_submission.title = "Test Post Title"
        mock_submission.permalink = "/r/test/comments/123/test_post"
        mock_submission.score = 100
        
        mock_subreddit = MagicMock()
        mock_subreddit.search.return_value = [mock_submission]
        mock_reddit_instance = MagicMock()
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        mock_reddit.return_value = mock_reddit_instance
        
        # 执行测试
        tool = RedditSearchTool()
        result = tool.search_reddit.invoke({"query": "test query"})
        
        # 验证结果
        self.assertIn("Test Post Title", result)
        self.assertIn("https://www.reddit.com/r/test/comments/123/test_post", result)
        self.assertIn("评分: 100", result)
        
        # 验证调用
        mock_reddit.assert_called_once()
        mock_reddit_instance.subreddit.assert_called_once_with("all")
        mock_subreddit.search.assert_called_once_with("test query", limit=5, sort="relevance")

    @patch('tools.reddit_search.os.getenv')
    def test_search_reddit_empty_query(self, mock_getenv):
        """测试空查询"""
        # 模拟环境变量
        def getenv_side_effect(key, default=None):
            env_vars = {
                "REDDIT_CLIENT_ID": "test_client_id",
                "REDDIT_CLIENT_SECRET": "test_client_secret",
                "REDDIT_USER_AGENT": "test_user_agent"
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect
        
        tool = RedditSearchTool()
        result = tool.search_reddit.invoke({"query": ""})
        self.assertEqual(result, "没有找到相关的Reddit讨论。")
        
        result = tool.search_reddit.invoke({"query": "   "})
        self.assertEqual(result, "没有找到相关的Reddit讨论。")

    @patch('tools.reddit_search.os.getenv')
    def test_search_reddit_missing_credentials(self, mock_getenv):
        """测试缺少认证凭据"""
        # 模拟缺少认证凭据
        def getenv_side_effect(key, default=None):
            env_vars = {
                "REDDIT_CLIENT_ID": None,
                "REDDIT_CLIENT_SECRET": None,
                "REDDIT_USER_AGENT": "test_user_agent"
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect
        
        with self.assertRaises(ValueError) as context:
            tool = RedditSearchTool()
            tool.search_reddit.invoke({"query": "test query"})
            
        self.assertIn("未找到REDDIT_CLIENT_ID或REDDIT_CLIENT_SECRET", str(context.exception))

    @patch('tools.reddit_search.praw.Reddit')
    @patch('tools.reddit_search.os.getenv')
    def test_search_reddit_no_results(self, mock_getenv, mock_reddit):
        """测试没有搜索结果"""
        # 模拟环境变量
        def getenv_side_effect(key, default=None):
            env_vars = {
                "REDDIT_CLIENT_ID": "test_client_id",
                "REDDIT_CLIENT_SECRET": "test_client_secret",
                "REDDIT_USER_AGENT": "test_user_agent"
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect
        
        # 模拟没有搜索结果
        mock_subreddit = MagicMock()
        mock_subreddit.search.return_value = []
        mock_reddit_instance = MagicMock()
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        mock_reddit.return_value = mock_reddit_instance
        
        tool = RedditSearchTool()
        result = tool.search_reddit.invoke({"query": "nonexistent query"})
        self.assertEqual(result, "没有找到相关的Reddit讨论。")

    @patch('tools.reddit_search.os.getenv')
    def test_search_reddit_api_exception(self, mock_getenv):
        """测试Reddit API异常"""
        # 模拟环境变量
        def getenv_side_effect(key, default=None):
            env_vars = {
                "REDDIT_CLIENT_ID": "test_client_id",
                "REDDIT_CLIENT_SECRET": "test_client_secret",
                "REDDIT_USER_AGENT": "test_user_agent"
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect
        
        # 模拟API异常
        with patch('tools.reddit_search.praw.Reddit', side_effect=Exception("API Error")):
            tool = RedditSearchTool()
            result = tool.search_reddit.invoke({"query": "test query"})
            self.assertIn("获取Reddit讨论时出错", result)

if __name__ == '__main__':
    unittest.main()