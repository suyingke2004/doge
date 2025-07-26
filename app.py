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
    def generate_with_session():
        from sqlalchemy.orm import sessionmaker
        from models import ChatSession, ChatMessage
        from sqlalchemy import create_engine
        import uuid

        # 数据库设置
        DATABASE_URL = "sqlite:///chat_history.db"
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()

        user_input = request.form.get('topic')
        session_id = session.get('session_id')

        # 如果没有会话ID，则创建新会话
        if not session_id:
            new_session = ChatSession(title=user_input[:200]) # 使用用户输入作为标题
            db_session.add(new_session)
            db_session.commit()
            session_id = new_session.id
            session['session_id'] = session_id

        # 保存用户消息
        user_message = ChatMessage(session_id=session_id, message_type='human', content=user_input)
        db_session.add(user_message)
        db_session.commit()

        # 从 session 中获取历史记录
        chat_history_raw = session.get('chat_history', [])
        chat_history_raw.append({'type': 'human', 'content': user_input})
        session['chat_history'] = chat_history_raw

        # 将原始字典列表转换为 LangChain 消息对象列表
        chat_history_messages = [HumanMessage(**msg) if msg['type'] == 'human' else AIMessage(**msg) for msg in chat_history_raw]

        try:
            model_provider = session.get('model_provider', 'deepseek')
            model_name = session.get('model_name', None)
            maxiter = session.get('maxiter', 128)
            language = session.get('language', 'zh')

            agent = NewsletterAgent(
                model_provider=model_provider, 
                model_name=model_name, 
                chat_history=chat_history_messages,
                max_iterations=maxiter,
                language=language
            )
            
            full_response = ""
            
            async def async_generate():
                nonlocal full_response
                async for chunk in agent.generate_newsletter_stream(user_input):
                    if chunk.get("type") == "output":
                        full_response += chunk.get("content", "")
                    yield json.dumps(chunk, ensure_ascii=False) + "\n"
            
            # (The rest of the streaming logic remains the same)
            import threading
            from queue import Queue, Empty
            
            q = Queue()
            
            def run_async_generator():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    async_gen = async_generate()
                    while True:
                        try:
                            item = loop.run_until_complete(async_gen.__anext__())
                            q.put(item)
                        except StopAsyncIteration:
                            break
                except Exception as e:
                    q.put(e)
                finally:
                    q.put(None)
                    loop.close()
            
            thread = threading.Thread(target=run_async_generator)
            thread.start()
            
            while True:
                try:
                    item = q.get(timeout=1)
                    if item is None:
                        break
                    if isinstance(item, Exception):
                        raise item
                    yield item
                except Empty:
                    if not thread.is_alive():
                        break
                    continue
            
            thread.join()

            # 保存AI消息
            ai_message = ChatMessage(session_id=session_id, message_type='ai', content=full_response)
            db_session.add(ai_message)
            db_session.commit()

            chat_history_raw.append({'type': 'ai', 'content': full_response})
            session['chat_history'] = chat_history_raw

        except Exception as e:
            print(f"生成内容时出错: {e}")
            yield json.dumps({"type": "output", "content": f"生成内容时发生错误: {e}"}, ensure_ascii=False) + "\n"
        finally:
            db_session.close()

    return Response(stream_with_context(generate_with_session()), content_type='text/plain; charset=utf-8')


# 3.9 定义获取历史记录的路由
@app.route('/history')
def get_history():
    """获取聊天历史记录"""
    try:
        from sqlalchemy.orm import sessionmaker
        from models import ChatSession
        from sqlalchemy import desc, create_engine
        from flask import jsonify
        
        # 数据库设置
        DATABASE_URL = "sqlite:///chat_history.db"
        engine = create_engine(DATABASE_URL, echo=False)
        
        # 创建数据库会话
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()
        
        # 获取所有会话，按时间倒序排列
        sessions = db_session.query(ChatSession).order_by(desc(ChatSession.start_time)).all()
        db_session.close()
        
        # 转换为JSON格式
        history_data = []
        for session in sessions:
            history_data.append({
                'id': session.id,
                'title': session.title or f"会话于 {session.start_time.strftime('%Y-%m-%d %H:%M')}",
                'start_time': session.start_time.isoformat()
            })
        
        return jsonify(history_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 3.10 定义加载特定历史记录的路由
@app.route('/history/<session_id>')
def load_history(session_id):
    """加载指定的聊天历史记录并渲染聊天页面"""
    try:
        from sqlalchemy.orm import sessionmaker
        from models import ChatSession, ChatMessage
        from sqlalchemy import create_engine
        
        # 数据库设置
        DATABASE_URL = "sqlite:///chat_history.db"
        engine = create_engine(DATABASE_URL, echo=False)
        
        # 创建数据库会话
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()
        
        # 查询指定的会话及其所有消息
        session_data = db_session.query(ChatSession).filter_by(id=session_id).first()
        
        if not session_data:
            return "会话未找到", 404
            
        messages = db_session.query(ChatMessage).filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
        db_session.close()
        
        # 将数据库消息转换为 session 格式
        chat_history = []
        for msg in messages:
            chat_history.append({
                'type': msg.message_type,
                'content': msg.content
            })
            
        # 将历史记录存入 Flask session
        session['chat_history'] = chat_history
        session['session_id'] = session_id
        
        # 重定向到聊天页面
        return redirect(url_for('chat_stream'))
        
    except Exception as e:
        print(f"加载历史记录时出错: {e}")
        return "加载历史记录时出错", 500


# 启动应用的入口
if __name__ == '__main__':
    app.run(debug=True, port=5001)
