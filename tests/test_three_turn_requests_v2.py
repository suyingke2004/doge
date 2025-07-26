import requests
import time

# 创建一个会话对象以保持cookies
session = requests.Session()

# 设置基础URL
base_url = "http://localhost:5001"

def chat_round(topic, is_first_round=False):
    """进行一轮对话"""
    if is_first_round:
        # 第一轮对话需要提供模型信息
        data = {
            'topic': topic,
            'model_provider': 'deepseek',
            'model_name': 'deepseek-chat',
            'maxiter': '5'
        }
    else:
        # 后续对话只需要提供主题
        data = {
            'topic': topic
        }
    
    # 发送POST请求
    response = session.post(f"{base_url}/chat_stream", data=data, stream=True)
    
    # 读取流式响应
    content = ""
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            try:
                # 处理可能的编码问题
                decoded_chunk = chunk.decode('utf-8')
                content += decoded_chunk
                print(decoded_chunk, end='', flush=True)
            except UnicodeDecodeError:
                # 忽略解码错误
                pass
    
    print("\n" + "="*50)
    return content

def main():
    print("=== 三轮对话测试 ===\n")
    
    # 第一轮对话
    print("--- 第一轮对话 ---")
    first_response = chat_round("简单介绍一下人工智能", is_first_round=True)
    
    # 等待一点时间确保会话状态正确设置
    time.sleep(2)
    
    # 第二轮对话
    print("\n--- 第二轮对话 ---")
    second_response = chat_round("机器学习和深度学习有什么区别？")
    
    # 等待一点时间
    time.sleep(2)
    
    # 第三轮对话
    print("\n--- 第三轮对话 ---")
    third_response = chat_round("请推荐一些学习AI的资源")
    
    print("\n=== 测试完成 ===")
    print(f"第一轮响应长度: {len(first_response)} 字符")
    print(f"第二轮响应长度: {len(second_response)} 字符")
    print(f"第三轮响应长度: {len(third_response)} 字符")

if __name__ == "__main__":
    main()