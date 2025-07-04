import streamlit as st
from crew import build_crew

st.set_page_config(page_title="AI 會議助理", layout="wide")
st.title("🧠 AI 會議助理（會計師 + 律師）")

st.markdown("請輸入您的會議問題，AI 將從兩個專業角度進行分析。")

# 初始化對話紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示歷史訊息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 使用者輸入
if user_input := st.chat_input("請輸入您的會議問題..."):
    # 顯示使用者提問
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # AI 分析
    with st.chat_message("assistant"):
        with st.spinner("📊 會計師與 ⚖️ 律師正在分析中..."):
            try:
                crew, acc_task, law_task = build_crew(user_input)
                result = crew.kickoff()

                accountant_reply = acc_task.output
                lawyer_reply = law_task.output

                combined_result = f"""📊 **Accountant 回覆**：
{accountant_reply}

---

⚖️ **Lawyer 回覆**：
{lawyer_reply}
"""
                st.markdown(combined_result)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": combined_result
                })

            except Exception as e:
                error_msg = f"❌ 發生錯誤：{e}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
