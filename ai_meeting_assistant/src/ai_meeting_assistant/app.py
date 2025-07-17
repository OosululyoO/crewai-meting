import streamlit as st
import os
import json
from src.ai_meeting_assistant.crew import build_memory_agent_task, openai_llm

#  streamlit run src/ai_meeting_assistant/app.py

st.set_page_config(page_title="AI 輪替式會議助手", layout="wide")
st.title("🧠 AI 輪替式會議助手（單一角色 + 上下文記憶）")

# 角色設定
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

# 初始化對話歷史
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 🔹 不使用 key，改用 local 變數接輸入
st.subheader("💬 請輸入您的會議問題：")
user_input = st.text_input("您的問題：", value="")

# 角色按鈕
col_btn1, col_btn2 = st.columns(2)
selected_role = None
role_cfg = None
run_task = False

if col_btn1.button(f"📊 {role1_name}回覆", use_container_width=True) and user_input.strip():
    selected_role = role1_name
    role_cfg = {
        "name": role1_name,
        "backstory": role1_backstory,
        "task": role1_task
    }
    run_task = True

if col_btn2.button(f"⚖️ {role2_name}回覆", use_container_width=True) and user_input.strip():
    selected_role = role2_name
    role_cfg = {
        "name": role2_name,
        "backstory": role2_backstory,
        "task": role2_task
    }
    run_task = True

# 🔁 執行任務邏輯
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

        st.success(f"{selected_role} 回覆：\n\n{task.output}")
        st.session_state.chat_history.append({
            "user": user_input,
            "agent": selected_role,
            "reply": task.output
        })

# 🧾 對話歷史區塊
st.divider()
st.subheader("🗂️ 歷史對話")
for entry in st.session_state.chat_history:
    if entry["agent"] != "user":
        st.markdown(f"**🧑‍💼 {entry['agent']} 回覆：**\n{entry['reply']}")
