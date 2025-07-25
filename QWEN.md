# Qwen Code Context

This document provides context about the coding practices, project structure, and development guidelines for this project. It is tailored to the specific preferences and environment of the developer working on this codebase.

## Project Overview

This is a newsletter generation agent project that uses AI to research topics and create personalized newsletters. It integrates multiple tools and data sources, and provides a web interface for interaction.

## Core Technologies

*   **Language:** Python 3
*   **Web Framework:** Flask
*   **AI Framework:** LangChain
*   **Language Models:** OpenAI API (gpt-4o) and DeepSeek API (deepseek-chat)
*   **Data Extraction:**
    *   `newsapi-python` (for NewsAPI integration)
    *   `newspaper3k` (for scraping and parsing article content)
*   **Frontend:** HTML, CSS
*   **Markdown Parsing:** `Markdown` library

## Development Environment

Ensure you are working within the `news_agent` Conda environment as specified in `DEVELOPER_STYLE_GUIDE.md`.

```bash
conda activate news_agent
```

## Coding Style

*   **Primary Guide:** Follow the [Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md). This is the base style for the project.
*   **Docstrings:** Use Google-style docstrings for all modules, classes, and functions.
*   **Naming Conventions:**
    *   Variables and functions: `snake_case`
    *   Classes: `PascalCase`
    *   Constants: `UPPER_SNAKE_CASE`
*   **Line Length:** Aim for 79 characters per line, but up to 100 is acceptable for readability if it avoids awkward line breaks.
*   **Imports:**
    *   Group imports in the standard order: standard library, third-party libraries, local imports.
    *   Each group should be separated by a blank line.
    *   Within each group, imports should be sorted alphabetically.
*   **Comments:**
    *   Write comments in Chinese for better understanding, especially for complex logic.
    *   Comments should explain "why" rather than "what".
*   **Error Handling:** Always handle potential exceptions gracefully, providing informative error messages where possible.

## Project Structure and Key Files

*   `agent.py`: Contains the `NewsletterAgent` class, which encapsulates the AI logic, tools, and conversation history management.
*   `app.py`: The Flask web application. Handles routing, user input, session management, and interaction with the agent.
*   `tools.py`: Defines the tools (`Search_News`, `Scrape_Article_Content`) available to the agent.
*   `requirements.txt`: Lists all Python dependencies.
*   `templates/`: Contains HTML templates for the web interface.
*   `static/`: Contains static assets like CSS files.
*   `tests/`: Contains unit tests for the project.
*   `.env`: (Not in version control) Stores API keys and other sensitive configuration. A `.env.example` should be provided as a template.

## Agent Architecture

The project uses LangChain's `create_openai_tools_agent` to build the AI agent. This approach is more stable and reliable for tool calling with OpenAI models compared to other methods. The agent is initialized with a system prompt, chat history, and a set of tools. It can perform multi-step reasoning and tool integration to generate a final newsletter.

## Web Application

The Flask app provides a simple web interface with the following key routes:

*   `/`: The main page where users can enter a topic or ask a question.
*   `/chat`: Handles form submissions, calls the agent, and displays the results.
*   `/new`: Clears the session and starts a new conversation.
*   `/chat_stream`: Handles streaming responses from the agent for a better user experience.

## Testing

*   Unit tests are located in the `tests/` directory.
*   Use `pytest` to run the tests.
*   Write tests for core functionalities, especially for tools and agent logic.
*   Since you cannot interact with a browser directly, do not use manual browser testing. Instead, use headless browser testing or write more comprehensive integration tests.

## Future Development

Refer to `plan.md` for a detailed roadmap of future features and improvements. Key areas for expansion include integrating more data sources (Reddit, RSS), enhancing the UI/UX, implementing content delivery systems (email, PDF), adding personalization, optimizing performance, and improving test coverage.

## Style Guide References

*   Google Python Style Guide: [https://github.com/google/styleguide/blob/gh-pages/pyguide.md](https://github.com/google/styleguide/blob/gh-pages/pyguide.md)
*   Google Developer Documentation Style Guide: [https://developers.google.com/style](https://developers.google.com/style)