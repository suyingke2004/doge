#!/usr/bin/env python3
"""
使用Selenium进行端到端测试
测试整个"翻书小狗"应用的功能，包括记忆模块、RAG知识库和生成能力
"""

import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.chrome import ChromeDriverManager
import os


class EndToEndTest(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        # 配置Chrome选项
        chrome_options = Options()
        # 移除 --headless 参数以在有头模式下运行
        # chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.binary_location = "/usr/bin/chromium-browser"  # 使用Chromium
        
        # 初始化WebDriver
        try:
            # 使用webdriver-manager自动下载和管理ChromeDriver，指定Chromium类型
            service = ChromeService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            raise Exception(f"无法初始化WebDriver: {e}")
        
        self.driver.implicitly_wait(15)  # 隐式等待15秒
        self.wait = WebDriverWait(self.driver, 15)
        
        # 应用URL
        self.base_url = "http://localhost:5001"

    def tearDown(self):
        """清理测试环境"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def test_memory_module_functionality(self):
        """测试记忆模块功能"""
        # 访问应用
        self.driver.get(self.base_url)
        
        # 等待页面加载
        self.wait.until(EC.presence_of_element_located((By.ID, "topic")))
        
        # 发送第一条消息
        input_field = self.driver.find_element(By.ID, "topic")
        input_field.send_keys("你好，我叫小明，我最近在为考试焦虑")
        input_field.send_keys(Keys.RETURN)
        
        # 等待响应
        time.sleep(5)
        
        # 获取第一条AI回复
        ai_messages = self.driver.find_elements(By.CLASS_NAME, "ai-message")
        self.assertGreater(len(ai_messages), 0, "应该收到AI回复")
        
        # 发送第二条消息，检查AI是否记得用户的名字和焦虑信息
        input_field = self.driver.find_element(By.ID, "topic")
        input_field.clear()
        input_field.send_keys("我刚才告诉你我的名字和焦虑情况了吗？")
        input_field.send_keys(Keys.RETURN)
        
        # 等待响应
        time.sleep(5)
        
        # 获取第二条AI回复
        ai_messages = self.driver.find_elements(By.CLASS_NAME, "ai-message")
        self.assertGreater(len(ai_messages), 1, "应该收到第二条AI回复")
        
        last_response = ai_messages[-1].text
        
        # 验证AI是否记得用户的名字和焦虑情况
        self.assertIn("小明", last_response, "AI应该记得用户的名字")
        self.assertIn("焦虑", last_response.lower(), "AI应该记得用户的焦虑情况")

    def test_rag_knowledge_base_functionality(self):
        """测试RAG知识库功能"""
        # 访问应用
        self.driver.get(self.base_url)
        
        # 等待页面加载
        self.wait.until(EC.presence_of_element_located((By.ID, "topic")))
        
        # 发送求助类问题，触发RAG工具
        input_field = self.driver.find_element(By.ID, "topic")
        input_field.send_keys("你能给我一些关于拖延症的建议吗？")
        input_field.send_keys(Keys.RETURN)
        
        # 等待响应
        time.sleep(8)
        
        # 获取AI回复
        ai_messages = self.driver.find_elements(By.CLASS_NAME, "ai-message")
        self.assertGreater(len(ai_messages), 0, "应该收到AI回复")
        
        last_response = ai_messages[-1].text
        
        # 验证回复内容与知识相关
        # 检查是否包含心理学相关的建议
        related_keywords = ["认知", "行为", "方法", "技巧", "建议", "策略"]
        found_keywords = [keyword for keyword in related_keywords if keyword in last_response]
        self.assertGreater(len(found_keywords), 0, "回复应该包含心理学相关的内容")

    def test_new_session_empty_memory(self):
        """测试新会话的空记忆状态"""
        # 访问应用
        self.driver.get(self.base_url)
        
        # 等待页面加载
        self.wait.until(EC.presence_of_element_located((By.ID, "topic")))
        
        # 发送消息
        input_field = self.driver.find_element(By.ID, "topic")
        input_field.send_keys("这是测试消息")
        input_field.send_keys(Keys.RETURN)
        
        # 等待响应
        time.sleep(3)
        
        # 点击"新对话"按钮
        new_chat_button = self.driver.find_element(By.ID, "new-chat")
        new_chat_button.click()
        
        # 等待新会话页面加载
        self.wait.until(EC.presence_of_element_located((By.ID, "topic")))
        
        # 发送消息询问之前的内容
        input_field = self.driver.find_element(By.ID, "topic")
        input_field.send_keys("我刚才说了什么？")
        input_field.send_keys(Keys.RETURN)
        
        # 等待响应
        time.sleep(3)
        
        # 检查AI是否不记得之前的内容
        ai_messages = self.driver.find_elements(By.CLASS_NAME, "ai-message")
        self.assertGreater(len(ai_messages), 0, "应该收到AI回复")
        
        last_response = ai_messages[-1].text
        # 验证AI不记得之前的内容
        self.assertNotIn("测试消息", last_response, "新会话中AI不应该记得之前的内容")

    def test_model_selection_functionality(self):
        """测试模型选择功能"""
        # 访问应用
        self.driver.get(self.base_url)
        
        # 等待页面加载
        self.wait.until(EC.presence_of_element_located((By.ID, "topic")))
        
        # 选择模型
        model_provider_select = self.driver.find_element(By.ID, "model_provider")
        model_provider_select.click()
        
        # 选择阿里云模型
        ali_option = self.driver.find_element(By.CSS_SELECTOR, "option[value='ali']")
        ali_option.click()
        
        # 输入模型名称
        model_name_input = self.driver.find_element(By.ID, "model_name")
        model_name_input.clear()
        model_name_input.send_keys("qwen-max")
        
        # 发送消息
        input_field = self.driver.find_element(By.ID, "topic")
        input_field.send_keys("你好，你能告诉我你是谁吗？")
        input_field.send_keys(Keys.RETURN)
        
        # 等待响应
        time.sleep(5)
        
        # 验证收到回复
        ai_messages = self.driver.find_elements(By.CLASS_NAME, "ai-message")
        self.assertGreater(len(ai_messages), 0, "应该收到AI回复")
        
        last_response = ai_messages[-1].text
        # 验证回复内容
        self.assertNotEqual(last_response.strip(), "", "AI回复不应该为空")

    def test_language_toggle_functionality(self):
        """测试语言切换功能"""
        # 访问应用
        self.driver.get(self.base_url)
        
        # 等待页面加载
        self.wait.until(EC.presence_of_element_located((By.ID, "topic")))
        
        # 切换到英文
        language_toggle = self.driver.find_element(By.ID, "language-toggle")
        language_toggle.click()
        
        # 等待语言切换
        time.sleep(2)
        
        # 验证界面元素已切换为英文
        history_title = self.driver.find_element(By.ID, "history-title")
        self.assertIn("History", history_title.text, "历史标题应该切换为英文")
        
        # 发送英文消息
        input_field = self.driver.find_element(By.ID, "topic")
        input_field.send_keys("Hello, who are you?")
        input_field.send_keys(Keys.RETURN)
        
        # 等待响应
        time.sleep(5)
        
        # 验证收到英文回复
        ai_messages = self.driver.find_elements(By.CLASS_NAME, "ai-message")
        self.assertGreater(len(ai_messages), 0, "应该收到AI回复")
        
        last_response = ai_messages[-1].text
        # 验证回复内容不为空
        self.assertNotEqual(last_response.strip(), "", "AI回复不应该为空")


if __name__ == "__main__":
    unittest.main()