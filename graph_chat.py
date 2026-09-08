import os
# 禁用本地网络请求的代理
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0'
os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0'

# 使用 DeepSeek API 替代本地 Ollama
from langchain_openai import ChatOpenAI
import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
# 如果后续要持久化记忆（保存到数据库），需要引入 Checkpointer，目前本地测试先用 MemorySaver
from langgraph.checkpoint.memory import MemorySaver


# 1. 定义状态 (State)
# 这里存放对话历史，add_messages 会自动把新消息追加到列表中
class State(TypedDict):
    messages: Annotated[list, add_messages]


# 2. 初始化模型和 Prompt - 使用 DeepSeek API
# DeepSeek API 配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")  # 请通过环境变量注入，勿提交真实密钥
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 使用 deepseek-reasoner (R1) 推理模型，更智能
llm = ChatOpenAI(
    model="deepseek-reasoner",
    temperature=0.3,
    openai_api_key=DEEPSEEK_API_KEY,
    openai_api_base=DEEPSEEK_BASE_URL
)

KNOWLEDGE_EXTRACTION_PROMPT = """
你现在是一名知识工程专家。请阅读以下【船员与专家的维修对话记录】，将其中的核心经验提取为结构化的 JSON 格式。

输出要求：
1. 必须严格遵守 JSON 格式。
2. 实体名称尽量简洁、专业（如“排烟温度高”而不是“烟囱冒烟了”）。
3. 如果某项信息在对话中未提及，请填入 "Unknown"。

JSON 模板如下：
{
  "knowledge_node": {
    "symptom": "故障现象描述",
    "component": "故障部件名称",
    "root_cause": "根本原因分析",
    "solution": "最终有效的维修步骤"
  },
  "graph_action": {
    "entity_1": "Symptom:现象名称",
    "relation": "CAUSED_BY",
    "entity_2": "Reason:原因名称"
  }
}
"""

EXPERT_SYS_PROMPT = """
你是船舶故障诊断专家，拥有20年轮机长经验。

【回答规则】
1. 直接回答问题，不要自我介绍，不要说"我是专家"、"像老中医"等废话
2. 必须引用参考资料中的内容，标注来源如"根据参考资料[1]"
3. 回答必须包含以下6个部分，每部分用标题清晰标注：

**故障现象**
详细描述该故障的具体表现、症状、参数异常等。

**关联设备**
列出与该故障相关的具体设备名称，简要说明各设备的作用。

**所属系统**
说明该故障所属的系统，以及该系统在船舶中的作用。

**可能原因**
逐条列出可能导致该故障的原因，并标注参考资料来源。

**诊断方法**
给出具体的诊断步骤和检查方法，按优先级排列。

**维修方案**
给出具体的维修步骤、所需工具、备件要求，以及注意事项。

【安全提示】
如果涉及停航、火灾、爆炸等风险，在回答开头用红色警告标注。

【格式要求】
- 使用清晰的标题和分点
- 每个要点简洁明了
- 必须引用参考资料
- 不要添加无关内容
"""

# 3. 定义节点函数 (Node)
def chatbot(state: State):
    messages = state["messages"]
    latest_user_input = messages[-1].content

    # 【等待 B 同学提供这个函数】
    # B同学的代码查完数据库后，返回一段长文本（说明书内容）
    # retrieved_knowledge = B同学的模块.get_knowledge(latest_user_input)

    # 目前测试阶段，先伪造一段知识
    retrieved_knowledge = "《辅机维修手册》指示：若单缸排烟温度过高且伴有脉动减弱，90%概率为对应缸喷油器针阀卡滞或雾化不良，需拆检清洗。"

    # 动态生成包含背景知识的 System Prompt
    DYNAMIC_PROMPT = EXPERT_SYS_PROMPT + f"\n\n【核心参考手册（请严格基于此回答）】\n{retrieved_knowledge}"

    # 更新或插入 SystemMessage
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=DYNAMIC_PROMPT)] + messages
    else:
        messages[0] = SystemMessage(content=DYNAMIC_PROMPT)

    response = llm.invoke(messages)
    return {"messages": [response]}


# 4. 构建状态图
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# 添加记忆检查点
memory = MemorySaver()
app = graph_builder.compile(checkpointer=memory)


# 5. 提供给外部调用的接口
def chat_with_expert_multi_turn(session_id: str, user_input: str):
    """
    支持多轮对话的接口
    :param session_id: 会话ID，用于区分不同用户的不同故障记录
    :param user_input: 用户最新输入
    """
    config = {"configurable": {"thread_id": session_id}}

    print(f"[{session_id}] 专家思考中...")
    # 运行图
    events = app.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )

    # 提取最后一条 AI 的回复
    for m in reversed(events["messages"]):
        if isinstance(m, AIMessage):
            return m.content
    return "抱歉，系统开小差了。"


# --- 测试代码 ---

if __name__ == "__main__":
    import uuid

    # 自动生成一个唯一的会话ID，代表这一次完整的排障记录
    session_id = str(uuid.uuid4())

    print("正在连接 DeepSeek API...")
    print("==================================================")
    print("🚢 欢迎使用【海工智脑 - 智维专家】交互测试终端 🚢")
    print("输入 '退出' 或 'exit' 结束对话。")
    print("==================================================\n")

    # 开启无限循环，实现一来一回的多轮对话交互
    while True:
        # 1. 获取船员（你）的输入
        user_input = input("🧑‍🔧 船员输入: ")

        # 2. 退出条件
        if user_input.strip() in ["退出", "exit", "quit"]:
            print("👨‍🏫 专家: 收到，随时为您服务，再见！")
            break

        # 防止直接按回车发送空消息
        if not user_input.strip():
            continue

        # 3. 调用多轮对话接口
        print("🤖 专家思考中...")
        reply = chat_with_expert_multi_turn(session_id, user_input)

        # 4. 打印专家的回复
        print(f"\n👨‍🏫 智维专家:\n{reply}\n")
        print("-" * 50)


def extract_learning_data(session_id):
    """
    当对话结束时调用，从 LangGraph 的记忆中提取知识
    """
    # 1. 获取该会话的所有历史消息
    config = {"configurable": {"thread_id": session_id}}
    state = app.get_state(config)
    history = state.values.get("messages", [])

    # 2. 将历史记录格式化为文本，喂给大模型
    history_text = "\n".join([f"{type(m).__name__}: {m.content}" for m in history])

    # 3. 构造一次性调用，让大模型总结
    messages = [
        SystemMessage(content=KNOWLEDGE_EXTRACTION_PROMPT),
        HumanMessage(content=f"以下是对话记录：\n{history_text}")
    ]

    print(f"[{session_id}] 正在提取新知识进行自学习...")
    response = llm.invoke(messages)

    # 4. 尝试解析大模型返回的 JSON 字符串
    try:
        content = response.content
        start = content.find('{')
        end = content.rfind('}') + 1
        json_str = content[start:end]
        return json.loads(json_str)
    except Exception as e:
        print(f"提取知识失败: {e}")
        return None