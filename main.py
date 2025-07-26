#!/usr/bin/env python3
"""
Newsletter Agent - Single file executable entry point
"""

# Import all necessary modules to ensure PyInstaller includes them
import os
import sys
import asyncio
import threading
import json
from queue import Queue, Empty

# Flask imports
from flask import Flask, render_template, request, session, redirect, url_for, Response, stream_with_context
import markdown

# LangChain imports
from langchain_core.messages import AIMessage, HumanMessage

# Project imports
from agent import NewsletterAgent
from tools import news_tools
from tools.reddit_search import reddit_search_tool
from tools.rss_feed import rss_feed_tool
from tools.content_delivery import content_delivery_tool

# Run the application
if __name__ == '__main__':
    # Add the current directory to sys.path to ensure imports work
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run the Flask app
    from app import app
    app.run(debug=False, port=5001)