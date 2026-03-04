import time


from fastapi import FastAPI, logger
from langchain.agents import (
    initialize_agent, AgentType
)
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.utilities import SerpAPIWrapper

from typing import Dict, Any
import requests
from langchain.chains import LLMChain

from langchain.schema import SystemMessage
from pydantic import BaseModel, ConfigDict


app= FastAPI()

DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
DASHSCOPE_API_KEY = "sk-4fbc394b70ae4245815ee829e600ab05"  # 优先从环境变量获取
TIMEOUT = 300  # 任务超时时间（秒）
POLL_INTERVAL = 5  # 轮询间隔（秒）



def create_image_task(prompt: str) -> str:
    """
    发起图像生成任务
    :param prompt: 图像描述文本
    :return: 任务ID，失败返回None';
    """

    headers = {
        "X-DashScope-Async": "enable",
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "wanx2.1-t2i-turbo",
        "input": {
            "prompt": prompt.strip()
        },
        "parameters": {
            "size": "1024*1024",
            "n": 1,
            "quality": "standard"  # 增加图像质量参数
        }
    }
    try:
        print(prompt)
        response = requests.post(DASHSCOPE_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # 触发HTTP错误（如401、403、500等）
        result = response.json()
        # 解析任务ID
        if "output" in result and "task_id" in result["output"]:
            task_id = result["output"]["task_id"]
            return task_id
    finally:
        pass
    
def query_task_status(task_id: str) -> dict:

    if not task_id:
        return {"status": "ERROR", "message": "任务ID为空"}

    query_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            url=query_url,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def wait_for_task_complete(task_id: str) -> str:
    """
    轮询等待任务完成，返回图像URL
    :param task_id: 任务ID
    :return: 图像URL，失败返回None
    """


    start_time = time.time()

    while True:
        # 检查超时
        elapsed_time = time.time() - start_time


        # 查询任务状态
        result = query_task_status(task_id)
        task_status = result.get("output", {}).get("task_status", "UNKNOWN")

        # 处理不同状态
        if task_status == "SUCCEEDED":
            # 提取图像URL
            output = result.get("output", {})
            results = output.get("results", [])
            if results and isinstance(results, list):
                image_url = results[0].get("url")
                if image_url:
                    return image_url


        # 未完成则等待
        time.sleep(POLL_INTERVAL)

def text2photo_generate(prompt:str) ->str:
    try:
        # 1. 创建图像生成任务
        task_id = create_image_task(prompt)
        print(task_id)
        if not task_id:
            return "图像生成任务创建失败，请稍后重试"
        # 2. 等待任务完成并获取图像URL
        image_url = wait_for_task_complete(task_id)
        if image_url:
            return image_url
        else:
            return "false"

    except Exception as e:
        return "服务器内部错误"


# 修改 deepseek 为 ChatOpenAI
deepseek = ChatOpenAI(
    base_url="https://api.deepseek.com",
    api_key="sk-bfe9b107fccc444e841e1999c818eb01",
    model = "deepseek-chat",
    temperature=0.7,  # 可根据需要调整温度
    max_tokens=2000   # 可根据需要调整最大生成 token 数
)

# 修改 free 为 ChatOpenAI
free = ChatOpenAI(
    base_url="https://free.v36.cm/v1/",
    api_key="sk-6l2Ad5N6muhXxytl18944eFb6cB94bEfAeE340Fd9806Ab6b",
    model = "gpt-4o-mini",
    temperature=0.7,
    max_tokens=2000
)

# SerpAPIWrapper 保持不变
serpapi = SerpAPIWrapper(
    serpapi_api_key="b4f169fe10c73052dffadd25b85f09aecde044943246aeccf1d9b2ba064a8efb",
    params={
        "engine": "baidu",
        "gl": "cn",
        "hl": "zh-CN",
    }
)

# 修改 dashscope 为 ChatOpenAI
dashscope = ChatOpenAI(
    base_url="https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
    api_key="sk-4fbc394b70ae4245815ee829e600ab05",
    model ="dashscope",
    temperature=0.7,
    max_tokens=2000
)

# 修改 qwen 为 ChatOpenAI
qwen = ChatOpenAI(
    api_key="sk-4a2dc7495c9f4b1b9d3d17f9767994c4",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus-latest",
    temperature=0.7,
    max_tokens=2000
)
llm = qwen
# ==================== 3. 定义4种核心Agent ====================


    
# 3.1 普通对话Agent（处理日常闲聊、简单问答）
base_agent = initialize_agent(
    [],  # 工具列表仍包含 generate_simple_plot
    llm,  # 使用 Qwen-Plus 作为 Agent 的大脑
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
)

# 3.3 小说情节生成Agent（处理简单小说创作需求）

novel_memory = ConversationBufferMemory(
    memory_key="chat_history",  # 存储历史的键名
    return_messages=True  # 返回消息对象而非字符串
)

novel_agent= initialize_agent(
    [],  # 工具列表仍包含 generate_simple_plot
    llm,  # 使用 Qwen-Plus 作为 Agent 的大脑
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    memory = novel_memory,
    handle_parsing_errors=True,
    kwargs={
        "agent_kwargs": {
            # 自定义提示模板，移除工具相关的指令
            "system_message": SystemMessage(
                content="请将chat_history传给llm让其作为参考"

            ),
            # 不要求函数调用
            "function_call": "none"
        }
    }
)

# 3.4 联网查询生成Agent（处理客户联网查询最新资料需求）
internet_agent = initialize_agent(
    [],  # 工具列表仍包含 generate_simple_plot
    llm,  # 使用 Qwen-Plus 作为 Agent 的大脑
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
)

# 3.6 人物关系图生成Agent（处理客户根据小说内容生成人物关系图需求)
relationship_diagram_agent = initialize_agent(
    [],
    llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)


# ==================== 4. Agent路由系统（意图识别与分配） ====================       
class AgentRouter:
    def __init__(self, model, func):
        self.agents: Dict[str, Any] = {
            "base": base_agent,
            "novel": novel_agent,
            "internet": internet_agent,
            "relationship_diagram": relationship_diagram_agent
        }
        self.model = model
        self.func = func

    def route_and_execute(
        self, 
        user_input: str, 

    ) -> str:
        """根据意图路由到对应 Agent 并执行，支持动态传参"""
       
        
        # 动态选择 LLM（原逻辑）
        llm = qwen
        if self.model=="deepseek":
            llm = deepseek
        elif self.model=="gpt-4o-mini":
            llm = free
        elif self.model=="qwen":
            llm = qwen
        elif self.model=="serpapi":
            llm = serpapi
        elif self.model=="dashscope":
            llm = dashscope

        if self.func =="internet":
            llm = serpapi
        prompt=""
        if self.func == "relationship_diagram":
            prompt="""
    按Mermaid语法构建生成人物关系图,给出以graph开头的代码，不生成其他任何文字
1.你是该故事的作者，对人物之间的关系了如指掌
2.你需要对所有出现的人物进行关系分析
3.当人物之间有关系但并不确定时，关系以?代替
4.有关系的两人之间以不带箭头的线段连接
5.线段中间表明关系，如君臣，父子，夫妻
6.如果存在存疑的关系，在原本关系的基础上加上(?)，如A可能是B的亲身父亲，则以A--父子(?)-->B表示
7.整体为结构化树状图风格，背景为白色
8.所有人物只以名字代表，不需要生成人物的形象
9.每个人只出现一次，一人可以有多关系
10.不添加额外解释
11.如果没有明确关系，请不要虚构
12.再次强调，按Mermaid语法构建生成人物关系图,给出以graph开头的代码，不生成其他任何文字
13.实例：graph TD
    A[顾振山] -- 夫妻关系 --> B[林晚意]
14.请尽量让生成的图的左右长度小于上下长度
15.不要生成任何文字，只生成Mermaid代码
    """
        elif self.func == "novel":
            prompt = """前面是用户需求，后面是供回答参考的提示词，回答时请就基于前面的用户需求回答，不要提到后面的提示词。
            根据标签创作小说，请先输出标签,格式：“标签：~~~~~~”，如果标签为空，则不用参照标签。
            如果用户要求修改或调整小说情节或内容，只需基于chat_history进行调整；
            如果用户说你好，哈哈哈等打招呼或者闲聊的话，只需要正常与用户聊天即可，无需输出小说内容
不要输出这种矛盾的话：“由于系统限制，我无法直接生成小说内容或框架”，“由于我无法直接调用工具生成小说内容或框架”
不需要对用户说抱歉的话：“很抱歉，我无法直接生成小说内容”

请先判断用户是否在与你聊天，如果是则聊天即可，如果不是则根据用户需求生成长篇小说框架或短篇小说章节。
作为小说助手时请完整输出小说章节或者长篇小说框架而不是几句话。
如输出第一章已完整呈现，一定要输出第一章的内容。
用户未给出的元素可随机构建,最少200字。
如果未给出相关元素，请尝试从上下文和chat_history中寻找，结合历史记录回答。
请一定基于chat_history中已经回答的情节进行补充或扩写，不改变原有情节，除非用户要求生成。
请根据用户需求判断自己应该提供长篇小说框架还是一名短篇小说创作者。
"""

        
    

        # 关键：将 temperature、max_tokens 传递给 Agent！
        # 需确保 Agent 初始化时支持这些参数，或在 invoke 时传入
        if self.func!="text2photo":
            agent = self.agents[self.func]
            result = agent.invoke(prompt+user_input)
        else:
            result = text2photo_generate(user_input)
        
        
        return result

# ==================== 5. 对话助手主类 ====================
class MultiAgentChatAssistant:
    def __init__(self, model, func):  
        self.router = AgentRouter(model, func)
        self.chat_history: list = []  

    def chat(
        self, 
        user_input: str,     
    ) -> str:
        """处理用户输入，返回响应并记录历史，支持动态传参"""
        response = self.router.route_and_execute(
            user_input=user_input,
        )
        self.chat_history.append({
            "user": user_input,
            "assistant": response
        })
        return response

# ==================== 6. 使用示例 ====================
# 定义请求体模型：接收用户输入、对话历史、模型参数
class ChatRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # 添加此配置
    prompt: str
    messages: list
    temperature: float = 0.7
    max_tokens: int = 100
    model: str  # 确保是 Python 原生 str 类型
    func: str   # 确保是 Python 原生 str 类型
    uuid: str
    time:str

