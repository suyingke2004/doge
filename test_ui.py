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

try:
    # 访问应用
    driver.get("http://localhost:5001")
    
    # 等待页面加载
    wait = WebDriverWait(driver, 10)
    
    # 检查页面标题
    assert "新闻对话" in driver.title
    print("页面标题正确")
    
    # 检查模型选择表单元素
    model_provider = wait.until(EC.presence_of_element_located((By.ID, "model-provider")))
    model_name = wait.until(EC.presence_of_element_located((By.ID, "model-name")))
    maxiter = wait.until(EC.presence_of_element_located((By.ID, "maxiter")))
    topic_input = wait.until(EC.presence_of_element_located((By.ID, "topic-input")))
    
    print("模型选择表单元素存在")
    
    # 检查模型提供商选项
    providers = [option.text for option in model_provider.find_elements(By.TAG_NAME, "option")]
    assert "DeepSeek" in providers
    assert "OpenAI" in providers
    print("模型提供商选项正确")
    
    # 检查模型名称下拉框选项（默认应该是DeepSeek的选项）
    model_options = [option.text for option in model_name.find_elements(By.TAG_NAME, "option")]
    assert "deepseek-chat (默认)" in model_options
    print("模型名称选项正确")
    
    # 检查maxiter输入框
    assert maxiter.get_attribute("type") == "number"
    assert maxiter.get_attribute("min") == "1"
    assert maxiter.get_attribute("max") == "10"
    assert maxiter.get_attribute("value") == "5"
    print("maxiter输入框配置正确")
    
    # 切换模型提供商检查模型选项是否更新
    model_provider.click()
    for option in model_provider.find_elements(By.TAG_NAME, "option"):
        if option.text == "OpenAI":
            option.click()
            break
    
    time.sleep(1)  # 等待选项更新
    
    # 检查模型名称选项是否更新为OpenAI的选项
    model_options = [option.text for option in model_name.find_elements(By.TAG_NAME, "option")]
    assert "gpt-4o (默认)" in model_options
    print("切换提供商后模型选项更新正确")
    
    print("所有UI测试通过!")
    
finally:
    # 关闭浏览器
    driver.quit()