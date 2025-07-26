from dotenv import load_dotenv
from langchain.tools import tool
import pdfkit
import os

# 加载 .env 文件中的环境变量
load_dotenv()

class PDFExportTool:
    """用于将内容导出为PDF的工具"""

    @tool("Export_To_PDF")
    def export_to_pdf(content: str, filename: str = "newsletter.pdf") -> str:
        """
        当需要将内容导出为PDF文件时，使用此工具。
        输入应该包含要导出的内容和可选的文件名。
        返回生成的PDF文件路径。
        """
        try:
            # 确保文件名以.pdf结尾
            if not filename.endswith(".pdf"):
                filename += ".pdf"
            
            # 创建HTML内容
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Newsletter</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 40px;
                        line-height: 1.6;
                    }}
                    h1 {{
                        color: #333;
                        border-bottom: 2px solid #333;
                        padding-bottom: 10px;
                    }}
                    h2 {{
                        color: #666;
                        margin-top: 30px;
                    }}
                    p {{
                        margin-bottom: 15px;
                    }}
                </style>
            </head>
            <body>
                <h1>Newsletter</h1>
                {content}
            </body>
            </html>
            """
            
            # 生成PDF文件
            pdfkit.from_string(html_content, filename)
            
            # 返回文件路径
            return f"PDF文件已生成: {filename}"
            
        except Exception as e:
            return f"导出PDF时出错: {e}"

# 实例化工具类，以便在 agent.py 中导入和使用
pdf_export_tool = PDFExportTool()