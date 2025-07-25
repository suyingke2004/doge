import os
import sys
import unittest
from unittest.mock import patch, MagicMock
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.rss_feed import RSSFeedTool

class TestRSSFeedTool(unittest.TestCase):
    """测试RSS订阅源工具"""

    def test_search_rss_feeds_empty_url(self):
        """测试空URL"""
        tool = RSSFeedTool()
        result = tool.search_rss_feeds.invoke({"feed_url": ""})
        self.assertEqual(result, "RSS订阅源URL不能为空。")
        
        result = tool.search_rss_feeds.invoke({"feed_url": "   "})
        self.assertEqual(result, "RSS订阅源URL不能为空。")

    @patch('tools.rss_feed.feedparser.parse')
    def test_search_rss_feeds_parse_error(self, mock_parse):
        """测试解析错误"""
        # 模拟解析错误
        mock_parse.return_value = MagicMock(
            bozo=True,
            bozo_exception=Exception("解析错误"),
            entries=[]
        )
        
        tool = RSSFeedTool()
        result = tool.search_rss_feeds.invoke({"feed_url": "http://example.com/rss"})
        self.assertIn("解析RSS订阅源时出错", result)

    @patch('tools.rss_feed.feedparser.parse')
    def test_search_rss_feeds_no_entries(self, mock_parse):
        """测试没有条目"""
        # 模拟没有条目
        mock_parse.return_value = MagicMock(
            bozo=False,
            entries=[],
            feed=MagicMock(title="Test Feed", link="http://example.com")
        )
        
        tool = RSSFeedTool()
        result = tool.search_rss_feeds.invoke({"feed_url": "http://example.com/rss"})
        self.assertEqual(result, "RSS订阅源中没有找到条目。")

    @patch('tools.rss_feed.feedparser.parse')
    def test_search_rss_feeds_success(self, mock_parse):
        """测试成功获取RSS条目"""
        # 模拟成功的RSS解析
        mock_entry1 = MagicMock(
            title="Test Article 1",
            link="http://example.com/article1",
            published="2023-01-01T00:00:00Z"
        )
        mock_entry2 = MagicMock(
            title="Test Article 2",
            link="http://example.com/article2"
        )
        
        mock_parse.return_value = MagicMock(
            bozo=False,
            entries=[mock_entry1, mock_entry2],
            feed=MagicMock(
                title="Test Feed",
                link="http://example.com"
            )
        )
        
        tool = RSSFeedTool()
        result = tool.search_rss_feeds.invoke({"feed_url": "http://example.com/rss"})
        
        # 验证结果
        self.assertIn("Test Feed", result)
        self.assertIn("http://example.com", result)
        self.assertIn("Test Article 1", result)
        self.assertIn("http://example.com/article1", result)
        self.assertIn("2023-01-01T00:00:00Z", result)
        self.assertIn("Test Article 2", result)
        self.assertIn("http://example.com/article2", result)

    @patch('tools.rss_feed.feedparser.parse')
    def test_search_rss_feeds_general_exception(self, mock_parse):
        """测试一般异常"""
        # 模拟一般异常
        mock_parse.side_effect = Exception("网络错误")
        
        tool = RSSFeedTool()
        result = tool.search_rss_feeds.invoke({"feed_url": "http://example.com/rss"})
        self.assertIn("获取RSS订阅源内容时出错", result)

if __name__ == '__main__':
    unittest.main()