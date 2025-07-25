from dotenv import load_dotenv
from langchain.tools import tool
import feedparser
import os

# 加载 .env 文件中的环境变量
load_dotenv()

class RSSFeedTool:
    """用于从RSS订阅源获取内容的工具"""

    @tool("Search_RSS_Feeds")
    def search_rss_feeds(feed_url: str) -> str:
        """
        当需要从RSS订阅源获取最新内容时，使用此工具。
        输入应该是一个有效的RSS订阅源URL。
        返回最新的几篇文章标题和链接。
        """
        # 添加对空URL的检查
        if not feed_url or not feed_url.strip():
            return "RSS订阅源URL不能为空。"

        try:
            # 解析RSS订阅源
            feed = feedparser.parse(feed_url)
            
            # 检查是否解析成功
            if feed.bozo and isinstance(feed.bozo_exception, Exception):
                return f"解析RSS订阅源时出错: {feed.bozo_exception}"
            
            # 检查是否有条目
            if not feed.entries:
                return "RSS订阅源中没有找到条目。"
            
            # 构建结果
            result = f"RSS订阅源: {feed.feed.title}\n"
            result += f"链接: {feed.feed.link}\n\n"
            
            # 获取最新的5篇文章
            for entry in feed.entries[:5]:
                result += f"标题: {entry.title}\n"
                result += f"链接: {entry.link}\n"
                # 如果有发布日期，也添加进去
                if hasattr(entry, 'published'):
                    result += f"发布日期: {entry.published}\n"
                result += "\n"
                
            return result
            
        except Exception as e:
            return f"获取RSS订阅源内容时出错: {e}"

# 实例化工具类，以便在 agent.py 中导入和使用
rss_feed_tool = RSSFeedTool()