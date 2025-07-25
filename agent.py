import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from tools import news_tools
from tools.reddit_search import reddit_search_tool

# 加载环境变量
load_dotenv()

# 定义常见的模型提供商和默认模型
MODEL_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "default_model": "gpt-4o",
        "base_url": None
    },
    "deepseek": {
        "name": "DeepSeek",
        "default_model": "deepseek-chat",
        "base_url": "https://api.deepseek.com/v1"
    },
    "zhipu": {
        "name": "Zhipu AI",
        "default_model": "glm-4",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/"
    },
    "ali": {
        "name": "Alibaba Cloud",
        "default_model": "qwen-max",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    },
    "moonshot": {
        "name": "Moonshot AI",
        "default_model": "moonshot-v1-8k",
        "base_url": "https://api.moonshot.cn/v1"
    }
}

class NewsletterAgent:
    """
    一个能够研究主题并生成新闻通讯的AI代理。
    现在支持对话记忆和流式输出。
    """
    def __init__(self, model_provider: str = "deepseek", model_name: str = None, chat_history: list = None, max_iterations: int = 5):
        """
        初始化代理。
        :param model_provider: 要使用的语言模型提供商。
        :param model_name: 要使用的具体模型名称，如果未提供则使用默认模型。
        :param chat_history: 一个包含对话历史的列表。
        :param max_iterations: 代理执行的最大迭代次数。
        """
        self.model_provider = model_provider
        self.model_name = model_name
        self.chat_history = chat_history or []
        self.max_iterations = max_iterations
        self._configure_llm()

        # 2. 定义工具集
        self.tools = [
            news_tools.search_news,
            news_tools.scrape_article_content,
            reddit_search_tool.search_reddit
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
            max_iterations=self.max_iterations
        )

    def _configure_llm(self):
        """根据选择的提供商配置语言模型"""
        # 获取提供商信息
        provider_info = MODEL_PROVIDERS.get(self.model_provider)
        if not provider_info:
            raise ValueError(f"不支持的模型提供商: {self.model_provider}")
            
        # 获取API密钥
        api_key_env_var = f"{self.model_provider.upper()}_API_KEY"
        api_key = os.getenv(api_key_env_var)
        if not api_key:
            raise ValueError(f"未找到 {api_key_env_var}，请在 .env 文件中配置。")
            
        # 确定模型名称
        model = self.model_name if self.model_name else provider_info["default_model"]
        
        # 配置LLM
        llm_kwargs = {
            "model": model,
            "temperature": 0.7,
            "max_tokens": 4096,
            "api_key": api_key
        }
        
        # 如果有base_url，添加到配置中
        if provider_info["base_url"]:
            llm_kwargs["base_url"] = provider_info["base_url"]
            
        self.llm = ChatOpenAI(**llm_kwargs)

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
        import asyncio  # 确保导入asyncio
        
        # 初始化一个变量来收集完整的响应
        full_response = ""
        
        try:
            async for chunk in self.agent_executor.astream({
                "input": topic,
                "chat_history": self.chat_history
            }):
                # 只返回最终输出的流，忽略中间步骤
                if "output" in chunk:
                    # 累积响应内容
                    output = chunk["output"]
                    full_response += output
                    
                    # 检查是否是最大迭代次数的消息
                    if "agent stopped due to max iterations" in output.lower():
                        # 当达到最大迭代次数时，给出总结性信息
                        summary_msg = "\n\n[已达到最大迭代次数限制，正在为您总结当前已获取的信息...]\n"
                        yield summary_msg
                        
                        # 收集到目前为止的所有输出内容
                        # 如果已经有内容，则进行总结；否则提供一般性说明
                        if full_response.strip() and not full_response.lower().endswith("agent stopped due to max iterations."):
                            # 创建一个总结提示，包含到目前为止的所有内容
                            summary_prompt = f"基于以上对话内容，请简洁总结已获取的信息来回答最初的问题：{topic}\n\n已获取的内容：{full_response}"
                        else:
                            # 如果还没有获取到内容，则提供一般性说明
                            summary_prompt = f"在尝试回答问题'{topic}'时，已经达到了最大迭代次数限制。请基于你已有的知识提供一个简洁的回答。"
                        
                        try:
                            # 使用LLM生成总结
                            summary_response = self.llm.invoke([
                                *self.chat_history,
                                HumanMessage(content=summary_prompt)
                            ])
                            
                            # 流式输出总结内容
                            summary_content = summary_response.content
                            for i in range(0, len(summary_content), 10):
                                yield summary_content[i:i+10]
                                # 添加一个小延迟以模拟流式效果
                                await asyncio.sleep(0.01)
                        except Exception as summary_error:
                            # 如果总结过程也出错，则提供一个简单的错误信息
                            error_msg = f"\n\n[抱歉，在总结信息时遇到问题: {summary_error}]"
                            yield error_msg
                    else:
                        yield output
                elif "actions" in chunk:
                    # 这里可以处理工具调用的流式输出（如果需要显示工具调用过程）
                    # 暂时我们只关注最终输出
                    pass
                elif "steps" in chunk:
                    # 这里可以处理中间步骤的流式输出（如果需要显示推理过程）
                    # 暂时我们只关注最终输出
                    pass
        except Exception as e:
            # 处理其他异常
            print(f"捕获到异常: {type(e).__name__}: {e}")
            raise

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
