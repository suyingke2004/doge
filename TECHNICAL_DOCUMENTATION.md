# 新闻通讯生成代理技术文档

## 项目概述

本项目是一个基于AI的新闻通讯生成代理，能够研究指定主题并生成个性化、信息丰富的新闻通讯。它整合了多种工具和数据源，并提供了一个Web界面用于交互。

## 技术栈

- **语言**: Python 3.11
- **Web框架**: Flask
- **AI框架**: LangChain
- **语言模型**: 
  - OpenAI API (gpt-4o)
  - DeepSeek API (deepseek-chat)
  - Zhipu AI (glm-4)
  - Alibaba Cloud (qwen-max)
  - Moonshot AI (moonshot-v1-8k)
- **数据提取**:
  - newsapi-python (NewsAPI集成)
  - newspaper3k (网页文章抓取和解析)
  - praw (Reddit API集成)
  - feedparser (RSS订阅源解析)
  - beautifulsoup4 (通用网页内容提取)
  - requests (HTTP请求获取网页内容)
- **内容交付**:
  - sendgrid (邮件发送)
  - weasyprint (PDF导出)
- **前端**: HTML, CSS
- **Markdown解析**: Markdown库

## 项目结构

```
news_agent/
├── agent.py                 # AI代理核心逻辑
├── app.py                   # Flask Web应用
├── requirements.txt         # Python依赖列表
├── .env.example             # 环境变量配置示例
├── plan.md                  # 项目开发计划和进度
├── QWEN.md                  # 项目编码规范和上下文
├── DEVELOPER_STYLE_GUIDE.md # 开发者风格指南
├── static/                  # 静态资源（CSS等）
│   └── style.css
├── templates/               # HTML模板
│   ├── chat.html
│   ├── debug_chat.html
│   └── simple_test.html
├── tools/                   # 工具模块
│   ├── __init__.py          # 新闻API和文章抓取工具
│   ├── reddit_search.py     # Reddit搜索工具
│   ├── rss_feed.py          # RSS订阅源工具
│   ├── content_delivery.py  # 内容交付工具（邮件和PDF）
│   └── pdf_export.py        # PDF导出工具
├── tests/                   # 测试套件
│   ├── test_tools.py
│   ├── test_ui_routes.py
│   ├── test_model_selection.py
│   ├── test_streaming.py
│   └── ...
└── ...
```

## 核心组件

### 1. NewsletterAgent (agent.py)

这是项目的核心AI代理类，负责：
- 初始化语言模型（支持多种提供商）
- 管理对话历史
- 集成工具集
- 生成新闻通讯内容
- 支持流式输出

关键特性：
- 支持多轮对话记忆
- 可配置最大迭代次数
- 支持多种AI模型提供商
- 实现了流式响应功能

### 2. 工具集 (tools/)

#### 2.1 新闻工具 (tools/__init__.py)
- `Search_News`: 从NewsAPI搜索相关新闻
- `Scrape_Article_Content`: 从URL抓取文章内容

#### 2.2 Reddit搜索工具 (tools/reddit_search.py)
- `Search_Reddit`: 从Reddit搜索相关讨论

#### 2.3 RSS订阅源工具 (tools/rss_feed.py)
- `Search_RSS_Feeds`: 从RSS订阅源获取内容

#### 2.4 内容交付工具 (tools/content_delivery.py)
- `Send_Email`: 通过邮件发送内容
- `Export_PDF`: 将内容导出为PDF文件

### 3. Web应用 (app.py)

基于Flask的Web应用，提供以下功能：
- 聊天界面，支持多轮对话
- 模型选择（提供商和具体模型）
- 最大迭代次数配置
- 流式响应显示
- 对话历史管理

主要路由：
- `/`: 重定向到聊天界面
- `/chat_stream`: 处理所有聊天请求（GET显示界面，POST处理对话）
- `/new`: 开始新对话

### 4. 前端界面 (templates/chat.html, static/style.css)

- 响应式聊天界面
- 模型选择下拉框
- 流式内容显示
- 对话历史展示
- 美观的UI设计

## 开发环境

### 依赖安装

```bash
# 创建并激活conda环境
conda create -n news_agent python=3.11
conda activate news_agent

# 安装依赖
pip install -r requirements.txt
```

### 环境变量配置

复制`.env.example`为`.env`并填写相应API密钥：

```env
# API Keys for different model providers
OPENAI_API_KEY=your_openai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
ZHIPU_API_KEY=your_zhipu_api_key_here
ALI_API_KEY=your_ali_api_key_here
MOONSHOT_API_KEY=your_moonshot_api_key_here

# News API
NEWS_API_KEY=your_newsapi_key_here

# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# SendGrid for email delivery
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=your_sender_email@example.com
```

## 测试

使用pytest运行测试：

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_tools.py -v
```

测试类型：
- 单元测试：测试工具函数
- 集成测试：测试Web路由和模型选择
- 流式处理测试：测试多轮对话和流式响应
- UI测试：测试前端界面交互

## 部署

1. 配置环境变量
2. 安装依赖
3. 运行应用：

```bash
python app.py
```

默认在`http://localhost:5001`访问应用。

## 扩展性

项目采用模块化设计，易于扩展：

1. 添加新的AI模型提供商：在`agent.py`的`MODEL_PROVIDERS`中添加配置
2. 添加新的工具：在`tools/`目录下创建新模块并注册到`agent.py`
3. 添加新的数据源：实现相应的工具函数并注册到代理
4. 增强UI功能：修改`templates/`和`static/`中的文件

## 故障排除

常见问题：
1. API密钥未配置：确保`.env`文件中配置了所有必需的API密钥
2. 依赖缺失：运行`pip install -r requirements.txt`确保所有依赖已安装
3. 模型配置错误：检查模型提供商和模型名称是否正确
4. 流式响应问题：检查异步处理代码和前端JavaScript实现