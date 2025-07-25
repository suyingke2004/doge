import unittest
import sys
import os

# 将项目根目录添加到 Python 路径中，以便导入模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools import news_tools

class TestNewsTools(unittest.TestCase):

    def test_search_news_success(self):
        """测试 search_news 函数是否能成功返回新闻"""
        query = "科技"
        result = news_tools.search_news(query)

        # 打印结果以供调试
        print(f"\n--- 测试查询: '{query}' ---")
        print(f"返回结果: {result[:200]}...") # 打印部分结果

        # 断言结果不是预期的失败消息
        self.assertNotIn("没有找到相关的新闻。", result)
        self.assertNotIn("获取新闻时出错", result)

        # 断言结果中包含预期的内容格式
        self.assertIn("标题:", result)
        self.assertIn("链接:", result)

    def test_search_news_empty_query(self):
        """测试当查询为空时 search_news 函数的行为"""
        query = ""
        result = news_tools.search_news(query)

        print(f"\n--- 测试空查询 ---")
        print(f"返回结果: {result}")

        # 对于空查询，API 可能会返回错误或空结果，我们期望它能优雅地处理
        # 在这种情况下，返回“没有找到相关的新闻。”是可接受的
        self.assertIn("没有找到相关的新闻。", result)

if __name__ == '__main__':
    unittest.main()
