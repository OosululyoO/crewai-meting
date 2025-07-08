import streamlit as st
from crew import build_custom_crew  # 要改 crew.py，見下方

st.set_page_config(page_title="🧠 AI 多角色會議助手", layout="wide")
st.title("🧠 AI 多角色會議助手")

st.markdown("請自訂兩位角色的名稱、背景與任務，然後輸入會議問題進行分析。")

# 🧩 角色 1 設定
st.subheader("🧑‍💼 角色 1")
role1_name = st.text_input("角色 1 名稱", value="行銷顧問")
role1_backstory = st.text_area("角色 1 背景", value="擅長品牌策略與行銷分析的顧問，具有豐富產品上市經驗。")
role1_task = st.text_area("角色 1 任務", value="請從行銷策略與市場分析角度分析問題。")

# 🧩 角色 2 設定
st.subheader("🧑‍💼 角色 2")
role2_name = st.text_input("角色 2 名稱", value="法務顧問")
role2_backstory = st.text_area("角色 2 背景", value="熟悉合約與智慧財產權的律師，專注於商業合規。")
role2_task = st.text_area("角色 2 任務", value="請從法律與合約風險角度提供意見。")

# 問題輸入
user_input = st.chat_input("請輸入您的會議問題...")
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("兩位角色正在分析中..."):
            try:
                crew, task1, task2 = build_custom_crew(
                    user_question=user_input,
                    role1={
                        "name": role1_name,
                        "backstory": role1_backstory,
                        "task": role1_task
                    },
                    role2={
                        "name": role2_name,
                        "backstory": role2_backstory,
                        "task": role2_task
                    }
                )
                result = crew.kickoff()

                reply = f"""🧑‍💼 **{role1_name} 回覆**：
{task1.output}

---

🧑‍💼 **{role2_name} 回覆**：
{task2.output}
"""
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            except Exception as e:
                error_msg = f"❌ 發生錯誤：{e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
