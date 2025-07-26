from flask import Flask, render_template, request, session, redirect, url_for, Response, stream_with_context
from agent import NewsletterAgent
from langchain_core.messages import AIMessage, HumanMessage
import markdown
import os
import asyncio
import json
import sys

# 1. 创建 Flask 应用实例
app = Flask(__name__)
# 设置一个密钥，以便使用 session
# 在生产环境中，应使用更安全的方式管理密钥，例如环境变量
app.secret_key = os.urandom(24)

# 处理打包后的资源路径
def resource_path(relative_path):
    """获取资源的绝对路径，用于PyInstaller打包后的资源访问"""
    try:
        # PyInstaller创建临时文件夹并存储路径到 _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 配置模板和静态文件路径
app.template_folder = resource_path('templates')
app.static_folder = resource_path('static')

# 2. 定义主页路由（重定向到流式端点）
@app.route('/')
def index():
    """重定向到流式聊天端点"""
    return redirect(url_for('chat_stream'))

# 3. 定义开始新对话的路由
@app.route('/new')
def new_chat():
    """清除 session 中的聊天记录，开始一个新对话"""
    session.pop('chat_history', None)
    session.pop('model_provider', None)
    session.pop('model_name', None)
    session.pop('maxiter', None)
    return redirect(url_for('chat_stream'))

# 3.5 定义调试聊天路由
@app.route('/debug_chat')
def debug_chat():
    """调试聊天页面"""
    # 从 session 中获取聊天历史记录
    chat_history_raw = session.get('chat_history', [])
    # 将原始字典列表转换为包含HTML的字典列表
    chat_history_with_html = []
    for msg in chat_history_raw:
        # 创建消息副本并添加HTML版本的内容
        msg_with_html = msg.copy()
        if msg['type'] == 'ai':
            # 将AI消息的Markdown内容转换为HTML
            msg_with_html['content_html'] = markdown.markdown(msg['content'])
        else:
            # 对于用户消息，直接显示文本
            msg_with_html['content_html'] = msg['content']
        chat_history_with_html.append(msg_with_html)
    
    # 渲染带调试信息的聊天模板
    return render_template('debug_chat.html', chat_history=chat_history_with_html)

# 3.6 定义简化测试路由
@app.route('/simple_test')
def simple_test():
    """简化测试页面"""
    return render_template('simple_test.html')

# 3.7 定义状态指示器调试路由
@app.route('/debug_status')
def debug_status():
    """状态指示器调试页面"""
    return render_template('debug_status.html')

