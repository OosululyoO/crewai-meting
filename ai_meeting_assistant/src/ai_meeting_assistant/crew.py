import os
import yaml
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from .tools.web_search_tool import WebSearchTool

# 🔌 載入環境變數
load_dotenv()

# 📁 載入 YAML 設定
def load_yaml_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

this_dir = os.path.dirname(__file__)
agents_config = load_yaml_config(os.path.join(this_dir, "config/agents.yaml"))

# 🔮 LLM 初始化
try:
    openai_llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    print("✅ OpenAI LLM 初始化成功")
except Exception as e:
    print(f"❌ OpenAI LLM 初始化失敗: {e}")
    openai_llm = None

try:
    openai_llm_lawyer = ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    print("✅ Lawyer OpenAI LLM 初始化成功")
except Exception as e:
    print(f"❌ Lawyer OpenAI LLM 初始化失敗: {e}")
    openai_llm_lawyer = None

# 🧰 導入自定工具
web_search_tool = WebSearchTool()

# 🤖 建立 Agents
agents = {}

if openai_llm is not None:
    agents["accountant"] = Agent(
        role=agents_config["accountant"]["role"],
        goal=agents_config["accountant"]["goal"],
        backstory=agents_config["accountant"]["backstory"],
        llm=openai_llm,
        tools=[web_search_tool],
        verbose=True
    )
    print("✅ Accountant agent 創建成功")
else:
    print("❌ 無法創建 Accountant agent - OpenAI LLM 未初始化")

if openai_llm_lawyer is not None:
    agents["lawyer"] = Agent(
        role=agents_config["lawyer"]["role"],
        goal=agents_config["lawyer"]["goal"],
        backstory=agents_config["lawyer"]["backstory"],
        llm=openai_llm_lawyer,
        tools=[web_search_tool],
        verbose=True
    )
    print("✅ Lawyer agent (OpenAI) 創建成功")
else:
    print("❌ 無法創建 Lawyer agent - OpenAI LLM 未初始化")

# 🧠 組裝預設任務流程
def build_crew(user_question: str, accountant_backstory=None, accountant_task=None,
               lawyer_backstory=None, lawyer_task=None):
    if not agents or "accountant" not in agents or "lawyer" not in agents:
        raise Exception("❌ 必須有會計師和律師 agents")

    if accountant_backstory:
        agents["accountant"].config.backstory = accountant_backstory
    if lawyer_backstory:
        agents["lawyer"].config.backstory = lawyer_backstory

    analyze_task = Task(
        description=f"{accountant_task or '請從財務與稅務角度提供建議與風險分析。'}\n\n問題：{user_question}",
        expected_output="詳細的財務分析報告，包含稅務建議和風險評估",
        agent=agents["accountant"]
    )

    legal_task = Task(
        description=f"{lawyer_task or '請從法律角度提供建議與合規分析，並結合財務考量。'}\n\n問題：{user_question}",
        expected_output="完整的法律分析報告，結合財務考量提供綜合建議",
        agent=agents["lawyer"],
        context=[analyze_task]
    )

    crew = Crew(
        agents=[agents["accountant"], agents["lawyer"]],
        tasks=[analyze_task, legal_task],
        process=Process.sequential,
        verbose=True
    )
    return crew, analyze_task, legal_task

# 🧩 客製兩角色流程
def build_custom_crew(user_question: str, role1: dict, role2: dict):
    agent1 = Agent(
        role=role1["name"],
        goal=role1["task"],
        backstory=role1["backstory"],
        llm=openai_llm,
        tools=[web_search_tool],
        verbose=True
    )
    agent2 = Agent(
        role=role2["name"],
        goal=role2["task"],
        backstory=role2["backstory"],
        llm=openai_llm_lawyer or openai_llm,
        tools=[web_search_tool],
        verbose=True
    )

    task1 = Task(
        description=f"{role1['task']}\n\n問題：{user_question}",
        expected_output="完整分析建議",
        agent=agent1
    )

    task2 = Task(
        description=f"{role2['task']}\n\n問題：{user_question}",
        expected_output="結合第一位角色意見的分析與建議",
        agent=agent2,
        context=[task1]
    )

    crew = Crew(
        agents=[agent1, agent2],
        tasks=[task1, task2],
        process=Process.sequential,
        verbose=True
    )
    return crew, task1, task2

# 🧠 記憶型單 agent 模式
def build_memory_agent_task(
    user_question: str,
    role_name: str,
    backstory: str,
    task_instruction: str,
    history_log: list,
    llm_instance
):
    history = ""
    for entry in history_log:
        history += f"- 使用者：{entry['user']}\n"
        history += f"  {entry['agent']} 回覆：{entry['reply']}\n"

    agent = Agent(
        role=role_name,
        goal=task_instruction,
        backstory=backstory,
        llm=llm_instance,
        tools=[web_search_tool],
        verbose=True
    )

    task = Task(
        description=f"""你是 {role_name}，請根據以下歷史對話與使用者的新問題進行回覆：

{history}

🔎 使用者的新提問：
{user_question}
""",
        expected_output="請提供專業且有上下文連貫的回應建議",
        agent=agent
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    return crew, task


# ✅ 快速測試（可略過）
if __name__ == "__main__":
    print("\n--- 正在測試 CrewAI 任務 ---")
    try:
        test_crew, task1, task2 = build_crew("現在查一下台灣最低工資是多少")
        result = test_crew.kickoff()
        print("\n--- 測試成功 ---")
        print(result)
    except Exception as e:
        print(f"❌ 測試失敗：{e}")
