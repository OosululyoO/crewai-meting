import os
import yaml
from dotenv import load_dotenv

from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI  # ✅ 用正確類別

from crewai import Agent, Task, Crew, Process

# 讀取 .env 環境變數
load_dotenv()

# ---------- 讀取 YAML ----------
def load_yaml_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 設定 YAML 路徑（從 crew.py 相對位置）
this_dir = os.path.dirname(__file__)
agents_config = load_yaml_config(os.path.join(this_dir, "config/agents.yaml"))
tasks_config = load_yaml_config(os.path.join(this_dir, "config/tasks.yaml"))

# ---------- 建立 LLM ----------
openai_llm = ChatOpenAI(model_name="gpt-4", temperature=0.3)

# ✅ 使用 API KEY 存取 Gemini，不會觸發 GCP ADC 機制
gemini_llm = GoogleGenerativeAI(
    model="gemini-pro",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3
)

# ---------- 指派 LLM 到對應 agent ----------
agent_llm_map = {
    "accountant": openai_llm,
    "lawyer": gemini_llm
}

# ---------- 建立 Agents ----------
agents = {}
for agent_id, config in agents_config.items():
    agents[agent_id] = Agent(
        config=config,
        llm=agent_llm_map.get(agent_id)  # 使用者不綁 LLM OK
    )

# ---------- 建立 Tasks ----------
tasks = []
for task_id, config in tasks_config.items():
    agent = agents[config["agent"]]
    tasks.append(Task(config=config, agent=agent))

# ---------- 建立 Crew ----------
crew = Crew(
    agents=list(agents.values()),
    tasks=tasks,
    process=Process.sequential,
    verbose=True
)
