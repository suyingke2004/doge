from flask import Flask, render_template, request, session, redirect, url_for, Response, stream_with_context, jsonify
from agent import DogAgent
from langchain_core.messages import AIMessage, HumanMessage
import markdown
import os
import asyncio
import json
import sys
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models import Base, ChatSession, ChatMessage
import uuid
from datetime import datetime

# 1. 创建 Flask 应用实例
app = Flask(__name__)
# 设置一个密钥，以便使用 session
# 在生产环境中，应使用更安全的方式管理密钥，例如环境变量
app.secret_key = os.urandom(24)

# 数据库设置
DATABASE_URL = "sqlite:///chat_history.db"
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

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
    # 获取数据库会话
    from sqlalchemy.orm import sessionmaker
    from models import ChatSession, ChatMessage
    from sqlalchemy import create_engine
    
    # 数据库设置
    DATABASE_URL = "sqlite:///chat_history.db"
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    try:
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

            # 获取或创建会话ID和ChatSession对象
            session_id = session.get('session_id')
            if not session_id:
                # 创建新的ChatSession
                new_session = ChatSession(title=user_input[:100])  # 使用前100个字符作为标题
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
                
                # 创建代理实例，并传入历史记录、 maxiter 和 language 参数
                agent = DogAgent(
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

        return Response(stream_with_context(generate_with_session()), content_type='text/plain; charset=utf-8')
        
    finally:
        # 确保关闭数据库会话
        db_session.close()


# 3.9 定义获取历史记录的路由
@app.route('/history')
def get_history():
    """获取聊天历史记录"""
    try:
        db_session = SessionLocal()
        try:
            # 获取所有会话，按开始时间倒序排列
            sessions = db_session.query(ChatSession).order_by(desc(ChatSession.start_time)).all()
            
            # 转换为JSON格式
            history_data = []
            for session in sessions:
                history_data.append({
                    'id': session.id,
                    'title': session.title or f"会话于 {session.start_time.strftime('%Y-%m-%d %H:%M')}",
                    'start_time': session.start_time.isoformat()
                })
            
            return jsonify(history_data)
        finally:
            db_session.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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
        db_session = SessionLocal()
        try:
            # 查询指定的会话及其所有消息
            session_data = db_session.query(ChatSession).filter_by(id=session_id).first()
            
            if not session_data:
                return "会话未找到", 404
                
            # 获取该会话的所有消息，按时间排序
            messages = db_session.query(ChatMessage).filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
            
            # 准备用于渲染模板的数据
            chat_history_to_render = []
            for message in messages:
                chat_history_to_render.append({
                    'type': message.message_type,
                    'content': message.content
                })
            
            # 将 Markdown 转换为 HTML
            for message in chat_history_to_render:
                if message['type'] == 'ai':
                    message['content_html'] = markdown.markdown(message['content'])
            
            # 设置session变量
            session['session_id'] = session_id
            session['chat_history'] = chat_history_to_render
            
            return render_template('chat.html', chat_history=chat_history_to_render)
        finally:
            db_session.close()
            
    except Exception as e:
        return f"加载历史记录时出错: {str(e)}", 500


# 3.11 定义历史记录页面路由
@app.route('/history_page')
def history_page():
    """显示聊天历史记录页面"""
    from flask import render_template
    return render_template('history.html')


@app.route('/main_chat')
def main_chat():
    try:
        db = SessionLocal()
        try:
            # 检查 Flask session 中是否已有聊天会话ID
            # chat_session_id = session.get('chat_session_id')
            
            # if chat_session_id:
            #     # 如果有，查询该会话和其所有消息
            #     chat_session = db.query(ChatSession).filter(ChatSession.id == chat_session_id).first()
            #     if chat_session:
            #         # 按时间顺序加载消息
            #         messages_query = db.query(ChatMessage).filter(ChatMessage.session_id == chat_session_id).order_by(ChatMessage.timestamp.asc()).all()
            #         # 格式化消息以适应模板
            #         messages = [{'type': msg.message_type, 'content': msg.content} for msg in messages_query]
            #     else:
            #         # 如果session中的ID无效，则创建一个新会话
            #         chat_session_id = None 
            
            # if not chat_session_id:
            #     # 如果没有会话ID，或ID无效，则创建新会话
            #     new_session = ChatSession()
            #     db.add(new_session)
            #     db.commit()
            #     db.refresh(new_session)
            #     session['chat_session_id'] = new_session.id
            #     messages = [] # 新会话没有历史消息

            # return render_template(
            #     'main_chat.html',
            #     active_page='chat',
            #     active_session='dog',
            #     messages=messages
            # )
            # 1. 查找数据库中最新的会话
            chat_session = db.query(ChatSession).order_by(ChatSession.start_time.desc()).first()
            if chat_session:
                chat_session_id = chat_session.id
                session['chat_session_id'] = chat_session_id
                messages_query = db.query(ChatMessage).filter(ChatMessage.session_id == chat_session_id).order_by(ChatMessage.timestamp.asc()).all()
                messages = [{'type': msg.message_type, 'content': msg.content} for msg in messages_query]
            else:
                # 没有历史会话则新建
                new_session = ChatSession()
                db.add(new_session)
                db.commit()
                db.refresh(new_session)
                session['chat_session_id'] = new_session.id
                messages = []

            return render_template(
                'main_chat.html',
                active_page='chat',
                active_session='dog',
                messages=messages
            )
        finally:
            db.close()

    except Exception as e:
        return f"加载历史记录时出错: {str(e)}", 500
   

@app.route('/api/chat', methods=['POST'])
def api_chat():
    db = SessionLocal()
    try:
        # 1. 获取当前会话ID，如果不存在则报错
        chat_session_id = session.get('chat_session_id')
        if not chat_session_id:
            return jsonify({'error': '会话不存在，请刷新页面开始新会话'}), 400

        # 2. 获取用户输入
        data = request.get_json()
        user_input = data.get('text', '').strip()
        if not user_input:
            return jsonify({'error': '消息不能为空'}), 400

        # 3. 将用户消息存入数据库
        user_message = ChatMessage(session_id=chat_session_id, message_type='user', content=user_input)
        db.add(user_message)
        db.commit()

        # 4. 从数据库加载当前会话的完整历史记录
        messages_query = db.query(ChatMessage).filter(ChatMessage.session_id == chat_session_id).order_by(ChatMessage.timestamp.asc()).all()
        chat_history_for_agent = [
            HumanMessage(content=msg.content) if msg.message_type == 'user' else AIMessage(content=msg.content)
            for msg in messages_query
        ]

        # 5. 调用DogAgent获取回复
        dog_agent = DogAgent(
            model_provider="ali",
            model_name="qwen-max",
            chat_history=chat_history_for_agent,
            max_iterations=3
        )
        # 注意：DogAgent的chat方法需要是同步的，如果它是异步的，需要用asyncio.run()
        dog_response = dog_agent.chat(user_input)

        # 6. 将AI回复存入数据库
        ai_message = ChatMessage(session_id=chat_session_id, message_type='dog', content=dog_response)
        db.add(ai_message)
        db.commit()

        # 7. 返回AI的回复给前端
        return jsonify({'reply': dog_response})

    except Exception as e:
        db.rollback()
        print(f"API Chat Error: {e}")
        return jsonify({'error': f'处理消息时发生错误: {e}'}), 500
    finally:
        db.close()

# @app.route('/api/chat', methods=['POST'])
# def api_chat():
#     data = request.get_json()
#     user_input = data.get('text', '').strip()
#     if not user_input:
#         return jsonify({'error': '消息不能为空'}), 400

#     # 这里可以用 session 或数据库管理 chat_history
#     chat_history = session.get('chat_history', [])
#     dog_agent = DogAgent(
#         model_provider="ali",
#         model_name="qwen-max",
#         chat_history=chat_history,
#         max_iterations=3
#     )
#     dog_response = dog_agent.chat(user_input)
#     # 更新历史
#     chat_history.append({"role": "user", "content": user_input})
#     chat_history.append({"role": "assistant", "content": dog_response})
#     session['chat_history'] = chat_history

#     return jsonify({'reply': dog_response})

@app.route('/diary')
def diary():
    return render_template(
        'diary.html',
        active_page='chat',         # 保持顶部导航高亮在“聊天”
        active_session='diary'      # 侧边栏高亮“晚安日记”
    )
# 启动应用的入口
if __name__ == '__main__':
    app.run(debug=True, port=5001)
