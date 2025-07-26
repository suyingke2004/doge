import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.pdf_export import PDFExportTool

class TestPDFExportIntegration(unittest.TestCase):
    """测试PDF导出工具的完整流程"""
    
    def setUp(self):
        """测试前准备"""
        self.pdf_tool = PDFExportTool()
        
    def test_pdf_export_and_link_generation(self):
        """测试PDF导出和链接生成"""
        # 创建测试内容
        test_content = "<h1>测试新闻通讯</h1><p>这是测试内容</p>"
        test_filename = "test_newsletter.pdf"
        
        # 使用临时目录进行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            # 修补os.path.join以使用临时目录
            with patch('tools.pdf_export.os.path.join') as mock_join:
                # 设置mock返回临时目录
                mock_join.side_effect = lambda *args: os.path.join(temp_dir, *args[1:]) if args[0] == "static" else os.path.join(*args)
                
                # 执行PDF导出
                result = self.pdf_tool.export_to_pdf(test_content, test_filename)
                
                # 验证结果
                self.assertIn("PDF文件已生成，下载链接:", result)
                self.assertIn(".pdf", result)
                
                # 验证文件是否创建
                # 从结果中提取文件名
                import re
                match = re.search(r"下载链接: (/static/downloads/[^ ]+)", result)
                self.assertIsNotNone(match, "应该能够提取下载链接")
                
                # 验证链接格式
                link = match.group(1)
                self.assertTrue(link.endswith('.pdf'), "链接应该指向PDF文件")
                
        print("PDF导出和链接生成集成测试通过!")

if __name__ == "__main__":
    unittest.main()