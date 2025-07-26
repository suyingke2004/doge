import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# 配置无头浏览器
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 启动浏览器
driver = webdriver.Chrome(options=chrome_options)

try:
    # 访问应用
    driver.get("http://localhost:5001/chat_stream")
    
    # 等待页面加载
    wait = WebDriverWait(driver, 10)
    
    # 等待模型选择表单出现
    model_form = wait.until(EC.presence_of_element_located((By.ID, "model-form")))
    print("模型选择表单已加载")
    
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
    
    # 输入主题
    topic_input = driver.find_element(By.ID, "topic-input")
    topic_input.send_keys("人工智能的最新发展")
    
    # 提交表单
    submit_button = driver.find_element(By.CSS_SELECTOR, "#model-form button[type='submit']")
    submit_button.click()
    
    print("已提交第一轮对话请求")
    
    # 等待响应开始出现
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chat-message.ai-message")))
    print("第一轮对话响应已开始")
    
    # 等待一定时间让响应完成（模拟用户阅读时间）
    time.sleep(5)
    
    # 检查是否有聊天表单出现（表示第一轮对话完成）
    chat_form = wait.until(EC.presence_of_element_located((By.ID, "chat-form")))
    # 确保聊天表单是可见的
    assert chat_form.is_displayed(), "聊天表单应该在第一轮对话后可见"
    print("第一轮对话完成，聊天表单已显示")
    
    # 进行第二轮对话
    chat_topic_input = driver.find_element(By.ID, "chat-topic-input")
    chat_topic_input.send_keys("能详细说说自然语言处理方面的进展吗？")
    
    # 提交第二轮对话
    chat_submit_button = driver.find_element(By.CSS_SELECTOR, "#chat-form button[type='submit']")
    chat_submit_button.click()
    
    print("已提交第二轮对话请求")
    
    # 等待第二轮响应开始出现
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chat-message.ai-message:nth-child(4)")))
    print("第二轮对话响应已开始")
    
    # 等待一定时间让响应完成
    time.sleep(5)
    
    # 检查聊天历史是否正确显示
    chat_messages = driver.find_elements(By.CSS_SELECTOR, ".chat-message")
    assert len(chat_messages) >= 4, f"应该至少有4条消息（用户2条，AI助手2条），实际有{len(chat_messages)}条"
    print(f"聊天历史正确显示，共有{len(chat_messages)}条消息")
    
    # 验证消息类型
    user_messages = driver.find_elements(By.CSS_SELECTOR, ".user-message")
    ai_messages = driver.find_elements(By.CSS_SELECTOR, ".ai-message")
    assert len(user_messages) >= 2, f"应该至少有2条用户消息，实际有{len(user_messages)}条"
    assert len(ai_messages) >= 2, f"应该至少有2条AI消息，实际有{len(ai_messages)}条"
    print("消息类型正确")
    
    print("多轮对话测试通过!")
    
finally:
    # 关闭浏览器
    driver.quit()