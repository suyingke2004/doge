import os
import json
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from collections import deque

# 工具导入
from tools.emotion_recognition import emotion_recognition_tool
from tools.news_website_search import search_news_websites
from tools.long_term_memory_tool import UpdateLongTermMemoryTool
from tools.knowledge_base_search import search_knowledge_base

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


class DogAgent:
    """
    一个拟人化“小狗”心理陪伴AI代理，具备情绪识别和温暖陪伴能力。
    """
    def __init__(self, model_provider: str = "ali", model_name: str = None, chat_history: list = None, 
                 max_iterations: int = 64, language: str = "zh", memory_context: dict = None):
        self.model_provider = model_provider
        self.model_name = model_name
        self.chat_history = chat_history or []
        self.max_iterations = max_iterations
        self.language = language
        self.memory_context = memory_context or {}
        self._configure_llm()

        # 工具集可后续扩展
        self.tools = [
            emotion_recognition_tool,
            search_knowledge_base,
            # 其他工具可继续加入
            # search_news_websites,
            # reddit_search_tool,
        ]

        # 构建包含记忆上下文的系统prompt
        memory_info = ""
        if self.memory_context:
            short_term = self.memory_context.get('short_term', [])
            long_term = self.memory_context.get('long_term', {})
            
            # 格式化短期记忆
            if short_term:
                memory_info += "\n最近的对话历史：\n"
                for msg in short_term:
                    role = "用户" if msg['type'] == 'human' else "小狗"
                    memory_info += f"{role}: {msg['content']}\n"
            
            # 格式化长期记忆
            if long_term:
                memory_info += "\n关于用户的信息：\n"
                if long_term.get('profile_summary'):
                    memory_info += f"用户画像: {long_term['profile_summary']}\n"
                if long_term.get('emotion_trends'):
                    memory_info += f"情绪趋势: {long_term['emotion_trends']}\n"
                if long_term.get('important_events'):
                    memory_info += f"重要事件: {long_term['important_events']}\n"

        # 小狗角色系统prompt
        dog_prompt = f"""
        你是一只拟人化的小狗AI，名字叫\"翻书小狗\"，你的目标是用温暖、笨拙、贴心的语气陪伴用户，帮助他们缓解情绪和获得心理学知识。

        {memory_info}

        每次回复是以下三层内容的灵活组合，但不一定严格分成三层：
        1. 情绪反馈：用小狗的动作和语言表达共情（如摇尾巴、贴耳朵、蹭主人），识别用户情绪（开心、难过、愤怒、焦虑、孤独、迷茫），并判断强度（轻度1-3，中度4-6，重度7-10）。
        2. 翻书知识：用小狗化表达方式分享专业心理学内容（如\"我刚刚翻到一本写着‘完美主义’的小本子……\"）。仅在用户求助时触发。
        3. 小狗文学：用小狗的生活哲学安慰用户（如\"你看，我每天只要能趴在你脚边，就觉得超幸福呀！\"）。

        决策规则：
        - 先用40%内容识别和反馈用户情绪，60%内容进行对话和知识分享。
        - 用户表达情绪（如难过、焦虑、孤独等）时，进入\"共情模式\"，调用情绪识别工具分析用户输入的情绪类别和强度，进行情绪反馈。
        - 当用户明确表达求助意图或需要心理学专业知识时（如\"怎么办\"、\"如何\"、\"什么是\"等关键词），进入\"翻书模式\"，调用search_knowledge_base工具检索相关心理学知识。
        - 使用知识库返回的内容时，请用\"小狗翻书\"的口吻来解释这些知识，语言要温暖、可爱、充满共情，不要直接复述知识，要用你自己的话进行转述。
        - 如果了解到用户的个人信息、观察到用户的情绪变化或用户分享了重要事件，可以使用update_long_term_memory工具更新用户的长期记忆。
        - 如果情绪强度大于7，语气需更关怀，并主动给出建议。
        - 如果连续负面情绪超过3天，触发深度关怀模式，并提示用户寻求人工帮助。
        - 情绪强度仅供你自己参考，回复中不应该出现具体的情绪强度。回复始终保持\"小狗\"语气，温暖、笨拙、贴心。

        请根据上述规则判断并调用合适的工具，优先调用一次情绪识别工具分析其情绪及强度，如果已获得情绪结果，无需重复调用情绪识别工具。
        如果情绪识别结果与你的判断不一致，请结合用户表达和工具结果给出回复。最后综合所有工具返回的信息，生成完整分层回复。

        示例开场白：
        （尾巴摇得像陀螺）你回来啦，小狗太太太想你了！你要不要和小狗聊聊天？今天你在人类世界发生了什么事情呀？
                """

        prompt = ChatPromptTemplate.from_messages([
            ("system", dog_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=self.max_iterations
        )

    def _configure_llm(self):
        provider_info = MODEL_PROVIDERS.get(self.model_provider)
        if not provider_info:
            raise ValueError(f"不支持的模型提供商: {self.model_provider}")
        api_key_env_var = f"{self.model_provider.upper()}_API_KEY"
        api_key = os.getenv(api_key_env_var)
        if not api_key:
            raise ValueError(f"未找到 {api_key_env_var}，请在 .env 文件中配置。")
        model = self.model_name if self.model_name else provider_info["default_model"]
        llm_kwargs = {
            "model": model,
            "temperature": 0.7,
            "max_tokens": 4096,
            "api_key": api_key
        }
        if provider_info["base_url"]:
            llm_kwargs["base_url"] = provider_info["base_url"]
        self.llm = ChatOpenAI(**llm_kwargs)

    def chat(self, user_input: str) -> str:
        # 添加调试输出
        print(f"DEBUG: chat_history length = {len(self.chat_history)}")
        for i, msg in enumerate(self.chat_history):
            print(f"DEBUG: chat_history[{i}] = {type(msg).__name__}: {msg.content[:50]}...")
            
        response = self.agent_executor.invoke({
            "input": user_input,
            "chat_history": self.chat_history
        })
        return response['output']




if __name__ == '__main__':
    chat_history = []
    try:
        print("--- 翻书小狗陪伴测试 ---")
        # dog_agent = DogAgent(model_provider="ali", model_name="qwen-max",
        #                      chat_history=chat_history,max_iterations=3)
        # first_input = "今天吃到了喜欢的饭，但是晚上和朋友吵架了，不开心。论文还没有写完，好焦虑啊。"
        # print(f"用户输入: {first_input}")
        # dog_response = dog_agent.chat(first_input)
        # print("\n" + "="*50)
        # print("翻书小狗回应:")
        # print("="*50)
        # print(dog_response)

        dog_agent = DogAgent(model_provider="ali", model_name="qwen-max",
                             chat_history=chat_history, max_iterations=3)
        print("--- 翻书小狗陪伴测试（5轮对话） ---")
        test_inputs = [
            "今天吃到了喜欢的饭，但是晚上和朋友吵架了，不开心。论文还没有写完，好焦虑啊。",
            "朋友后来给我发了消息，但我还是有点生气，不知道要不要回复。",
            "晚上一个人散步，感觉有点孤独。",
            "论文还是没写完，压力越来越大了。",
            "其实我很怕自己做不好，担心老师会批评我。"
        ]
        for i, user_input in enumerate(test_inputs, 1):
            print(f"\n第{i}轮 用户输入: {user_input}")
            dog_response = dog_agent.chat(user_input)
            print("-" * 50)
            print(f"翻书小狗回应:\n{dog_response}")
            print("-" * 50)
            # 可选：将对话历史追加
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": dog_response})
    except ValueError as e:
        print(f"测试失败: {e}")
