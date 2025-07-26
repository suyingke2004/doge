#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Search_News_Websites和Scrape_Article_Content工具的联动使用
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.news_website_search import search_news_websites
from tools import news_tools

def test_news_website_and_scraping_linkage():
    """测试新闻网站搜索和文章抓取工具的联动使用"""
    print("测试Search_News_Websites和Scrape_Article_Content工具的联动使用...")
    
    try:
        # 1. 首先使用Search_News_Websites搜索相关新闻
        print("\n1. 搜索人工智能相关的新闻...")
        search_result = search_news_websites.invoke({"query": "artificial intelligence"})
        print("搜索结果:")
        print(search_result)
        
        # 从搜索结果中提取一个URL进行测试
        # 在实际使用中，这会由AI代理自动完成
        if "链接:" in search_result:
            # 简单提取第一个链接
            lines = search_result.split('\n')
            url = None
            for line in lines:
                if line.startswith("链接:"):
                    url = line.replace("链接:", "").strip()
                    break
            
            if url:
                print(f"\n2. 使用Scrape_Article_Content抓取文章内容...")
                print(f"抓取URL: {url}")
                # 使用Scrape_Article_Content抓取文章内容
                scrape_result = news_tools.scrape_article_content.invoke({"url": url})
                print("文章内容预览:")
                # 只显示前500个字符避免输出过长
                print(scrape_result[:500] + ("..." if len(scrape_result) > 500 else ""))
            else:
                print("未找到有效的新闻链接")
        else:
            print("搜索结果中未包含链接信息")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_news_website_and_scraping_linkage()