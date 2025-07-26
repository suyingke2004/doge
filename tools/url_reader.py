from dotenv import load_dotenv
from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
import re

# 加载 .env 文件中的环境变量
load_dotenv()

class URLReaderTool:
    """用于读取和提取任意URL内容的工具"""

    @tool("Read_URL_Content")
    def read_url_content(url: str) -> str:
        """
        当需要从给定的URL中提取网页内容时，使用此工具。
        输入应该是一个有效的网页链接。
        返回网页的标题和主要内容文本。
        """
        try:
            # 发送GET请求获取网页内容
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "无标题"
            
            # 移除脚本和样式元素
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 提取文本内容
            text = soup.get_text()
            
            # 清理文本：移除多余的空白字符
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # 限制返回的文本长度，避免过长
            if len(text) > 3000:
                text = text[:3000] + "... (内容已截断)"
            
            # 组织结果
            result = f"网页标题: {title_text}\n\n"
            result += f"URL: {url}\n\n"
            result += f"内容:\n{text}"
            
            return result

        except requests.RequestException as e:
            return f"获取URL内容时出错: 网络请求失败 - {e}"
        except Exception as e:
            return f"处理URL内容时出错: {e}"

# 实例化工具类，以便在 agent.py 中导入和使用
url_reader_tool = URLReaderTool()