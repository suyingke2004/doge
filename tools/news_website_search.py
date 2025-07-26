from dotenv import load_dotenv
from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

# 加载 .env 文件中的环境变量
load_dotenv()

# 定义一些常见的新闻网站RSS源
NEWS_RSS_FEEDS = {
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "Reuters": "https://www.reuters.com/news/rss.xml",  # Reuters实际可能不提供RSS
}

@tool("Search_News_Websites")
def search_news_websites(query: str) -> str:
    """
    当需要从常见新闻网站获取相关新闻时，使用此工具。
    输入应该是一个搜索关键词。
    返回包含新闻标题和URL的列表。
    此工具通过RSS源获取最新新闻，而不是直接搜索网站。
    """
    try:
        results = []
        
        # 对每个新闻网站的RSS源进行处理
        for site_name, rss_url in NEWS_RSS_FEEDS.items():
            try:
                # 添加小延迟避免过于频繁的请求
                time.sleep(0.5)
                
                # 发送请求获取RSS内容
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(rss_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # 解析RSS
                soup = BeautifulSoup(response.content, 'xml')
                
                # 提取条目
                entries = soup.find_all('item')[:5]  # 限制每个源最多5个条目
                
                # 筛选包含查询关键词的条目
                query_lower = query.lower()
                matched_entries = []
                for entry in entries:
                    title_elem = entry.find('title')
                    link_elem = entry.find('link')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text().strip()
                        link = link_elem.get_text().strip() if link_elem.get_text().strip() else link_elem.get('href', '')
                        
                        # 检查标题是否包含查询词
                        if query_lower in title.lower():
                            matched_entries.append({
                                'title': title,
                                'url': link
                            })
                
                # 添加匹配的条目到结果（每个网站最多3个）
                for entry in matched_entries[:3]:
                    results.append(f"来源: {site_name}\n标题: {entry['title']}\n链接: {entry['url']}\n")
                    
            except Exception as e:
                # 忽略单个源的错误，继续处理其他源
                continue
        
        # 如果没有找到匹配的结果，返回最新的几条新闻作为备选
        if not results:
            for site_name, rss_url in NEWS_RSS_FEEDS.items():
                try:
                    # 添加小延迟避免过于频繁的请求
                    time.sleep(0.5)
                    
                    # 发送请求获取RSS内容
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(rss_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    # 解析RSS
                    soup = BeautifulSoup(response.content, 'xml')
                    
                    # 提取条目
                    entries = soup.find_all('item')[:3]  # 限制每个源最多3个条目
                    
                    # 添加条目到结果
                    for entry in entries:
                        title_elem = entry.find('title')
                        link_elem = entry.find('link')
                        
                        if title_elem and link_elem:
                            title = title_elem.get_text().strip()
                            link = link_elem.get_text().strip() if link_elem.get_text().strip() else link_elem.get('href', '')
                            
                            results.append(f"来源: {site_name}\n标题: {title}\n链接: {link}\n")
                            
                except Exception as e:
                    # 忽略单个源的错误，继续处理其他源
                    continue
        
        # 如果仍然没有结果，返回提示信息
        if not results:
            return "未在常见新闻网站上找到相关结果。"
        
        # 组织结果
        result_str = f"关于'{query}'的新闻:\n\n"
        result_str += "\n".join(results[:10])  # 最多返回10个结果
        
        return result_str

    except Exception as e:
        return f"搜索新闻网站时出错: {e}"