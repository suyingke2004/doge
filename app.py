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
from models import Base, User, ChatSession, ChatMessage, LongTermMemory
import uuid
from datetime import datetime
from collections import deque
import queue
from langchain_core.callbacks import BaseCallbackHandler

class StreamCallbackHandler(BaseCallbackHandler):
    """自定义回调处理程序，用于捕获工具调用状态"""
    
    def __init__(self, queue):
        self.queue = queue

    def on_tool_start(self, serialized, input_str, **kwargs):
        """工具开始执行时调用"""
        tool_name = serialized.get("name", "未知工具")
        self.queue.put({"type": "status", "content": f"[正在调用工具: {tool_name}]"})

    def on_tool_end(self, output, **kwargs):
        """工具执行结束时调用"""
        self.queue.put({"type": "status", "content": "[工具调用完成]"})

    def on_tool_error(self, error, **kwargs):
        """工具执行出错时调用"""
        self.queue.put({"type": "status", "content": f"[工具调用出错: {str(error)}]"})

# 1. 创建 Flask 应用实例
app = Flask(__name__)
# 设置一个固定的密钥，以便使用 session
# 在生产环境中，应使用更安全的方式管理密钥，例如环境变量
app.secret_key = "a_fixed_secret_key_for_testing_purposes_only"

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

# 2. 定义主页路由
@app.route('/')
def index():
    """显示主页，可以是登录或注册页面"""
    # 简单实现：重定向到聊天流端点
    # 在更完整的实现中，这里可能需要检查用户是否已登录
    return redirect(url_for('chat_stream'))

# 3. 定义开始新对话的路由
@app.route('/new')
def new_chat():
    """清除 session 中的聊天记录，开始一个新对话"""
    session.pop('chat_history', None)
    session.pop('model_provider', None)
    session.pop('model_name', None)
    session.pop('maxiter', None)
    session.pop('session_id', None)  # 确保创建新的数据库会话
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




# 3.9 定义PDF下载路由
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

