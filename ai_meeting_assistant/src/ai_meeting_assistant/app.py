import streamlit as st
import os
import json
from crew import build_memory_agent_task, openai_llm

st.set_page_config(page_title="AI 輪替式會議助手", layout="wide")
st.title("🧠 AI 輪替式會議助手（上下文記憶 + 儲存功能）")

# 儲存路徑
SAVE_DIR = "./saved_chats"
os.makedirs(SAVE_DIR, exist_ok=True)

# 儲存與載入功能
def list_saved_meetings():
    return [f[:-5] for f in os.listdir(SAVE_DIR) if f.endswith(".json")]

def save_chat(meeting_name, chat_history):
    path = os.path.join(SAVE_DIR, f"{meeting_name}.json")
    clean_history = []
    for entry in chat_history:
        clean_entry = dict(entry)
        if not isinstance(clean_entry["reply"], str):
            try:
                clean_entry["reply"] = clean_entry["reply"].content
            except:
                clean_entry["reply"] = str(clean_entry["reply"])
        clean_history.append(clean_entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean_history, f, ensure_ascii=False, indent=2)

def load_chat(meeting_name):
    path = os.path.join(SAVE_DIR, f"{meeting_name}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- Sidebar: 載入或新會議 ---
st.sidebar.header("📁 選擇對話模式")
mode = st.sidebar.radio("請選擇：", ["🆕 開啟新會議", "📂 載入過去會議"])

if mode == "🆕 開啟新會議":
    if "meeting_name" not in st.session_state:
        st.session_state.meeting_name = "未命名會議"
        st.session_state.chat_history = []
else:
    saved = list_saved_meetings()
    selected = st.sidebar.selectbox("選擇過去會議：", saved)
    if st.sidebar.button("📤 載入"):
        st.session_state.chat_history = load_chat(selected)
        st.session_state.meeting_name = selected
        st.success(f"✅ 已載入會議：{selected}")


# --- Header: 會議主題名稱 + 儲存按鈕 ---
st.markdown("### 💼 當前會議主題")
st.session_state.meeting_name = st.text_input("📝 會議主題", value=st.session_state.get("meeting_name", "未命名會議"))

col_save, _ = st.columns([1, 5])
with col_save:
    if st.button("💾 儲存目前對話", use_container_width=True):
        save_chat(st.session_state.meeting_name, st.session_state.chat_history)
        st.success(f"✅ 對話已儲存為：「{st.session_state.meeting_name}」")

# --- 自訂角色 ---
st.subheader("👥 自訂兩位角色")
col1, col2 = st.columns(2)
with col1:
    role1_name = st.text_input("角色 1 名稱", value="會計師")
    role1_backstory = st.text_area("角色 1 背景", value="擁有豐富稅務與財務管理經驗的會計師")
    role1_task = st.text_area("角色 1 任務", value="從財務與稅務角度提供建議")
with col2:
    role2_name = st.text_input("角色 2 名稱", value="律師")
    role2_backstory = st.text_area("角色 2 背景", value="熟悉商業合規與公司法的律師")
    role2_task = st.text_area("角色 2 任務", value="從法律角度分析問題並提供建議")

# --- 問題輸入與角色按鈕 ---
st.subheader("💬 請輸入您的會議問題：")
user_input = st.text_input("您的問題：", value="")

col_btn1, col_btn2 = st.columns(2)
selected_role = None
role_cfg = None
run_task = False

if col_btn1.button(f"📊 {role1_name}回覆", use_container_width=True) and user_input.strip():
    selected_role = role1_name
    role_cfg = {"name": role1_name, "backstory": role1_backstory, "task": role1_task}
    run_task = True

if col_btn2.button(f"⚖️ {role2_name}回覆", use_container_width=True) and user_input.strip():
    selected_role = role2_name
    role_cfg = {"name": role2_name, "backstory": role2_backstory, "task": role2_task}
    run_task = True

# --- 執行任務並記錄歷史 ---
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
            llm_instance=openai_llm
        )
        result = crew.kickoff()
        reply_text = str(task.output.content if hasattr(task.output, "content") else task.output)
        st.success(f"{selected_role} 回覆：\n\n{reply_text}")
        st.session_state.chat_history.append({
            "user": user_input,
            "agent": selected_role,
            "reply": reply_text
        })

# --- 歷史回顧 ---
st.divider()
st.subheader("🗂️ 歷史對話")
for entry in st.session_state.chat_history:
    if entry["agent"] != "user":
        st.markdown(f"**🧑‍💼 {entry['agent']} 回覆：**\n{entry['reply']}")
