import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from tools import news_tools

# 加载环境变量
load_dotenv()

class NewsletterAgent:
    """
    一个能够研究主题并生成新闻通讯的AI代理。
    现在支持对话记忆和流式输出。
    """
    def __init__(self, model_provider: str = "openai", chat_history: list = None):
        """
        初始化代理。
        :param model_provider: 要使用的语言模型提供商 ('openai' 或 'deepseek')。
        :param chat_history: 一个包含对话历史的列表。
        """
        self.model_provider = model_provider
        self.chat_history = chat_history or []
        self._configure_llm()

        # 2. 定义工具集
        self.tools = [
            news_tools.search_news,
            news_tools.scrape_article_content
        ]

        # 3. 创建包含聊天记录占位符的提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个强大的新闻研究助理。你的任务是根据用户指定的主题和之前的对话内容，搜集相关信息，并生成一份简洁、引人入胜且信息丰富的新闻通讯或回答。请先使用工具收集信息，然后整合信息并输出最终的报告。"),
            MessagesPlaceholder(variable_name="chat_history"),
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
        根据给定主题和对话历史生成回应。
        """
        response = self.agent_executor.invoke({
            "input": topic,
            "chat_history": self.chat_history
        })
        return response['output']

    async def generate_newsletter_stream(self, topic: str):
        """
        根据给定主题和对话历史生成回应，并以流式方式返回。
        """
        async for chunk in self.agent_executor.astream({
            "input": topic,
            "chat_history": self.chat_history
        }):
            # 只返回最终输出的流，忽略中间步骤
            if "output" in chunk:
                yield chunk["output"]
            elif "actions" in chunk:
                # 这里可以处理工具调用的流式输出（如果需要显示工具调用过程）
                # 暂时我们只关注最终输出
                pass
            elif "steps" in chunk:
                # 这里可以处理中间步骤的流式输出（如果需要显示推理过程）
                # 暂时我们只关注最终输出
                pass

# 主程序入口（用于测试对话记忆功能）
if __name__ == '__main__':
    
    chat_history = []
    
    try:
        # ---- 第一轮对话 ----
        print("--- 正在使用 DeepSeek 进行第一轮对话 ---")
        agent_turn_1 = NewsletterAgent(model_provider="deepseek", chat_history=chat_history)
        
        first_question = "简单介绍一下最近关于苹果公司的主要新闻"
        print(f"用户提问: {first_question}")
        
        response_1 = agent_turn_1.generate_newsletter(first_question)
        
        print("\n" + "="*50)
        print("AI 回答 (第一轮):")
        print("="*50)
        print(response_1)

        # 更新聊天记录
        chat_history.append(HumanMessage(content=first_question))
        chat_history.append(AIMessage(content=response_1))

        print("\n" + "="*70 + "\n")

        # ---- 第二轮对话（追问） ----
        print("--- 正在使用 DeepSeek 进行第二轮对话（追问） ---")
        # 传入更新后的 chat_history
        agent_turn_2 = NewsletterAgent(model_provider="deepseek", chat_history=chat_history)

        second_question = "很好，那关于他们的 AI 战略，有更详细的分析吗？"
        print(f"用户追问: {second_question}")

        response_2 = agent_turn_2.generate_newsletter(second_question)

        print("\n" + "="*50)
        print("AI 回答 (第二轮):")
        print("="*50)
        print(response_2)

    except ValueError as e:
        print(f"测试失败: {e}")
