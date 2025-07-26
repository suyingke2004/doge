# 新闻通讯生成代理 (Newsletter Generation Agent)

## 项目简介

新闻通讯生成代理是一个智能AI助手，能够根据用户指定的主题自动搜集相关信息并生成简洁、引人入胜且信息丰富的新闻通讯。它整合了多种信息源，包括新闻网站、Reddit讨论和RSS订阅，能够提供全面的内容概览。

## 核心功能

1. **多源信息搜集**：
   - 从NewsAPI获取最新新闻
   - 从Reddit搜索相关讨论
   - 从RSS订阅源获取专业内容

2. **智能内容生成**：
   - 利用先进的AI模型（支持OpenAI、DeepSeek等）分析和整理信息
   - 生成结构化、易读的新闻通讯

3. **多轮对话支持**：
   - 支持连续对话，可以追问更多细节
   - 保持上下文记忆，提供连贯的交互体验

4. **多种模型选择**：
   - 支持多个AI模型提供商
   - 可选择具体模型以满足不同需求

5. **流式响应**：
   - 实时显示AI生成内容，提升用户体验

6. **内容交付**：
   - 通过邮件发送生成的内容
   - 导出为PDF文件保存

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

## 快速开始

### 1. 环境准备

```bash
# 创建并激活conda环境
conda create -n news_agent python=3.11
conda activate news_agent

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

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

### 3. 启动应用

```bash
python app.py
```

应用将启动在`http://localhost:5001`。

## 使用指南

### 使用流程

1. **访问应用**：
   打开浏览器访问`http://localhost:5001`。

2. **选择模型**：
   - 选择AI模型提供商（如DeepSeek、OpenAI等）
   - 选择具体模型（如gpt-4o、deepseek-chat等）
   - 设置最大迭代次数（1-10，默认为5）

3. **输入主题**：
   在输入框中输入您感兴趣的新闻主题，例如"人工智能最新发展"。

4. **查看结果**：
   AI将自动搜集相关信息并生成新闻通讯，内容会以流式方式实时显示。

5. **继续对话**：
   可以继续提问以获取更多细节，代理会基于之前的对话历史提供连贯的回答。

6. **内容交付**：
   - 请求发送邮件："请将这份新闻通讯通过邮件发送给我"
   - 请求导出PDF："请将这份新闻通讯导出为PDF"

## 应用界面说明

### 1. 聊天界面
主界面为聊天窗口，显示用户和AI助手的对话历史。

### 2. 模型选择
首次访问时会显示模型选择表单，可选择：
- 模型提供商（DeepSeek、OpenAI等）
- 具体模型（各提供商的默认模型及其他选项）
- 最大迭代次数（1-10）

### 3. 输入框
底部的输入框用于输入问题或主题。

### 4. 开始新对话
点击"开始新对话"按钮可清除历史记录，开始新的对话。

## 常见使用场景

1. **科技资讯**：
   输入"最新的人工智能技术发展"获取AI领域的最新动态。

2. **财经新闻**：
   输入"最近的股市趋势分析"获取金融市场相关信息。

3. **学术研究**：
   输入"量子计算的最新研究成果"获取前沿科学研究内容。

4. **娱乐资讯**：
   输入"最近热门的电影和电视剧"获取娱乐行业动态。

5. **个性化内容**：
   结合多轮对话深入了解特定主题的各个方面。

## 开发指南

### 测试

使用pytest运行测试：

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_tools.py -v
```

### 扩展性

项目采用模块化设计，易于扩展：

1. 添加新的AI模型提供商：在`agent.py`的`MODEL_PROVIDERS`中添加配置
2. 添加新的工具：在`tools/`目录下创建新模块并注册到`agent.py`
3. 添加新的数据源：实现相应的工具函数并注册到代理
4. 增强UI功能：修改`templates/`和`static/`中的文件

## 未来发展规划

1. **更多数据源**：
   集成更多类型的信息源，如Twitter、专业数据库等。

2. **个性化推荐**：
   根据用户历史偏好提供个性化内容推荐。

3. **移动端适配**：
   优化移动端用户体验。

4. **定时发送**：
   支持定时自动发送新闻通讯。

5. **多语言支持**：
   扩展支持更多语言的内容生成。

## 注意事项

1. **API密钥**：
   确保已正确配置所有必需的API密钥，否则相关功能将无法使用。

2. **网络连接**：
   应用需要稳定的网络连接以访问外部API。

3. **模型限制**：
   不同的AI模型有不同的能力和限制，选择合适的模型可获得更好的结果。

4. **隐私保护**：
   应用不会存储用户的对话内容，所有信息仅在会话期间保存在内存中。

5. **内容准确性**：
   AI生成的内容基于搜集到的信息，可能存在不准确或过时的情况，请以官方信息为准。

## 技术文档

详细的技术文档请参考：
- [技术文档](TECHNICAL_DOCUMENTATION.md)
- [应用文档](APPLICATION_DOCUMENTATION.md)
- [开发规范](DEVELOPER_STYLE_GUIDE.md)
- [项目计划](plan.md)

## 故障排除

1. **无法启动应用**：
   - 检查是否已安装所有依赖
   - 确认环境变量已正确配置

2. **API调用失败**：
   - 检查API密钥是否正确
   - 确认网络连接正常

3. **模型选择无效**：
   - 检查所选模型是否支持
   - 确认API密钥与模型提供商匹配

4. **流式响应中断**：
   - 检查网络连接
   - 降低最大迭代次数设置

5. **内容交付失败**：
   - 检查SendGrid API密钥和发件人邮箱配置
   - 确认系统已安装wkhtmltopdf（PDF导出所需）