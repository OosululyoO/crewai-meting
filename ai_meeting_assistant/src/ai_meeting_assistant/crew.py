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
def build_crew(user_question: str):
    # 檢查 agents 是否已建立
    if not agents:
        raise Exception("❌ 沒有可用的 agents，請檢查 LLM 初始化")
    
    # 檢查兩個 agent 是否都可用
    if "accountant" not in agents or "lawyer" not in agents:
        raise Exception("❌ 需要會計師和律師兩個 agents 才能運作")
    
    # 會計師任務：從財務角度分析
    analyze_task = Task(
        description=f"""
        作為專業會計師，請針對以下問題從財務與稅務角度提供分析：
        
        問題：{user_question}
        
        請提供：
        1. 財務影響分析
        2. 稅務考量
        3. 風險評估
        4. 具體建議
        """,
        expected_output="詳細的財務分析報告，包含稅務建議和風險評估",
        agent=agents["accountant"]
    )

    # 律師任務：從法律角度提供意見
    legal_task = Task(
        description=f"""
        作為專業律師，請針對以下問題從法律角度提供分析：
        
        問題：{user_question}
        
        請提供：
        1. 法律風險評估
        2. 合規要求
        3. 法律結構建議
        4. 整合財務與法律的綜合建議
        """,
        expected_output="完整的法律分析報告，結合財務考量提供綜合建議",
        agent=agents["lawyer"],
        context=[analyze_task]  # 依賴會計師的分析結果
    )

    crew = Crew(
        agents=[agents["accountant"], agents["lawyer"]],
        tasks=[analyze_task, legal_task],
        process=Process.sequential,
        verbose=True
    )
    return crew

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