#!/usr/bin/env python3
"""
使用Selenium测试记忆模块功能
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import unittest
import os


class TestMemoryModuleWithSelenium(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 尝试使用系统已安装的ChromeDriver
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            # 如果找不到ChromeDriver，尝试指定路径
            chromedriver_path = "/usr/local/bin/chromedriver"
            if os.path.exists(chromedriver_path):
                self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
            else:
                raise Exception("无法找到ChromeDriver，请确保已安装并配置正确路径")
        
        self.driver.implicitly_wait(10)  # 隐式等待10秒
        self.wait = WebDriverWait(self.driver, 10)
        
        # 应用URL
        self.base_url = "http://localhost:5001"

    def tearDown(self):
        """清理测试环境"""
        self.driver.quit()

    def test_short_term_memory_in_conversation(self):
        """测试短期记忆在对话中的作用"""
        # 访问应用
        self.driver.get(self.base_url)
        
        # 等待页面加载
        self.wait.until(EC.presence_of_element_located((By.ID, "topic")))
        
        # 发送第一条消息
        input_field = self.driver.find_element(By.ID, "topic")
        input_field.send_keys("你好，我叫小明")
        input_field.send_keys(Keys.RETURN)
        
        # 等待响应
        time.sleep(3)
        
        # 发送第二条消息，提及第一条消息中的内容
        input_field = self.driver.find_element(By.ID, "topic")
        input_field.send_keys("我刚才告诉过你我的名字吗？")
        input_field.send_keys(Keys.RETURN)
        
        # 等待响应
        time.sleep(3)
        
        # 检查AI是否记得用户的名字
        response_elements = self.driver.find_elements(By.CLASS_NAME, "ai-message")
        last_response = response_elements[-1].text.lower()
        
        # 验证AI是否提到了用户的名字
        self.assertIn("小明", last_response, "AI应该记得用户的名字")

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
        
        # 打开新会话
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
        response_elements = self.driver.find_elements(By.CLASS_NAME, "ai-message")
        last_response = response_elements[-1].text
        
        # 验证AI不记得之前的内容
        self.assertNotIn("测试消息", last_response, "新会话中AI不应该记得之前的内容")

    def test_long_term_memory_persistence(self):
        """测试长期记忆的持久性（模拟）"""
        # 这个测试比较复杂，因为它需要检查数据库中的长期记忆
        # 在实际应用中，我们可以通过特定的提示来测试AI是否能记住重要信息
        pass


if __name__ == "__main__":
    unittest.main()