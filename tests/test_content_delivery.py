import os
import sys
import unittest
from unittest.mock import patch, MagicMock
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.content_delivery import ContentDeliveryTool

class TestContentDeliveryTool(unittest.TestCase):
    """测试内容交付工具"""

    def test_send_email_missing_parameters(self):
        """测试发送邮件时缺少参数"""
        tool = ContentDeliveryTool()
        
        # 测试缺少收件人
        result = tool.send_email.invoke({"to_email": "", "subject": "Test", "content": "Test content"})
        self.assertIn("邮件发送失败：缺少必要参数", result)
        
        # 测试缺少主题
        result = tool.send_email.invoke({"to_email": "test@example.com", "subject": "", "content": "Test content"})
        self.assertIn("邮件发送失败：缺少必要参数", result)
        
        # 测试缺少内容
        result = tool.send_email.invoke({"to_email": "test@example.com", "subject": "Test", "content": ""})
        self.assertIn("邮件发送失败：缺少必要参数", result)

    @patch('tools.content_delivery.os.getenv')
    def test_send_email_missing_credentials(self, mock_getenv):
        """测试发送邮件时缺少认证凭据"""
        # 模拟缺少认证凭据
        def getenv_side_effect(key, default=None):
            env_vars = {
                "SENDGRID_API_KEY": None,
                "FROM_EMAIL": None
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect
        
        tool = ContentDeliveryTool()
        result = tool.send_email.invoke({
            "to_email": "test@example.com", 
            "subject": "Test", 
            "content": "Test content"
        })
        self.assertIn("邮件发送失败：未配置SendGrid API密钥或发件人邮箱", result)

    @patch('tools.content_delivery.sendgrid.SendGridAPIClient')
    @patch('tools.content_delivery.os.getenv')
    def test_send_email_success(self, mock_getenv, mock_sendgrid):
        """测试成功发送邮件"""
        # 模拟环境变量
        def getenv_side_effect(key, default=None):
            env_vars = {
                "SENDGRID_API_KEY": "SG.test_api_key",
                "FROM_EMAIL": "sender@example.com"
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect
        
        # 模拟SendGrid响应
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_sendgrid_instance = MagicMock()
        mock_sendgrid_instance.send.return_value = mock_response
        mock_sendgrid.return_value = mock_sendgrid_instance
        
        tool = ContentDeliveryTool()
        result = tool.send_email.invoke({
            "to_email": "test@example.com", 
            "subject": "Test", 
            "content": "Test content"
        })
        self.assertIn("邮件已成功发送至 test@example.com", result)

    @patch('tools.content_delivery.sendgrid.SendGridAPIClient')
    @patch('tools.content_delivery.os.getenv')
    def test_send_email_failure(self, mock_getenv, mock_sendgrid):
        """测试发送邮件失败"""
        # 模拟环境变量
        def getenv_side_effect(key, default=None):
            env_vars = {
                "SENDGRID_API_KEY": "SG.test_api_key",
                "FROM_EMAIL": "sender@example.com"
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect
        
        # 模拟SendGrid响应
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_sendgrid_instance = MagicMock()
        mock_sendgrid_instance.send.return_value = mock_response
        mock_sendgrid.return_value = mock_sendgrid_instance
        
        tool = ContentDeliveryTool()
        result = tool.send_email.invoke({
            "to_email": "test@example.com", 
            "subject": "Test", 
            "content": "Test content"
        })
        self.assertIn("邮件发送失败，状态码：400", result)

    def test_export_pdf_empty_content(self):
        """测试导出PDF时内容为空"""
        tool = ContentDeliveryTool()
        result = tool.export_pdf.invoke({"content": ""})
        self.assertIn("PDF导出失败：内容不能为空", result)

    @patch('tools.content_delivery.pdfkit.from_string')
    @patch('tools.content_delivery.tempfile.NamedTemporaryFile')
    def test_export_pdf_success(self, mock_tempfile, mock_pdfkit):
        """测试成功导出PDF"""
        # 模拟临时文件
        mock_tempfile_instance = MagicMock()
        mock_tempfile_instance.name = "/tmp/test.pdf"
        mock_tempfile.return_value.__enter__.return_value = mock_tempfile_instance
        mock_tempfile.return_value.__exit__.return_value = None
        
        tool = ContentDeliveryTool()
        result = tool.export_pdf.invoke({"content": "# Test\n\nThis is a test.", "filename": "test.pdf"})
        self.assertIn("PDF已成功导出至：/tmp/test.pdf", result)

if __name__ == '__main__':
    unittest.main()