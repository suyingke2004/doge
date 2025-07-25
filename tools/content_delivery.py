from dotenv import load_dotenv
from langchain.tools import tool
import sendgrid
from sendgrid.helpers.mail import Mail, Email, Content
import os
import pdfkit
import markdown
import tempfile

# 加载 .env 文件中的环境变量
load_dotenv()

class ContentDeliveryTool:
    """用于内容交付的工具，支持邮件发送和PDF导出"""

    @tool("Send_Email")
    def send_email(to_email: str, subject: str, content: str) -> str:
        """
        当需要将内容通过邮件发送给用户时，使用此工具。
        输入包括收件人邮箱、邮件主题和邮件内容。
        """
        # 检查必要参数
        if not to_email or not subject or not content:
            return "邮件发送失败：缺少必要参数（收件人、主题或内容）。"
        
        # 从环境变量获取SendGrid API密钥
        sg_api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("FROM_EMAIL")
        
        if not sg_api_key or not from_email:
            return "邮件发送失败：未配置SendGrid API密钥或发件人邮箱。"
        
        try:
            # 初始化SendGrid客户端
            sg = sendgrid.SendGridAPIClient(api_key=sg_api_key)
            
            # 创建邮件对象
            mail = Mail(
                from_email=Email(from_email),
                to_emails=to_email,
                subject=subject,
                plain_text_content=content
            )
            
            # 发送邮件
            response = sg.send(mail)
            
            if response.status_code == 202:
                return f"邮件已成功发送至 {to_email}"
            else:
                return f"邮件发送失败，状态码：{response.status_code}"
                
        except Exception as e:
            return f"邮件发送过程中出现错误：{e}"

    @tool("Export_PDF")
    def export_pdf(content: str, filename: str = "newsletter.pdf") -> str:
        """
        当需要将内容导出为PDF文件时，使用此工具。
        输入包括要导出的内容和文件名。
        返回PDF文件的路径。
        """
        # 检查必要参数
        if not content:
            return "PDF导出失败：内容不能为空。"
        
        try:
            # 将Markdown转换为HTML
            html_content = markdown.markdown(content)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                pdf_path = tmp_file.name
                
                # 使用pdfkit生成PDF
                # 注意：这需要系统中安装了wkhtmltopdf
                pdfkit.from_string(html_content, pdf_path)
                
                return f"PDF已成功导出至：{pdf_path}"
                
        except Exception as e:
            return f"PDF导出过程中出现错误：{e}"

# 实例化工具类，以便在 agent.py 中导入和使用
content_delivery_tool = ContentDeliveryTool()