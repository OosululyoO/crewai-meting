import streamlit as st
import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.ai_meeting_assistant.crew import build_memory_agent_task, openai_llm

st.set_page_config(page_title="AI 輪替式會議助手", layout="wide")
st.title("🧠 AI 輪替式會議助手（含角色、主題記憶與文件分析）")

SAVE_DIR = "./saved_chats"
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------------- 預設角色設定 ----------------
default_role1 = {
    "name": "會計師",
    "backstory": "擁有豐富稅務與財務管理經驗的會計師",
    "task": "從財務與稅務角度提供建議"
}

default_role2 = {
    "name": "律師",
    "backstory": "熟悉商業合規與公司法的律師",
    "task": "從法律角度分析問題並提供建議"
}

# ---------------- 初始化 Session State ----------------
if "meeting_name" not in st.session_state:
    st.session_state.meeting_name = "未命名會議"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "role1_cfg" not in st.session_state:
    st.session_state.role1_cfg = default_role1.copy()
if "role2_cfg" not in st.session_state:
    st.session_state.role2_cfg = default_role2.copy()

# ---------------- 工具函式 ----------------
def get_output_text(output):
    if hasattr(output, "content"):
        return output.content
    elif isinstance(output, str):
        return output
    elif hasattr(output, "result"):
        return output.result
    return str(output)

def save_chat(meeting_name, chat_history):
    data = {
        "meeting_name": meeting_name,
        "chat_history": [],
        "role1_cfg": st.session_state.role1_cfg,
        "role2_cfg": st.session_state.role2_cfg
    }
    for entry in chat_history:
        clean_entry = dict(entry)
        clean_entry["reply"] = get_output_text(clean_entry["reply"])
        data["chat_history"].append(clean_entry)

    path = os.path.join(SAVE_DIR, f"{meeting_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_chat(meeting_name):
    path = os.path.join(SAVE_DIR, f"{meeting_name}.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    st.session_state.chat_history = data.get("chat_history", [])
    st.session_state.role1_cfg = data.get("role1_cfg", default_role1.copy())
    st.session_state.role2_cfg = data.get("role2_cfg", default_role2.copy())
    st.session_state.meeting_name = data.get("meeting_name", meeting_name)

def list_saved_meetings():
    return [f[:-5] for f in os.listdir(SAVE_DIR) if f.endswith(".json")]

# ---------------- Sidebar 模式與檔案上傳 ----------------
st.sidebar.header("📁 選擇對話模式")
mode = st.sidebar.radio("請選擇：", ["🆕 開啟新會議", "📂 載入過去會議"])

if mode == "📂 載入過去會議":
    saved = list_saved_meetings()
    selected = st.sidebar.selectbox("選擇過去會議：", saved)
    if st.sidebar.button("📤 載入"):
        load_chat(selected)
        st.success(f"✅ 已載入會議：{selected}")
else:
    if st.sidebar.button("🔄 重置為新會議"):
        st.session_state.meeting_name = "未命名會議"
        st.session_state.chat_history = []
        st.session_state.role1_cfg = default_role1.copy()
        st.session_state.role2_cfg = default_role2.copy()

# 📎 文件上傳
st.sidebar.header("📎 上傳輔助文件")
uploaded_files = st.sidebar.file_uploader(
    "選擇 .pdf, .docx, .xlsx 文件（可複數）",
    type=["pdf", "docx", "xlsx"],
    accept_multiple_files=True
)

uploaded_texts = []
if uploaded_files:
    for file in uploaded_files:
        try:
            if file.name.endswith(".pdf"):
                from PyPDF2 import PdfReader
                reader = PdfReader(file)
                text = "\n".join([page.extract_text() for page in reader.pages])
            elif file.name.endswith(".docx"):
                import docx
                doc = docx.Document(file)
                text = "\n".join([para.text for para in doc.paragraphs])
            elif file.name.endswith(".xlsx"):
                import pandas as pd
                df = pd.read_excel(file)
                text = df.to_markdown()
            else:
                text = f"{file.name} 格式不支援"
            uploaded_texts.append(f"📄 {file.name}:\n{text}")
        except Exception as e:
            uploaded_texts.append(f"⚠️ 無法解析 {file.name}：{e}")

doc_context = "\n\n".join(uploaded_texts)

# ---------------- Header: 主題與儲存 ----------------
st.markdown("### 💼 當前會議主題")
st.session_state.meeting_name = st.text_input("📝 會議主題", value=st.session_state.meeting_name)

col_save, _ = st.columns([1, 5])
with col_save:
    if st.button("💾 儲存目前對話", use_container_width=True):
        save_chat(st.session_state.meeting_name, st.session_state.chat_history)
        st.success(f"✅ 對話已儲存為：「{st.session_state.meeting_name}」")

# ---------------- 角色設定 ----------------
st.subheader("👥 自訂兩位角色")
col1, col2 = st.columns(2)

with col1:
    st.session_state.role1_cfg["name"] = st.text_input("角色 1 名稱", value=st.session_state.role1_cfg["name"])
    st.session_state.role1_cfg["backstory"] = st.text_area("角色 1 背景", value=st.session_state.role1_cfg["backstory"])
    st.session_state.role1_cfg["task"] = st.text_area("角色 1 任務", value=st.session_state.role1_cfg["task"])

with col2:
    st.session_state.role2_cfg["name"] = st.text_input("角色 2 名稱", value=st.session_state.role2_cfg["name"])
    st.session_state.role2_cfg["backstory"] = st.text_area("角色 2 背景", value=st.session_state.role2_cfg["backstory"])
    st.session_state.role2_cfg["task"] = st.text_area("角色 2 任務", value=st.session_state.role2_cfg["task"])

# ---------------- 問題輸入與角色按鈕 ----------------
st.subheader("💬 請輸入您的會議問題：")
user_input = st.text_input("您的問題：", value="")

col_btn1, col_btn2 = st.columns(2)
selected_role = None
role_cfg = None
run_task = False

if col_btn1.button(f"📊 {st.session_state.role1_cfg['name']}回覆", use_container_width=True) and user_input.strip():
    selected_role = st.session_state.role1_cfg["name"]
    role_cfg = st.session_state.role1_cfg
    run_task = True

if col_btn2.button(f"⚖️ {st.session_state.role2_cfg['name']}回覆", use_container_width=True) and user_input.strip():
    selected_role = st.session_state.role2_cfg["name"]
    role_cfg = st.session_state.role2_cfg
    run_task = True

# ---------------- 執行任務 ----------------
if run_task and role_cfg:
    st.session_state.chat_history.append({
        "user": user_input,
        "agent": "user",
        "reply": ""
    })

    with st.spinner(f"{selected_role} 正在分析..."):
        crew, task = build_memory_agent_task(
            user_question=user_input,
            role_name=role_cfg["name"],
            backstory=role_cfg["backstory"],
            task_instruction=role_cfg["task"],
            history_log=st.session_state.chat_history,
            llm_instance=openai_llm,
            extra_context=doc_context
        )
        result = crew.kickoff()
        reply_text = get_output_text(task.output)
        st.success(f"{selected_role} 回覆：\n\n{reply_text}")
        st.session_state.chat_history.append({
            "user": user_input,
            "agent": selected_role,
            "reply": reply_text
        })

# ---------------- 歷史對話 ----------------
st.divider()
st.subheader("🗂️ 歷史對話")
for entry in st.session_state.chat_history:
    if entry["agent"] != "user":
        st.markdown(f"**🧑‍💼 {entry['agent']} 回覆：**\n\n{entry['reply']}")
