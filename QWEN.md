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

## Development Workflow

*   The application automatically restarts when code changes are detected (using Flask's debug mode).
*   You don't need to manually restart the application after making changes.

## Testing

*   Unit tests are located in the `tests/` directory.
*   Use `pytest` to run the tests.
*   Write tests for core functionalities, especially for tools and agent logic.
*   Since you cannot interact with a browser directly, do not use manual browser testing. Instead, use headless browser testing or write more comprehensive integration tests.

## Bug Fixes

### History Sidebar Display Issue (July 26, 2025)

Fixed an issue where history records in the sidebar had inconsistent heights and displayed full content without truncation. The fix involved modifying CSS styles and JavaScript logic to ensure uniform display.

Changes made:
1. Modified `static/style.css` to set a fixed height for history items in the sidebar and added text truncation
2. Updated `templates/chat.html` to truncate history titles to 30 characters with ellipsis
3. Updated `templates/history.html` to limit displayed content and maintain consistent item heights

### UI Layout and Styling Improvements (July 26, 2025)

Improved the UI layout and styling by moving the "New Chat" button to below the model selection sidebar and adding a background image to the model selection area.

Changes made:
1. Moved the "New Chat" button from below the chat input to below the model selection sidebar in `templates/chat.html`
2. Added a background image to the model selection sidebar in `static/style.css`
3. Created new styling for the relocated "New Chat" button to make it more visually appealing

### Language Toggle Fix (July 26, 2025)

Fixed an issue where the language toggle button was not responding to clicks. The fix involved adding the missing JavaScript event listener and functionality to switch between Chinese and English.

Changes made:
1. Added JavaScript code to handle language toggle button clicks in `templates/chat.html`
2. Implemented logic to switch between Chinese and English with appropriate UI updates
3. Updated page title and all other UI elements (history sidebar title, model sidebar title, form labels, etc.) to reflect the selected language
4. Added comprehensive translation mapping for all visible text elements

### History Record Background Enhancement (July 26, 2025)

Enhanced the visual distinction between history records by adding semi-transparent light blue backgrounds that don't overly obscure the background image.

Changes made:
1. Changed background color of history items from white to light blue (rgba(173, 216, 230, 0.3)) in both `static/style.css` (for chat sidebar) and `templates/history.html` (for history page)
2. Increased border radius from 4px to 10px for a more rounded appearance
3. Updated hover effects to use light blue as well
4. Maintained consistency with the overall design aesthetic

### PDF Download Link Issue (July 26, 2025)

Fixed an issue where PDF download links were displayed as plain text and required a page refresh to become clickable. The fix involved simplifying the HTML link generation in `agent.py` to remove unnecessary JavaScript event handlers, making the links immediately functional.

Changes made:
1. Modified the PDF link handling code in `agent.py` to generate clean HTML anchor tags
2. Removed complex JavaScript onclick handlers that were causing the refresh requirement
3. Ensured the frontend properly renders HTML content using `innerHTML`

## Bug Fixes

### PDF Download Link Issue (July 26, 2025)

Fixed an issue where PDF download links were displayed as plain text and required a page refresh to become clickable. The fix involved simplifying the HTML link generation in `agent.py` to remove unnecessary JavaScript event handlers, making the links immediately functional.

Changes made:
1. Modified the PDF link handling code in `agent.py` to generate clean HTML anchor tags
2. Removed complex JavaScript onclick handlers that were causing the refresh requirement
3. Ensured the frontend properly renders HTML content using `innerHTML`

### PDF Link Rendering Issue (July 26, 2025)

Fixed an issue where PDF download links in Markdown format were not properly rendered as HTML links during streaming responses. The problem occurred because the streaming response directly used `innerHTML` without converting Markdown to HTML, while the page refresh process correctly converted Markdown to HTML.

Changes made:
1. Added the `marked` library to the chat template for Markdown to HTML conversion
2. Modified the JavaScript in `chat.html` to convert Markdown to HTML during streaming responses
3. Ensured consistent link rendering behavior between streaming and page refresh scenarios

## Future Development

Refer to `plan.md` for a detailed roadmap of future features and improvements. Key areas for expansion include integrating more data sources (Reddit, RSS), enhancing the UI/UX, implementing content delivery systems (email, PDF), adding personalization, optimizing performance, and improving test coverage.

## Style Guide References

*   Google Python Style Guide: [https://github.com/google/styleguide/blob/gh-pages/pyguide.md](https://github.com/google/styleguide/blob/gh-pages/pyguide.md)
*   Google Developer Documentation Style Guide: [https://developers.google.com/style](https://developers.google.com/style)