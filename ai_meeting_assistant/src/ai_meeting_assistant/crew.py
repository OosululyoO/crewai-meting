import os
import yaml
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
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
openai_llm = ChatOpenAI(model="gpt-4", temperature=0.3)

# ---------- 建立 Agents ----------
agents = {}
for agent_id, config in agents_config.items():
    agents[agent_id] = Agent(
        config=config,
        llm=openai_llm
    )

# ---------- 建立任務流程（用程式定義） ----------
def build_crew(user_question: str):
    analyze_task = Task(
        description=(
            f"使用者輸入的問題是：\n{user_question}\n\n"
            "你是一位會計師，請從財務與稅務角度提供建議與風險分析。"
        ),
        expected_output="詳細建議與說明",
        agent=agents["accountant"]
    )

    legal_task = Task(
        description=(
            "你是律師，請根據會計師的分析結果，從法律角度補充建議，並指出潛在法律風險與合規建議。"
        ),
        expected_output="法律補充建議",
        agent=agents["lawyer"],
        context=[analyze_task]
    )

    crew = Crew(
        agents=[agents["accountant"], agents["lawyer"]],
        tasks=[analyze_task, legal_task],
        process=Process.sequential,
        verbose=True
    )
    return crew
