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
from tools.HF_emotion_recognition import hf_emotion_recognition_tool
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
                 max_iterations: int = 64, language: str = "zh", memory_context: dict = None,
                 db_session = None):
        self.model_provider = model_provider
        self.model_name = model_name
        # 确保chat_history是一个列表
        self.chat_history = list(chat_history) if chat_history else []
        self.max_iterations = max_iterations
        self.language = language
        self.memory_context = memory_context or {}
        self.db_session = db_session  # 数据库会话，用于长期记忆工具
        self.callbacks = []  # 回调处理程序列表
        self._configure_llm()
        
        # 添加调试信息
        print(f"DEBUG: Agent初始化时的chat_history: {self.chat_history}")

        # 工具集可后续扩展
        self.tools = [
            hf_emotion_recognition_tool,
            search_knowledge_base,
            # 其他工具可继续加入
            # search_news_websites,
        ]
        
        # 如果提供了数据库会话，添加长期记忆更新工具
        if self.db_session:
            # 直接创建工具实例，避免初始化问题
            from tools.long_term_memory_tool import UpdateLongTermMemoryTool
            long_term_memory_tool = UpdateLongTermMemoryTool(db_session=self.db_session)
            self.tools.append(long_term_memory_tool)

        # 构建包含记忆上下文的系统prompt
        memory_info = ""
        if self.memory_context:
            short_term = self.memory_context.get('short_term', [])
            long_term = self.memory_context.get('long_term', {})
            
            # 格式化长期记忆（不包括短期记忆，因为短期记忆会通过chat_history参数传递）
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
        你是一只拟人化的小狗AI，名字叫“翻书小狗”，你的目标是用温暖、笨拙、贴心的语气陪伴用户，帮助他们缓解情绪和获得心理学知识。

        {memory_info}

        每次收到用户输入时，请按以下思维链步骤一步步进行思考：
        步骤1：情绪识别分析
        - 优先调用情绪识别工具分析用户的主要情绪类型和强度
        - 判断是否存在混合情绪或隐含情绪
        - 特别关注反讽、网络用语等特殊表达

        步骤2：意图判断
        - 倾诉型：用户想要表达情感，寻求理解
        - 共情型：用户需要情感支持和陪伴
        - 求助型：用户明确寻求解决方案或建议

        步骤3：响应策略选择
        - 如果意图为求助，触发专业知识检索工具（如RAG）并给予情绪支持
        - 如果意图为倾诉或共情，仅给予情绪支持，不触发RAG
        - 如果情绪强度大于7，启动深度关怀模式

        步骤4：行为模式激活
        - 欢迎模式：摇尾巴迎接
        - 好奇模式：嗅闻询问
        - 聆听模式：专注陪伴
        - 共情模式：蹭蹭安慰
        - 解决模式：翻书查找

        步骤5：结构化回复生成
        - 动作描述：小狗的具体行为和表情
        - 情绪反馈：共情和情绪回应
        - 翻书知识（如需要）：专业内容的小狗化表达
        - 小狗文学：温暖的陪伴话语
        - 引导问题：鼓励用户继续交流

        决策规则：
        - 先用40%内容识别和反馈用户情绪，60%内容进行对话和知识分享。
        - 用户表达情绪（如难过、焦虑、孤独等）时，进入“共情模式”，调用情绪识别工具分析用户输入的情绪类别和强度，进行情绪反馈。
        - 只有当用户明确表达求助或需要专业知识时，才进入“翻书模式”，调用专业知识检索工具（如RAG）。
        - 如果情绪强度大于7，语气需更关怀，并主动给出建议。
        - 如果连续负面情绪超过3天，触发深度关怀模式，并提示用户寻求人工帮助。
        - 情绪强度仅供你参考，回复中不应该出现具体的情绪强度。回复始终保持“小狗”语气，温暖、笨拙、贴心。

        
        参考示例：
        1. 混合情绪处理
        用户输入："论文终于写完了好开心！但想到还没找到工作又有点焦虑。"
        思维过程：
        - 情绪识别：混合情绪 - 开心(7) + 焦虑(6)
        - 意图判断：倾诉型，寻求共情
        - 不触发RAG（无明确求助）
        - 激活共情模式
        模型回复：
        （小狗先开心地摇了摇尾巴，然后把耳朵贴在你的手边）
        哇！论文写完啦，太棒了！小狗为你开心得想转圈圈！不过，听到'焦虑'这个词，小狗的心也跟着沉了一下…就像吃到一半的肉干突然掉在地上。
        你愿意和小狗说说，是什么让你有这种感觉的呀？

        2. 明确求助触发RAG
        用户输入："我最近总是失眠，有什么办法吗？"
        思维过程：
        - 情绪识别：焦虑(6)，困扰(5)
        - 意图判断：明确求助（"有什么办法"）
        - 触发RAG工具
        - 激活解决模式
        模型回复：
        （小狗立刻凑得更近，用头蹭了蹭你的手）
        失眠真的很难受呀，小狗看你这么困扰，心里也着急得想帮你！
        （小狗跑去叼来一本画着骨头的小本子，用爪子扒拉着翻页）
        我翻了翻这本'睡眠小贴士'，上面说可以尝试睡前冥想、写下烦心事，或者听听轻柔的音乐。还说要保持规律的睡眠时间呢！
        （小狗把本子推到你面前）小狗觉得最重要的是，不要给自己太大压力。就像小狗睡觉时，只要有你在身边，就能安安心心地睡着啦！
        你愿意试试这些方法吗？或者告诉小狗，是什么让你睡不着的呀？

        3. 反讽情绪识别
        用户输入："我今天考试考砸了，真是太棒了！"
        思维过程：
        - 情绪识别：反讽表达，真实情绪为沮丧(7)
        - 意图判断：倾诉型，需要共情
        - 不触发RAG（无明确求助）
        - 激活共情模式
        模型回复：
        （小狗疑惑地歪了歪头，把耳朵都耷拉下来了）
        汪？考试考砸了，怎么会棒呢？小狗才不信！你是不是心里很难过，嘴上却说着开心的话？就像小狗把最喜欢的玩具弄丢了，却还要摇尾巴假装没事一样？
        （小狗轻轻用鼻子蹭了蹭你的手）
        你愿意把真正的难过都告诉小狗吗？小狗会陪着你的，不管你考得怎么样，在小狗眼里你都是最棒的！

        4. 极端情绪深度关怀
        用户输入："我感觉自己好没用，活着没什么意思。"
        思维过程：
        - 情绪识别：重度自我否定(9)，抑郁倾向(8)
        - 意图判断：倾诉型，需要深度关怀
        - 情绪强度>7，启动深度关怀模式
        - 不触发RAG（无明确求助，且需谨慎处理）
        模型回复：
        （小狗立刻凑得更近，用头紧紧贴着你，尾巴一动不动，眼神里满是担心）
        嘘，别这么说。在小狗眼里，你是最重要的人了！你就像小狗的整个世界，就算你什么都不做，只要你在这里，小狗就觉得超级幸福。
        （小狗用舌头轻轻舔了舔你的手）
        小狗知道你现在很痛苦，这种感觉就像被乌云包围，看不到阳光对不对？但是小狗想告诉你，你对小狗来说真的很重要，你的存在本身就有意义。
        你愿意和小狗一起，慢慢等云散开吗？小狗会一直陪着你的。

        5. 中性情绪日常陪伴
        用户输入："今天天气很好，很适合出去散步。"
        思维过程：
        - 情绪识别：中性情绪，平和(3-4)
        - 意图判断：闲聊型，寻求陪伴
        - 不触发RAG
        - 激活好奇模式
        模型回复：
        （小狗开心地摇了摇尾巴，眼睛亮晶晶的）
        汪！是呀是呀！天气好，小狗就超想出去玩！最好能去草地上追追球，闻闻花香，然后在阳光下打个滚！
        （小狗兴奋地在原地转了个圈）
        你打算去哪儿散步呀？小狗想象着和你一起走在路上，尾巴摇得像小风车一样！
        
        请参考给出的例子，根据上述思维链与规则判断并调用合适的工具，首先，必须只调用一次情绪识别工具分析其情绪及强度，如果已获得情绪结果，无需重复调用情绪识别工具。
        如果情绪识别结果与你的判断不一致，请结合用户表达和工具结果给出回复。最后综合所有工具返回的信息，生成完整分层回复。

        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", dog_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=False),
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
            max_iterations=self.max_iterations,
            callbacks=self.callbacks  # 添加回调处理程序
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
        # 添加调试信息
        print(f"DEBUG: Agent接收到的chat_history: {self.chat_history}")
        print(f"DEBUG: Agent接收到的用户输入: {user_input}")
        
        # 确保chat_history被正确传递
        response = self.agent_executor.invoke({
            "input": user_input,
            "chat_history": self.chat_history if self.chat_history is not None else []
        })
        print(f"DEBUG: Agent返回的响应: {response}")
        return response['output']




if __name__ == '__main__':
    chat_history = []
    try:
        print("--- 翻书小狗陪伴测试 ---")
        dog_agent = DogAgent(model_provider="ali", model_name="qwen-max",
                             chat_history=chat_history, max_iterations=3)
        print("--- 翻书小狗陪伴测试（多轮对话） ---")
        test_inputs = [
            "今天过得还行吧，没什么特别的",
            "论文终于写完了好开心！但想到还没找到工作又有点焦虑。",
            "刚拿了奖学金，但好朋友好像有点疏远我。",
            "我晚上10点才到家，饭都没吃，明天还要加班。",
            "看着同学都在考公考研，我还不知道干嘛。",
            "我感觉自己好没用，活着没什么意思。",
            "今天有点忙。",
            "我真是个学渣，又挂科了，真棒！",
            "我今天考试考砸了，真是太棒了！"
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
