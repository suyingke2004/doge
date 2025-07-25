from dotenv import load_dotenv
from langchain.tools import tool
import os
import praw

# 加载 .env 文件中的环境变量
load_dotenv()

class RedditSearchTool:
    """用于从Reddit搜索相关主题的工具"""

    @tool("Search_Reddit")
    def search_reddit(query: str) -> str:
        """
        当需要获取关于某个主题的Reddit讨论时，使用此工具。
        它会返回一个包含最相关帖子及其URL的列表。
        """
        # 添加对空查询的检查
        if not query or not query.strip():
            return "没有找到相关的Reddit讨论。"

        # 从环境变量获取Reddit API凭据
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "news_agent by u/yourusername")

        if not client_id or not client_secret:
            raise ValueError("未找到REDDIT_CLIENT_ID或REDDIT_CLIENT_SECRET，请确保 .env 文件中已配置。")

        try:
            # 初始化Reddit实例
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            
            # 搜索相关帖子
            submissions = reddit.subreddit("all").search(query, limit=5, sort="relevance")
            
            result = ""
            for submission in submissions:
                result += f"标题: {submission.title}\n"
                result += f"链接: https://www.reddit.com{submission.permalink}\n"
                result += f"评分: {submission.score}\n\n"
                
            if not result:
                return "没有找到相关的Reddit讨论。"
                
            return result
            
        except Exception as e:
            return f"获取Reddit讨论时出错: {e}"

# 实例化工具类，以便在 agent.py 中导入和使用
reddit_search_tool = RedditSearchTool()