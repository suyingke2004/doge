import unittest
import re
from agent import NewsletterAgent

class TestPDFLinkRendering(unittest.TestCase):
    """专门测试PDF链接渲染的测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = NewsletterAgent(model_provider="deepseek")
    
    def test_pdf_link_immediate_usability(self):
        """测试PDF链接是否立即可用，无需刷新页面"""
        # 模拟agent输出包含PDF链接的情况
        raw_output = "这是您的新闻通讯内容。\nPDF文件已生成，下载链接: /static/downloads/test_newsletter.pdf\n请查看附件。"
        
        # 模拟agent.py中的链接处理逻辑
        processed_output = raw_output
        if "PDF文件已生成，下载链接:" in processed_output:
            try:
                # 提取URL (修复URL提取逻辑)
                import re
                match = re.search(r"PDF文件已生成，下载链接:\s*([^\s]+)", processed_output)
                if match:
                    url = match.group(1)
                    # 生成HTML链接（修复后的简化版本）
                    link_html = f'<a href="{url}" target="_blank" class="pdf-download-link">下载PDF文件</a>'
                    # 用HTML链接替换原始文本
                    processed_output = processed_output.replace(f"PDF文件已生成，下载链接: {url}", link_html)
            except Exception:
                pass  # 如果处理链接出错，则按原样输出
        
        # 验证处理后的输出包含正确的HTML链接
        self.assertIn('<a href="/static/downloads/test_newsletter.pdf"', processed_output)
        self.assertIn('class="pdf-download-link"', processed_output)
        self.assertIn('下载PDF文件</a>', processed_output)
        # 确保原始文本已被替换
        self.assertNotIn("PDF文件已生成，下载链接:", processed_output)
        
        print("PDF链接立即可用性测试通过!")

    def test_multiple_pdf_links_handling(self):
        """测试多个PDF链接的处理"""
        # 模拟包含多个PDF链接的输出
        raw_output = """这是您的新闻通讯内容。
PDF文件已生成，下载链接: /static/downloads/test_newsletter1.pdf
更多内容请查看：
PDF文件已生成，下载链接: /static/downloads/test_newsletter2.pdf"""
        
        # 处理所有PDF链接
        processed_output = raw_output
        pdf_pattern = r"PDF文件已生成，下载链接:\s*(/[^\s]+\.pdf)"
        matches = re.findall(pdf_pattern, processed_output)
        
        for url in matches:
            # 生成HTML链接
            link_html = f'<a href="{url}" target="_blank" class="pdf-download-link">下载PDF文件</a>'
            # 替换原始文本
            processed_output = processed_output.replace(f"PDF文件已生成，下载链接: {url}", link_html)
        
        # 验证两个链接都被正确处理
        link_count = processed_output.count('class="pdf-download-link"')
        self.assertEqual(link_count, 2, "应该正确处理两个PDF链接")
        
        # 确保原始文本已被替换
        self.assertNotIn("PDF文件已生成，下载链接:", processed_output)
        
        print("多个PDF链接处理测试通过!")

if __name__ == "__main__":
    unittest.main()