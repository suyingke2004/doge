from flask import Flask, render_template, request
from agent import NewsletterAgent
import markdown

# 1. 创建 Flask 应用实例
app = Flask(__name__)

# 实例化我们的新闻通讯代理
# 在生产环境中，您可能希望以更有效的方式管理此实例
try:
    agent = NewsletterAgent()
except ValueError as e:
    print(f"启动错误: {e}")
    agent = None

# 2. 定义主页路由
@app.route('/')
def index():
    """渲染主页，显示主题输入表单"""
    return render_template('index.html')

# 3. 定义生成路由
@app.route('/generate', methods=['POST'])
def generate():
    """处理表单提交，调用代理生成新闻通讯"""
    if agent is None:
        # 如果代理未能初始化，显示错误信息
        return "错误：新闻代理未能启动，请检查您的 API 密钥配置。", 500

    # 从表单获取用户输入的主题
    topic = request.form.get('topic')
    if not topic:
        return "错误：请输入一个主题。", 400

    try:
        # 调用代理生成内容
        # 注意：这是一个耗时操作，在生产应用中应使用异步任务队列（如 Celery）
        content = agent.generate_newsletter(topic)
        
        # 将 Markdown 格式的输出转换为 HTML
        html_content = markdown.markdown(content)

        # 渲染结果页面
        return render_template('newsletter.html', topic=topic, content=html_content)
    
    except Exception as e:
        # 捕获代理执行过程中可能出现的任何错误
        print(f"生成新闻时出错: {e}")
        return f"生成新闻时发生错误: {e}", 500

# 启动应用的入口
if __name__ == '__main__':
    # 使用 debug=True 可以在开发时获得详细的错误信息和自动重载功能
    # 在生产环境中，应使用专业的 WSGI 服务器（如 Gunicorn）
    app.run(debug=True, port=5001)
