import os
import yaml
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, Task, Crew, Process

# 讀取環境變數
load_dotenv()

# ---------- 讀取 YAML ----------
def load_yaml_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

this_dir = os.path.dirname(__file__)
agents_config = load_yaml_config(os.path.join(this_dir, "config/agents.yaml"))

# ---------- 建立 LLM ----------
try:
    openai_llm = ChatOpenAI(
        model="gpt-4o",  # 使用 .env 中定義的模型
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    print("✅ OpenAI LLM 初始化成功")
except Exception as e:
    print(f"❌ OpenAI LLM 初始化失敗: {e}")
    openai_llm = None

# 為了穩定性，暫時兩個 agent 都使用 OpenAI
try:
    openai_llm_lawyer = ChatOpenAI(
        model="gpt-4o",  # 使用相同的模型但不同的實例
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    print("✅ Lawyer OpenAI LLM 初始化成功")
except Exception as e:
    print(f"❌ Lawyer OpenAI LLM 初始化失敗: {e}")
    openai_llm_lawyer = None

# Gemini LLM 暫時作為備用
try:
    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",  # 簡化模型名稱
        temperature=0.3,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    print("✅ Gemini LLM 初始化成功")
except Exception as e:
    print(f"❌ Gemini LLM 初始化失敗: {e}")
    gemini_llm = None

# ---------- 建立 Agents ----------
agents = {}

# 會計師使用 OpenAI
if openai_llm is not None:
    agents["accountant"] = Agent(
        config=agents_config["accountant"],
        llm=openai_llm,
        verbose=True
    )
    print("✅ Accountant agent 創建成功")
else:
    print("❌ 無法創建 Accountant agent - OpenAI LLM 未初始化")

# 律師優先使用專用的 OpenAI 實例確保穩定性
if openai_llm_lawyer is not None:
    agents["lawyer"] = Agent(
        config=agents_config["lawyer"],
        llm=openai_llm_lawyer,  # 使用專用的 OpenAI 實例
        verbose=True
    )
    print("✅ Lawyer agent (OpenAI) 創建成功")
elif gemini_llm is not None:
    agents["lawyer"] = Agent(
        config=agents_config["lawyer"],
        llm=gemini_llm,
        verbose=True
    )
    print("✅ Lawyer agent (Gemini) 創建成功")
else:
    print("❌ 無法創建 Lawyer agent - 所有 LLM 都未初始化")

# ---------- 建立任務流程（用程式定義） ----------
def build_crew(user_question: str, accountant_backstory=None, accountant_task=None,
               lawyer_backstory=None, lawyer_task=None):
    if not agents or "accountant" not in agents or "lawyer" not in agents:
        raise Exception("❌ 必須有會計師和律師 agents")

    # 如果使用者自訂了 backstory，動態更新
    if accountant_backstory:
        agents["accountant"].config.backstory = accountant_backstory
    if lawyer_backstory:
        agents["lawyer"].config.backstory = lawyer_backstory

    # 動態任務說明
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

from crewai import Agent

def build_custom_crew(user_question: str, role1: dict, role2: dict):
    # LLM 初始化（你已有 openai_llm）
    agent1 = Agent(
        role=role1["name"],
        goal=role1["task"],
        backstory=role1["backstory"],
        llm=openai_llm,
        verbose=True
    )
    agent2 = Agent(
        role=role2["name"],
        goal=role2["task"],
        backstory=role2["backstory"],
        llm=openai_llm_lawyer or openai_llm,
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


# 增加測試執行區塊
if __name__ == "__main__":
    print("\n--- 正在測試 CrewAI 簡化任務 ---")
    try:
        # 使用一個簡短且無爭議的問題來測試
        test_crew = build_crew("測試問題。")
        result = test_crew.kickoff()
        print("\n--- Crew AI 處理結果 ---")
        print(result)
        print("✅ CrewAI 簡化任務測試成功！")
    except Exception as e:
        print(f"❌ CrewAI 簡化任務測試失敗：{e}")
        print("如果這裡仍然是 BadRequestError，問題可能更複雜。")