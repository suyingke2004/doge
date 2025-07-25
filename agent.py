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
    def __init__(self, model_provider: str = "openai"):
        """
        初始化代理。
        :param model_provider: 要使用的语言模型提供商 ('openai' 或 'deepseek')。
        """
        self.model_provider = model_provider
        self._configure_llm()

        # 2. 定义工具集
        self.tools = [
            news_tools.search_news,
            news_tools.scrape_article_content
        ]

        # 3. 创建提示模板
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

    def _configure_llm(self):
        """根据选择的提供商配置语言模型"""
        if self.model_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("未找到 OPENAI_API_KEY，请在 .env 文件中配置。")
            self.llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.7,
                max_tokens=4096,
                api_key=api_key
            )
        elif self.model_provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("未找到 DEEPSEEK_API_KEY，请在 .env 文件中配置。")
            self.llm = ChatOpenAI(
                model="deepseek-chat",
                temperature=0.7,
                max_tokens=4096,
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"
            )
        else:
            raise ValueError(f"不支持的模型提供商: {self.model_provider}")

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
    # ---- 使用 OpenAI 测试 ----
    print("--- 正在使用 OpenAI (GPT-4o) ---")
    try:
        openai_agent = NewsletterAgent(model_provider="openai")
        test_topic_openai = "AI 在生物医药领域的应用"
        print(f"正在研究主题: {test_topic_openai}")
        newsletter_openai = openai_agent.generate_newsletter(test_topic_openai)
        print("\n" + "="*50)
        print("生成的新闻通讯 (OpenAI):")
        print("="*50)
        print(newsletter_openai)
    except ValueError as e:
        print(f"OpenAI 测试失败: {e}")

    print("\n" + "="*70 + "\n")

    # ---- 使用 DeepSeek 测试 ----
    print("--- 正在使用 DeepSeek (DeepSeek-Chat) ---")
    try:
        deepseek_agent = NewsletterAgent(model_provider="deepseek")
        test_topic_deepseek = "自动驾驶技术的商业化前景"
        print(f"正在研究主题: {test_topic_deepseek}")
        newsletter_deepseek = deepseek_agent.generate_newsletter(test_topic_deepseek)
        print("\n" + "="*50)
        print("生成的新闻通讯 (DeepSeek):")
        print("="*50)
        print(newsletter_deepseek)
    except ValueError as e:
        print(f"DeepSeek 测试失败: {e}")
