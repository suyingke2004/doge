import unittest
from unittest.mock import patch, MagicMock
from tools import news_tools


class TestNewsTools(unittest.TestCase):
    """测试 NewsTools 类中的工具函数"""

    @patch('tools.NewsApiClient')
    def test_search_news_success(self, mock_newsapi_client):
        """测试 search_news 函数是否能成功返回新闻"""
        # 模拟 NewsApiClient 的行为
        mock_api_instance = MagicMock()
        mock_newsapi_client.return_value = mock_api_instance
        
        # 模拟 get_everything 的返回值
        mock_api_instance.get_everything.return_value = {
            'articles': [
                {
                    'title': 'Test News Article 1',
                    'url': 'https://example.com/article1'
                },
                {
                    'title': 'Test News Article 2',
                    'url': 'https://example.com/article2'
                }
            ]
        }
        
        query = "科技"
        result = news_tools.search_news(query)
        
        # 验证 NewsApiClient 被正确调用
        mock_newsapi_client.assert_called_once()
        mock_api_instance.get_everything.assert_called_once_with(
            q=query,
            language='zh',
            sort_by='relevancy'
        )
        
        # 断言结果包含预期的内容
        self.assertIn("Test News Article 1", result)
        self.assertIn("https://example.com/article1", result)
        self.assertIn("Test News Article 2", result)
        self.assertIn("https://example.com/article2", result)

    def test_search_news_empty_query(self):
        """测试 search_news 函数处理空查询的情况"""
        query = ""
        result = news_tools.search_news(query)
        
        # 断言返回适当的错误消息
        self.assertEqual(result, "没有找到相关的新闻。")
        
        # 测试只包含空格的查询
        query = "   "
        result = news_tools.search_news(query)
        self.assertEqual(result, "没有找到相关的新闻。")

    @patch('tools.Article')
    def test_scrape_article_content(self, mock_article_class):
        """测试 scrape_article_content 函数"""
        # 模拟 Article 的行为
        mock_article = MagicMock()
        mock_article_class.return_value = mock_article
        mock_article.text = "This is a test article content."
        
        url = "https://www.example.com/"
        result = news_tools.scrape_article_content(url)
        
        # 验证 Article 被正确调用
        mock_article_class.assert_called_once_with(url)
        mock_article.download.assert_called_once()
        mock_article.parse.assert_called_once()
        
        # 断言返回了正确的文章内容
        self.assertEqual(result, "This is a test article content.")


if __name__ == '__main__':
    unittest.main()
