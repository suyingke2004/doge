from flask import Flask, render_template, request, session, redirect, url_for, Response, stream_with_context
from agent import NewsletterAgent
from langchain_core.messages import AIMessage, HumanMessage
import markdown
import os
import asyncio
import json

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

# 5. 添加流式响应的路由
@app.route('/chat_stream', methods=['POST'])
def chat_stream():
    """处理用户的提问并以流式方式返回响应"""
    import asyncio

    def generate():
        # 从表单获取用户输入
        user_input = request.form.get('topic')
        
        # 打印调试信息
        print(f"Received form data: {dict(request.form)}")
        print(f"user_input: '{user_input}'")
        
        # 如果是新对话，获取模型选择并存入 session
        # 对于已存在的对话，从 session 中获取模型选择
        if 'chat_history' not in session:
            model_choice = request.form.get('model', 'openai')
            session['model_choice'] = model_choice
        else:
            model_choice = session.get('model_choice', 'openai')

        # 更宽松的输入验证 - 只有当输入为 None 时才报错
        if user_input is None:
            yield "错误：请输入一个主题或问题。"
            return
            
        # 如果输入是空字符串，也认为是无效输入
        if not user_input.strip():
            yield "错误：请输入一个主题或问题。"
            return

        # 从 session 中获取历史记录
        chat_history_raw = session.get('chat_history', [])
        # 将原始字典列表转换为 LangChain 消息对象列表
        chat_history_messages = [HumanMessage(**msg) if msg['type'] == 'human' else AIMessage(**msg) for msg in chat_history_raw]

        try:
            # 创建代理实例，并传入历史记录
            agent = NewsletterAgent(model_provider=model_choice, chat_history=chat_history_messages)
            
            # 使用流式方式调用代理生成内容
            full_response = ""
            
            # 创建一个新的事件循环来运行异步代码
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 定义一个内部异步函数来处理流式响应
            async def handle_stream():
                nonlocal full_response
                async for chunk in agent.generate_newsletter_stream(user_input):
                    # 发送每个块到客户端
                    yield chunk
                    full_response += chunk
                    
            # 运行异步生成器并逐个获取结果
            async_gen = handle_stream()
            while True:
                try:
                    chunk = loop.run_until_complete(async_gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
                except Exception as e:
                    print(f"Error in async generator: {e}")
                    break
                    
            loop.close()
                
            # 更新历史记录
            chat_history_raw.append({'type': 'human', 'content': user_input})
            chat_history_raw.append({'type': 'ai', 'content': full_response})
            session['chat_history'] = chat_history_raw

        except ValueError as e:
            print(f"配置错误: {e}")
            yield f"错误: {e}"
        except Exception as e:
            print(f"生成内容时出错: {e}")
            yield f"生成内容时发生错误: {e}"

    # 使用Flask的stream_with_context包装生成器
    return Response(stream_with_context(generate()), content_type='text/plain; charset=utf-8')

# 启动应用的入口
if __name__ == '__main__':
    app.run(debug=True, port=5001)
