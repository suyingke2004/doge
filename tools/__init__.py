from dotenv import load_dotenv
from langchain.tools import tool
from newsapi import NewsApiClient
from newspaper import Article
import os

# 加载 .env 文件中的环境变量
load_dotenv()

class NewsTools:
    """封装了用于新闻获取和文章抓取的工具"""

    @tool("Search_News")
    def search_news(query: str) -> str:
        """
        当需要获取关于某个主题的最新新闻时，使用此工具。
        它会返回一个包含多篇新闻文章及其URL的列表。
        """
        # 添加对空查询的检查
        if not query or not query.strip():
            return "没有找到相关的新闻。"

        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            raise ValueError("未找到 NEWS_API_KEY，请确保 .env 文件中已配置。")

        newsapi = NewsApiClient(api_key=api_key)
        try:
            # 使用 get_everything 接口进行更广泛的搜索
            all_articles = newsapi.get_everything(
                q=query, 
                language='zh', 
                sort_by='relevancy' # 按相关性排序
            )
            articles = all_articles.get('articles', [])

            if not articles:
                return "没有找到相关的新闻。"

            result = ""
            for article in articles[:5]:  # 限制返回的文章数量
                result += f"标题: {article['title']}\n"
                result += f"链接: {article['url']}\n\n"

            return result

        except Exception as e:
            return f"获取新闻时出错: {e}"

    @tool("Scrape_Article_Content")
    def scrape_article_content(url: str) -> str:
        """
        当需要从给定的URL中提取文章的详细内容时，使用此工具。
        输入应该是一个有效的新闻文章链接。
        """
        try:
            article = Article(url)
            article.download()
            article.parse()

            # 为了结果的简洁性，我们只返回文章的核心文本
            return article.text

        except Exception as e:
            return f"抓取文章内容时出错: {e}"

# 实例化工具类，以便在 agent.py 中导入和使用
news_tools = NewsTools()
