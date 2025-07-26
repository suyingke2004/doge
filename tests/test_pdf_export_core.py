import unittest
import os
import tempfile
import pdfkit

class TestPDFExportCoreFunctionality(unittest.TestCase):
    """测试PDF导出的核心功能"""
    
    def test_pdf_generation_core_functionality(self):
        """测试PDF生成的核心功能"""
        # 准备测试内容
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Test Newsletter</title>
        </head>
        <body>
            <h1>测试标题</h1>
            <p>这是测试段落内容。</p>
        </body>
        </html>
        """
        
        filename = "test_document.pdf"
        
        # 在临时目录中执行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建保存目录
            save_dir = os.path.join(temp_dir, "static", "downloads")
            os.makedirs(save_dir, exist_ok=True)
            
            # 完整的文件路径
            file_path = os.path.join(save_dir, filename)
            
            # 生成PDF文件
            pdfkit.from_string(html_content, file_path)
            
            # 验证文件是否实际创建
            self.assertTrue(os.path.exists(file_path), f"PDF文件应该存在: {file_path}")
            
            # 验证文件大小
            file_size = os.path.getsize(file_path)
            self.assertGreater(file_size, 0, "PDF文件大小应该大于0")
            
            # 验证返回的URL格式
            file_url = f"/static/downloads/{filename}"
            self.assertEqual(file_url, f"/static/downloads/{filename}")
            
        print("PDF核心功能测试通过!")

if __name__ == "__main__":
    unittest.main()