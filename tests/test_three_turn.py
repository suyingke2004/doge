import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 配置无头浏览器
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 启动浏览器
driver = webdriver.Chrome(options=chrome_options)

def get_ai_response_text():
    """获取最新的AI助手响应文本"""
    try:
        # 获取最新的AI消息容器
        ai_messages = driver.find_elements(By.CSS_SELECTOR, ".ai-message")
        if ai_messages:
            latest_ai_message = ai_messages[-1]  # 获取最后一条AI消息
            # 获取其中的文本内容
            response_div = latest_ai_message.find_element(By.CSS_SELECTOR, "div")
            return response_div.text
        return ""
    except Exception as e:
        print(f"获取AI响应时出错: {e}")
        return ""

try:
    print("=== 开始三轮对话测试 ===")
    
    # 访问应用
    driver.get("http://localhost:5001/chat_stream")
    
    # 等待页面加载
    wait = WebDriverWait(driver, 10)
    
    # 等待模型选择表单出现
    model_form = wait.until(EC.presence_of_element_located((By.ID, "model-form")))
    print("1. 模型选择表单已加载")
    
    # 选择模型提供商和模型
    model_provider = driver.find_element(By.ID, "model-provider")
    model_provider.click()
    
    # 选择DeepSeek提供商
    provider_options = model_provider.find_elements(By.TAG_NAME, "option")
    for option in provider_options:
        if option.text == "DeepSeek":
            option.click()
            break
    
    time.sleep(1)
    
    # 选择模型名称
    model_name = driver.find_element(By.ID, "model-name")
    model_name.click()
    
    # 选择默认模型
    model_options = model_name.find_elements(By.TAG_NAME, "option")
    for option in model_options:
        if "默认" in option.text:
            option.click()
            break
    
    # 设置最大迭代次数
    maxiter = driver.find_element(By.ID, "maxiter")
    maxiter.clear()
    maxiter.send_keys("3")
    
    # 第一轮对话
    print("\n--- 第一轮对话 ---")
    topic_input = driver.find_element(By.ID, "topic-input")
    topic_input.send_keys("简单介绍一下人工智能")
    
    # 提交表单
    submit_button = driver.find_element(By.CSS_SELECTOR, "#model-form button[type='submit']")
    submit_button.click()
    
    print("已提交第一轮对话请求")
    
    # 等待响应开始出现
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chat-message.ai-message")))
    print("第一轮对话响应已开始")
    
    # 等待响应完成（最长等待10秒）
    time_start = time.time()
    while time.time() - time_start < 10:
        time.sleep(1)
        # 检查是否有新内容加载
        response_text = get_ai_response_text()
        if "AI助手" in response_text and len(response_text) > 50:  # 简单判断是否已有内容
            break
    
    # 获取第一轮响应内容
    first_response = get_ai_response_text()
    print(f"第一轮响应内容（前200字符）:\n{first_response[:200]}...")
    
    # 等待聊天表单出现
    chat_form = wait.until(EC.presence_of_element_located((By.ID, "chat-form")))
    assert chat_form.is_displayed(), "聊天表单应该在第一轮对话后可见"
    print("第一轮对话完成，聊天表单已显示")
    
    # 第二轮对话
    print("\n--- 第二轮对话 ---")
    chat_topic_input = driver.find_element(By.ID, "chat-topic-input")
    chat_topic_input.send_keys("机器学习和深度学习有什么区别？")
    
    # 提交第二轮对话
    chat_submit_button = driver.find_element(By.CSS_SELECTOR, "#chat-form button[type='submit']")
    chat_submit_button.click()
    
    print("已提交第二轮对话请求")
    
    # 等待第二轮响应开始出现
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chat-message.ai-message:nth-child(4)")))
    print("第二轮对话响应已开始")
    
    # 等待响应完成（最长等待10秒）
    time_start = time.time()
    while time.time() - time_start < 10:
        time.sleep(1)
        # 检查是否有新内容加载
        response_text = get_ai_response_text()
        if "机器学习" in response_text and len(response_text) > 50:
            break
    
    # 获取第二轮响应内容
    second_response = get_ai_response_text()
    print(f"第二轮响应内容（前200字符）:\n{second_response[:200]}...")
    
    # 第三轮对话
    print("\n--- 第三轮对话 ---")
    chat_topic_input.clear()
    chat_topic_input.send_keys("请推荐一些学习AI的资源")
    
    # 提交第三轮对话
    chat_submit_button.click()
    
    print("已提交第三轮对话请求")
    
    # 等待第三轮响应开始出现
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chat-message.ai-message:nth-child(6)")))
    print("第三轮对话响应已开始")
    
    # 等待响应完成（最长等待10秒）
    time_start = time.time()
    while time.time() - time_start < 10:
        time.sleep(1)
        # 检查是否有新内容加载
        response_text = get_ai_response_text()
        if "学习" in response_text and len(response_text) > 50:
            break
    
    # 获取第三轮响应内容
    third_response = get_ai_response_text()
    print(f"第三轮响应内容（前200字符）:\n{third_response[:200]}...")
    
    # 验证聊天历史
    print("\n--- 验证聊天历史 ---")
    chat_messages = driver.find_elements(By.CSS_SELECTOR, ".chat-message")
    print(f"总共{len(chat_messages)}条消息")
    
    # 验证消息数量（应有6条：3条用户消息+3条AI消息）
    assert len(chat_messages) >= 6, f"应该至少有6条消息，实际有{len(chat_messages)}条"
    
    # 分别获取用户和AI消息
    user_messages = driver.find_elements(By.CSS_SELECTOR, ".user-message")
    ai_messages = driver.find_elements(By.CSS_SELECTOR, ".ai-message")
    print(f"用户消息: {len(user_messages)}条")
    print(f"AI消息: {len(ai_messages)}条")
    
    print("\n=== 三轮对话测试完成 ===")
    
finally:
    # 关闭浏览器
    driver.quit()