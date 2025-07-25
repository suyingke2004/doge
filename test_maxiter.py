import requests
import time

# 创建一个会话对象以保持cookies
session = requests.Session()

# 设置基础URL
base_url = "http://localhost:5001"

def test_maxiter_behavior():
    """测试达到最大迭代次数时的行为"""
    print("\n--- 测试达到最大迭代次数时的行为 ---")
    print("请求主题: 详细介绍人工智能的最新发展")
    
    # 第一轮对话需要提供模型信息，设置maxiter为1以快速测试
    data = {
        'topic': '详细介绍人工智能的最新发展',
        'model_provider': 'deepseek',
        'model_name': 'deepseek-chat',
        'maxiter': '1'
    }
    print(f"发送数据: {data}")
    
    # 发送POST请求
    try:
        response = session.post(f"{base_url}/chat_stream", data=data, stream=True)
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        # 检查是否有错误
        if response.status_code != 200:
            print(f"错误: HTTP {response.status_code}")
            return ""
            
        # 读取流式响应
        content = ""
        chunk_count = 0
        for chunk in response.iter_content(chunk_size=1024):
            chunk_count += 1
            if chunk:
                try:
                    # 处理可能的编码问题
                    decoded_chunk = chunk.decode('utf-8')
                    content += decoded_chunk
                    # 打印前几个块的内容以调试
                    if chunk_count <= 10:
                        print(f"响应块 {chunk_count}: {repr(decoded_chunk[:100])}")
                except UnicodeDecodeError:
                    # 忽略解码错误
                    print(f"块 {chunk_count}: 解码错误")
                    pass
        
        print(f"总共接收到 {chunk_count} 个块")
        print(f"响应内容长度: {len(content)} 字符")
        
        # 如果内容太短，可能是错误信息
        if len(content) < 20:
            print(f"注意: 响应内容可能异常: {repr(content)}")
            
        return content
    except Exception as e:
        print(f"请求过程中出现异常: {e}")
        return ""

def main():
    print("=== 测试达到最大迭代次数时的处理 ===")
    
    # 测试达到最大迭代次数时的行为
    response = test_maxiter_behavior()
    
    print("\n=== 测试完成 ===")
    print(f"响应长度: {len(response)} 字符")
    if response:
        print("响应内容预览:")
        print(response[:500] + ("..." if len(response) > 500 else ""))

if __name__ == "__main__":
    main()