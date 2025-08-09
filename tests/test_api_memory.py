
import unittest
import requests
import json

class TestApiMemory(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://127.0.0.1:5000"
        self.chat_url = f"{self.base_url}/chat_stream"
        self.session = requests.Session()

    def tearDown(self):
        self.session.close()

    def test_chat_api_short_term_memory(self):
        """测试聊天API的短期记忆功能"""
        self.session.get(self.base_url)  # 建立会话
        # 第一次交互：告诉机器人我喜欢蓝色
        data1 = {'topic': '我喜欢蓝色'}
        response1 = self.session.post(self.chat_url, data=data1)
        self.assertEqual(response1.status_code, 200)

        # 第二次交互：问机器人我最喜欢的颜色是什么
        data2 = {'topic': '我最喜欢的颜色是什么？'}
        response2 = self.session.post(self.chat_url, data=data2)
        self.assertEqual(response2.status_code, 200)

        # 解析第二次的流式响应
        full_response = ""
        for line in response2.iter_lines():
            if line:
                try:
                    json_line = json.loads(line.decode('utf-8'))
                    if json_line.get('type') == 'output':
                        full_response += json_line.get('content', '')
                except json.JSONDecodeError:
                    continue

        # 验证响应中是否包含“蓝色”
        self.assertIn("蓝色", full_response, "机器人没有记住我喜欢的颜色")

if __name__ == '__main__':
    unittest.main()