# 3.8 定义PDF下载路由
@app.route('/download/<filename>')
def download_pdf(filename):
    """提供PDF文件下载"""
    try:
        # 确保文件名是安全的
        from werkzeug.utils import secure_filename
        filename = secure_filename(filename)
        
        # 构建文件路径
        downloads_dir = os.path.join(app.static_folder, 'downloads')
        file_path = os.path.join(downloads_dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return "文件未找到", 404
            
        # 检查文件扩展名是否为PDF
        if not filename.endswith('.pdf'):
            return "只能下载PDF文件", 400
            
        # 使用Flask的send_from_directory提供文件下载
        from flask import send_from_directory
        return send_from_directory(
            directory=downloads_dir,
            path=filename,
            as_attachment=True  # 强制下载而不是在浏览器中打开
        )
    except Exception as e:
        return f"下载文件时出错: {str(e)}", 500

# 4. 定义流式生成路由，处理所有对话
@app.route('/chat_stream', methods=['GET', 'POST'])
def chat_stream():
    """处理用户的提问并以流式方式返回响应"""
    import asyncio

    # 如果是 GET 请求，渲染聊天界面
    if request.method == 'GET':
        # 准备用于渲染模板的数据
        chat_history_to_render = session.get('chat_history', [])
        # 将 Markdown 转换为 HTML
        for message in chat_history_to_render:
            if message['type'] == 'ai':
                message['content_html'] = markdown.markdown(message['content'])
                
        return render_template('chat.html', chat_history=chat_history_to_render)

    # 如果是 POST 请求，处理流式响应
    def generate():
        # 从表单获取用户输入
        user_input = request.form.get('topic')
        
        # 打印调试信息
        print(f"Received form data: {dict(request.form)}")
        print(f"user_input: '{user_input}'")
        
        # 如果是新对话，获取模型选择、语言和 maxiter 参数并存入 session
        # 对于已存在的对话，从 session 中获取模型选择和语言
        if 'chat_history' not in session:
            model_provider = request.form.get('model_provider', 'deepseek')
            model_name = request.form.get('model_name', '').strip()
            # 如果没有提供模型名称，则使用空字符串表示使用默认模型
            model_name = model_name if model_name else None
            # 获取 maxiter 参数，默认为 128
            maxiter = int(request.form.get('maxiter', 128))
            # 获取语言参数，默认为中文
            language = request.form.get('language', 'zh')
            
            session['model_provider'] = model_provider
            session['model_name'] = model_name
            session['maxiter'] = maxiter
            session['language'] = language
        else:
            model_provider = session.get('model_provider', 'deepseek')
            model_name = session.get('model_name', None)
            maxiter = session.get('maxiter', 128)
            language = session.get('language', 'zh')

        # 更宽松的输入验证 - 只有当输入为 None 时才报错
        if user_input is None:
            yield "{\"type\": \"output\", \"content\": \"错误: 请输入一个主题或问题.\"}\n"
            return
            
        # 如果输入是空字符串，也认为是无效输入
        if not user_input.strip():
            yield "{\"type\": \"output\", \"content\": \"错误: 请输入一个主题或问题.\"}\n"
            return

        # 从 session 中获取历史记录
        chat_history_raw = session.get('chat_history', [])
        # 将原始字典列表转换为 LangChain 消息对象列表
        chat_history_messages = [HumanMessage(**msg) if msg['type'] == 'human' else AIMessage(**msg) for msg in chat_history_raw]

        try:
            # 创建代理实例，并传入历史记录、 maxiter 和 language 参数
            agent = NewsletterAgent(
                model_provider=model_provider, 
                model_name=model_name, 
                chat_history=chat_history_messages,
                max_iterations=maxiter,
                language=language
            )
            
            # 使用流式方式调用代理生成内容
            full_response = ""
            
            # 使用 asyncio.run 来处理异步代码（推荐方法）
            import asyncio
            import json
            
            # 定义一个异步生成器函数
            async def async_generate():
                nonlocal full_response
                async for chunk in agent.generate_newsletter_stream(user_input):
                    # 累积响应内容
                    if chunk.get("type") == "output":
                        full_response += chunk.get("content", "")
                    # 立即发送每个块到客户端
                    yield json.dumps(chunk, ensure_ascii=False) + "\n"
            
            # 在新事件循环中运行异步代码
            async def run_async_code():
                async for item in async_generate():
                    yield item
                    
            # 同步包装异步生成器
            import threading
            from queue import Queue, Empty
            
            # 创建队列用于传递数据
            q = Queue()
            
            # 定义在后台线程中运行的函数
            def run_async_generator():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    async_gen = run_async_code()
                    while True:
                        try:
                            item = loop.run_until_complete(async_gen.__anext__())
                            q.put(item)
                        except StopAsyncIteration:
                            break
                except Exception as e:
                    q.put(e)
                finally:
                    q.put(None)  # 信号表示完成
                    loop.close()
            
            # 启动后台线程
            thread = threading.Thread(target=run_async_generator)
            thread.start()
            
            # 从队列中获取数据并发送给客户端
            while True:
                try:
                    item = q.get(timeout=1)  # 1秒超时
                    if item is None:  # 完成信号
                        break
                    if isinstance(item, Exception):
                        raise item
                    yield item
                except Empty:
                    # 检查线程是否还活着
                    if not thread.is_alive():
                        break
                    continue
            
            # 等待线程完成
            thread.join()
                    
            # 更新历史记录
            chat_history_raw.append({'type': 'human', 'content': user_input})
            chat_history_raw.append({'type': 'ai', 'content': full_response})
            session['chat_history'] = chat_history_raw

        except ValueError as e:
            print(f"配置错误: {e}")
            yield json.dumps({"type": "output", "content": f"错误: {e}"}, ensure_ascii=False) + "\n"
        except Exception as e:
            print(f"生成内容时出错: {e}")
            yield json.dumps({"type": "output", "content": f"生成内容时发生错误: {e}"}, ensure_ascii=False) + "\n"

    # 使用Flask的stream_with_context包装生成器
    return Response(stream_with_context(generate()), content_type='text/plain; charset=utf-8')



# 启动应用的入口
if __name__ == '__main__':
    app.run(debug=True, port=5001)
