import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import news_tools

# 加载环境变量
load_dotenv()

class NewsletterAgent:
    """
    一个能够研究主题并生成新闻通讯的AI代理。
    """
    def __init__(self):
        # 验证 API 密钥是否存在
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("未找到 OPENAI_API_KEY，请在 .env 文件中配置。")
        
        # 1. 设置语言模型
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0.7,
            max_tokens=4096
        )

        # 2. 定义工具集
        self.tools = [
            news_tools.search_news,
            news_tools.scrape_article_content
        ]

        # 3. 创建更适合工具调用模型的提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个强大的新闻研究助理。你的任务是根据用户指定的主题，搜集相关信息，并生成一份简洁、引人入胜且信息丰富的新闻通讯。请先使用工具收集信息，然后整合信息并输出最终的新闻通讯稿。"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # 4. 创建并绑定代理
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # 5. 创建代理执行器
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

    def generate_newsletter(self, topic: str) -> str:
        """
        根据给定主题生成新闻通讯。
        """
        response = self.agent_executor.invoke({
            "input": topic
        })
        return response['output']

# 主程序入口（用于测试）
if __name__ == '__main__':
    # 创建代理实例
    newsletter_agent = NewsletterAgent()
    
    # 定义一个测试主题
    test_topic = "自动驾驶技术的商业化前景"
    
    # 生成新闻通讯
    print(f"正在研究主题: {test_topic}")
    newsletter = newsletter_agent.generate_newsletter(test_topic)
    
    # 打印结果
    print("\n" + "="*50)
    print("生成的新闻通讯:")
    print("="*50)
    print(newsletter)
