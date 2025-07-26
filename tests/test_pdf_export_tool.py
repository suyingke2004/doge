import unittest
import os
import tempfile
from tools.pdf_export import pdf_export_tool

class TestPDFExportTool(unittest.TestCase):
    """测试PDF导出工具的功能"""
    
    def test_pdf_generation_and_link_format(self):
        """测试PDF生成和链接格式"""
        # 准备测试内容
        content = "<h1>测试标题</h1><p>这是测试段落内容。</p>"
        filename = "test_document.pdf"
        
        # 在临时目录中执行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            # 保存当前工作目录
            original_cwd = os.getcwd()
            try:
                # 切换到临时目录
                os.chdir(temp_dir)
                
                # 创建static/downloads目录结构
                os.makedirs(os.path.join("static", "downloads"), exist_ok=True)
                
                # 直接调用工具的export_to_pdf方法
                result = pdf_export_tool.export_to_pdf(content, filename)
                
                # 验证返回结果格式
                self.assertIn("PDF文件已生成，下载链接:", result)
                self.assertIn("/static/downloads/", result)
                self.assertIn(".pdf", result)
                
                # 验证文件是否实际创建
                # 从结果中提取文件路径
                import re
                match = re.search(r"下载链接: (/[^\s]+)", result)
                self.assertIsNotNone(match, "应该能够提取下载链接")
                
                # 检查文件是否存在
                file_path = match.group(1)[1:]  # 移除开头的 "/"
                self.assertTrue(os.path.exists(file_path), f"PDF文件应该存在: {file_path}")
                
                # 验证文件大小
                file_size = os.path.getsize(file_path)
                self.assertGreater(file_size, 0, "PDF文件大小应该大于0")
                
            finally:
                # 恢复原始工作目录
                os.chdir(original_cwd)
        
        print("PDF生成和链接格式测试通过!")

if __name__ == "__main__":
    unittest.main()