def get_memory_context(user_id, db_session, session_id):
    """
    获取用户的短期和长期记忆上下文
    :param user_id: 用户ID
    :param db_session: 数据库会话
    :param session_id: 当前的会话ID
    :return: 包含短期和长期记忆的上下文字典
    """
    # --- 新逻辑：从数据库获取短期记忆 ---
    recent_messages = db_session.query(ChatMessage).filter_by(session_id=session_id).order_by(desc(ChatMessage.timestamp)).limit(10).all()
    # 将结果反转，使其按时间正序排列
    recent_messages.reverse()
    
    # 转换为与之前兼容的字典格式
    short_term_memory = [{'type': msg.message_type, 'content': msg.content} for msg in recent_messages]
    
    print(f"DEBUG: 从数据库获取的短期记忆条数: {len(short_term_memory)}")

    # 获取长期记忆 (这部分逻辑不变)
    long_term_memory = db_session.query(LongTermMemory).filter_by(user_id=user_id).first()
    
    # 打印调试信息
    print(f"获取记忆上下文 - User ID: {user_id}")
    if long_term_memory:
        print(f"长期记忆 - 用户画像: {long_term_memory.profile_summary}")
        print(f"长期记忆 - 情绪趋势: {long_term_memory.emotion_trends}")
        print(f"长期记忆 - 重要事件: {long_term_memory.important_events}")
    else:
        print("未找到长期记忆记录")
    
    return {
        'short_term': short_term_memory, # short_term_memory已经是list of dicts
        'long_term': {
            'profile_summary': long_term_memory.profile_summary if long_term_memory else '',
            'emotion_trends': long_term_memory.emotion_trends if long_term_memory else {},
            'important_events': long_term_memory.important_events if long_term_memory else {}
        }
    }


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
            
            print(f"Received form data: {dict(request.form)}")
            print(f"user_input: '{user_input}'")
            
            # 模型和语言参数管理
            if 'chat_history' not in session:
                model_provider = request.form.get('model_provider', 'deepseek')
                model_name = request.form.get('model_name', '').strip() or None
                maxiter = int(request.form.get('maxiter', 128))
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

            # 输入验证
            if user_input is None or not user_input.strip():
                yield json.dumps({"type": "output", "content": "错误: 请输入一个主题或问题."}, ensure_ascii=False) + "\n"
                return

            # --- 核心逻辑重构 ---

            # 1. 获取或创建会话ID
            session_id = session.get('session_id')
            if not session_id:
                new_session_db = ChatSession(title=user_input[:100])
                db_session.add(new_session_db)
                db_session.commit()
                session_id = new_session_db.id
                session['session_id'] = session_id
            
            user_id = session_id  # 简化处理

            # 2. 将当前用户消息存入数据库
            user_message = ChatMessage(session_id=session_id, message_type='human', content=user_input)
            db_session.add(user_message)
            db_session.commit()

            # 3. 从数据库获取包含当前消息的记忆上下文
            memory_context = get_memory_context(user_id, db_session, session_id)
            
            # 4. 从记忆上下文构建LangChain消息列表
            chat_history_messages = []
            for msg in memory_context['short_term']:
                if msg['type'] == 'human':
                    chat_history_messages.append(HumanMessage(content=msg['content']))
                else:
                    chat_history_messages.append(AIMessage(content=msg['content']))
            
            print(f"DEBUG: 构建的chat_history_messages数量: {len(chat_history_messages)}")

            try:
                # 5. 创建并调用Agent
                agent = DogAgent(
                    model_provider=model_provider, 
                    model_name=model_name, 
                    chat_history=chat_history_messages,
                    max_iterations=maxiter,
                    language=language,
                    memory_context=memory_context,
                    db_session=db_session
                )
                full_response = agent.chat(user_input)

                # 6. 将AI响应存入数据库
                ai_message = ChatMessage(session_id=session_id, message_type='ai', content=full_response)
                db_session.add(ai_message)
                db_session.commit()

                # 7. 更新用于前端渲染的session变量 (这部分可以保留)
                chat_history_raw = session.get('chat_history', [])
                chat_history_raw.append({'type': 'human', 'content': user_input})
                chat_history_raw.append({'type': 'ai', 'content': full_response})
                session['chat_history'] = chat_history_raw
                session.modified = True
                
                # 8. 返回完整响应
                yield json.dumps({"type": "output", "content": full_response}, ensure_ascii=False) + "\n"

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
                # 获取该会话的第一条用户消息和AI响应
                first_human_message = db_session.query(ChatMessage).filter_by(
                    session_id=session.id, message_type='human'
                ).order_by(ChatMessage.timestamp).first()
                
                first_ai_message = db_session.query(ChatMessage).filter_by(
                    session_id=session.id, message_type='ai'
                ).order_by(ChatMessage.timestamp).first()
                
                history_data.append({
                    'id': session.id,
                    'title': session.title or f"会话于 {session.start_time.strftime('%Y-%m-%d %H:%M')}",
                    'start_time': session.start_time.isoformat(),
                    'user_input': first_human_message.content if first_human_message else "",
                    'agent_response': first_ai_message.content if first_ai_message else ""
                })
            
            return jsonify(history_data)
        finally:
            db_session.close()
            
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


# 3.12 定义用户注册页面路由
@app.route('/register')
def register_page():
    """显示用户注册页面"""
    return render_template('register.html')


# 3.13 定义用户注册API端点
@app.route('/api/user/register', methods=['POST'])
def register_user():
    """用户注册接口"""
    from models import User
    from werkzeug.security import generate_password_hash
    import json
    
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 验证必要字段
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password or not email:
            return jsonify({
                "status": "error",
                "code": 400,
                "message": "缺少必要参数: username, password, email"
            }), 400
        
        # 检查用户名和邮箱是否已存在
        db_session = SessionLocal()
        try:
            existing_user = db_session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return jsonify({
                    "status": "error",
                    "code": 409,
                    "message": "用户名或邮箱已存在"
                }), 409
            
            # 创建新用户
            password_hash = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash
            )
            
            db_session.add(new_user)
            db_session.commit()
            
            # 生成访问令牌（简化实现，实际项目中应使用JWT等）
            import secrets
            access_token = secrets.token_urlsafe(32)
            
            return jsonify({
                "status": "success",
                "code": 200,
                "message": "注册成功",
                "response_data": {
                    "user_id": new_user.id,
                    "access_token": access_token,
                    "expires_in": 3600  # 1小时过期
                }
            })
        finally:
            db_session.close()
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "code": 500,
            "message": f"注册失败: {str(e)}"
        }), 500


# 启动应用的入口
if __name__ == '__main__':
    app.run(debug=True, port=5001)
