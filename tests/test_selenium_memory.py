
import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class TestChatUIMemory(unittest.TestCase):
    def setUp(self):
        """初始化浏览器驱动，打开聊天页面"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 无头模式，不在前台显示浏览器窗口
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.binary_location = "/usr/bin/google-chrome-stable"  # 指定Chrome二进制文件位置
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.driver.get("http://127.0.0.1:5000")  # 假设应用运行在5000端口
        time.sleep(2)  # 等待页面加载

    def tearDown(self):
        """关闭浏览器"""
        self.driver.quit()

    def test_chat_short_term_memory(self):
        """测试聊天机器人的短期记忆功能"""
        # 输入第一条消息
        chat_input = self.driver.find_element(By.ID, "chat-input")
        chat_input.send_keys("我喜欢蓝色")
        chat_input.send_keys(Keys.RETURN)
        time.sleep(5)  # 等待机器人回复

        # 验证第一条回复
        chat_messages = self.driver.find_elements(By.CSS_SELECTOR, ".chat-message p")
        self.assertTrue(len(chat_messages) > 1, "没有收到回复")
        
        # 输入第二条消息
        chat_input.send_keys("我最喜欢的颜色是什么？")
        chat_input.send_keys(Keys.RETURN)
        time.sleep(5)

        # 验证第二条回复
        chat_messages = self.driver.find_elements(By.CSS_SELECTOR, ".chat-message p")
        last_message = chat_messages[-1].text
        self.assertIn("蓝色", last_message, "机器人没有记住我喜欢的颜色")

if __name__ == '__main__':
    unittest.main()
