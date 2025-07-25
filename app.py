from flask import Flask, render_template, request, session, redirect, url_for
from agent import NewsletterAgent
from langchain_core.messages import AIMessage, HumanMessage
import markdown
import os

# 1. 创建 Flask 应用实例
app = Flask(__name__)
# 设置一个密钥，以便使用 session
# 在生产环境中，应使用更安全的方式管理密钥，例如环境变量
app.secret_key = os.urandom(24)

# 2. 定义主页路由
@app.route('/')
def index():
    """渲染主页，提供开始新对话的选项"""
    return render_template('index.html')

# 3. 定义开始新对话的路由
@app.route('/new')
def new_chat():
    """清除 session 中的聊天记录，开始一个新对话"""
    session.pop('chat_history', None)
    session.pop('model_choice', None)
    return redirect(url_for('index'))

# 4. 定义生成路由，现在也处理后续的聊天
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """处理用户的首次提问和后续追问"""
    if request.method == 'POST':
        # 从表单获取用户输入
        user_input = request.form.get('topic')
        
        # 如果是新对话，获取模型选择并存入 session
        if 'chat_history' not in session:
            model_choice = request.form.get('model', 'openai')
            session['model_choice'] = model_choice
            session['chat_history'] = []
        else:
            # 对于已存在的对话，从 session 中获取模型选择
            model_choice = session['model_choice']

        if not user_input:
            return "错误：请输入一个主题或问题。", 400

        # 从 session 中获取历史记录
        chat_history_raw = session.get('chat_history', [])
        # 将原始字典列表转换为 LangChain 消息对象列表
        chat_history_messages = [HumanMessage(**msg) if msg['type'] == 'human' else AIMessage(**msg) for msg in chat_history_raw]

        try:
            # 创建代理实例，并传入历史记录
            agent = NewsletterAgent(model_provider=model_choice, chat_history=chat_history_messages)
            
            # 调用代理生成内容
            ai_response = agent.generate_newsletter(user_input)
            
            # 更新历史记录
            chat_history_raw.append({'type': 'human', 'content': user_input})
            chat_history_raw.append({'type': 'ai', 'content': ai_response})
            session['chat_history'] = chat_history_raw

        except ValueError as e:
            print(f"配置错误: {e}")
            return f"错误: {e}", 500
        except Exception as e:
            print(f"生成内容时出错: {e}")
            return f"生成内容时发生错误: {e}", 500

    # 准备用于渲染模板的数据
    chat_history_to_render = session.get('chat_history', [])
    # 将 Markdown 转换为 HTML
    for message in chat_history_to_render:
        if message['type'] == 'ai':
            message['content_html'] = markdown.markdown(message['content'])

    return render_template('chat.html', chat_history=chat_history_to_render)

# 启动应用的入口
if __name__ == '__main__':
    app.run(debug=True, port=5001)
