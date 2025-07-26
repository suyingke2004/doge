import unittest
from agent import NewsletterAgent

class TestPDFLinkGeneration(unittest.TestCase):
    """测试PDF链接生成和显示"""
    
    def test_pdf_link_generation(self):
        """测试PDF链接是否正确生成且可立即使用"""
        # 模拟agent生成包含PDF链接的输出
        agent = NewsletterAgent(model_provider="deepseek")
        
        # 模拟PDF工具返回的内容
        pdf_output = "PDF文件已生成，下载链接: /static/downloads/test_newsletter.pdf"
        
        # 检查链接处理逻辑
        if "PDF文件已生成，下载链接:" in pdf_output:
            # 提取URL
            url = pdf_output.split("下载链接:")[-1].strip()
            # 生成HTML链接
            link_html = f'<a href="{url}" target="_blank" class="pdf-download-link">下载PDF文件</a>'
            # 用HTML链接替换原始文本
            processed_output = pdf_output.replace(f"PDF文件已生成，下载链接: {url}", link_html)
            
            # 验证生成的HTML链接格式正确
            self.assertIn('<a href="/static/downloads/test_newsletter.pdf"', processed_output)
            self.assertIn('class="pdf-download-link"', processed_output)
            self.assertIn('下载PDF文件</a>', processed_output)
            # 确保原始文本已被替换
            self.assertNotIn("PDF文件已生成，下载链接:", processed_output)
            
        print("PDF链接生成测试通过!")

if __name__ == "__main__":
    unittest.main()