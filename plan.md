# 新闻通讯生成代理项目总结

本文档总结了新闻通讯生成代理的最终实现方案和架构。

## 技术栈

*   **语言:** Python
*   **Web 框架:** Flask
*   **AI 框架:** LangChain
*   **语言模型:** OpenAI API (`gpt-4o`)
*   **数据提取:**
    *   `newsapi-python` (用于对接 NewsAPI)
    *   `newspaper3k` (用于抓取和解析网页文章内容)
*   **前端:** HTML, CSS
*   **Markdown 解析:** `Markdown`

## 项目架构

项目最终由三个核心模块组成：

1.  **工具模块 (`tools.py`)**:
    *   提供了两个核心工具：`Search_News` 和 `Scrape_Article_Content`。
    *   工具名遵循了 OpenAI API 的规范（不含空格）。
    *   使用 `python-dotenv` 库从 `.env` 文件安全加载 API 密钥。

2.  **AI代理模块 (`agent.py`)**:
    *   封装了 `NewsletterAgent` 类，负责处理所有 AI 相关的逻辑。
    *   **关键决策**: 使用 `create_openai_tools_agent` 代替了 `create_react_agent`。这个选择极大地提升了代理调用工具的稳定性和可靠性，因为它专门为 OpenAI 的函数调用功能设计。
    *   代理能够根据用户输入，自主地选择并执行工具，并在信息收集完毕后生成最终的报告。

3.  **Web应用模块 (`app.py`)**:
    *   使用 Flask 搭建了一个简单的 Web 服务器。
    *   提供了两个路由：
        *   `/`: 显示一个允许用户输入主题的表单 (`index.html`)。
        *   `/generate`: 接收用户主题，调用 `NewsletterAgent`，并将生成的 Markdown 格式内容转换为 HTML，最终渲染在 `newsletter.html` 页面上。
    *   通过 `static/style.css` 提供了简洁的用户界面样式。

## 开发流程回顾

项目遵循了计划中的任务分解，但在“集成与测试”阶段遇到了多次挑战，主要集中在 **环境依赖** 和 **代理逻辑** 上。通过迭代式的调试，我们解决了以下关键问题：
*   补全了 `python-dotenv`, `langchain-openai`, `lxml_html_clean`, `Markdown` 等多个缺失的 Python 依赖。
*   修正了代理提示模板以符合 LangChain 的要求。
*   修正了工具名称以符合 OpenAI API 的规范。
*   通过重构代理创建方式，解决了模型输出格式不稳定的核心问题。

最终，我们成功交付了一个功能完整、可交互的原型。

## 最新开发进度

### 1. 多模型支持
*   实现了在 OpenAI 和 DeepSeek 模型之间切换的功能，用户可以在前端界面选择使用的语言模型。
*   `agent.py` 中的 `NewsletterAgent` 类现在可以根据选择动态初始化不同的语言模型。

### 2. 搜索工具修复与优化
*   将 NewsAPI 的 `Search_News` 工具从 `get_top_headlines` 接口更换为 `get_everything`，显著提高了新闻搜索的相关性和成功率。
*   增加了对空查询的健壮性处理，避免了无效的 API 请求。
*   新增了 `tests/test_tools.py` 单元测试文件，确保了 `Search_News` 工具的正确性。

### 3. 多轮对话功能
*   为 AI 代理 (`agent.py`) 增加了对话记忆能力，通过 `chat_history` 管理上下文。
*   重构了 Web 应用 (`app.py`)，利用 Flask 的 `session` 来持久化聊天历史，实现了用户与代理的持续对话。
*   更新了前端界面 (`templates/index.html`, `templates/chat.html`, `static/style.css`)，提供了新的聊天界面和交互流程。
*   将旧的 `templates/newsletter.html` 移动到了 `trash` 目录，并创建了 `templates/chat.html` 作为新的对话页面。
