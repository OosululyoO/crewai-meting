import os
from crew import build_custom_crew

print("🚀 AI 多角色會議助手 CLI 版本")

# 檢查 API 金鑰
openai_key = os.getenv("OPENAI_API_KEY")
google_key = os.getenv("GOOGLE_API_KEY")

if not openai_key:
    print("⚠️  警告：未找到 OPENAI_API_KEY")
if not google_key:
    print("⚠️  警告：未找到 GOOGLE_API_KEY")

# 自訂兩位角色
print("\n👥 請設定第 1 位角色：")
role1_name = input("角色名稱（預設：會計顧問）: ").strip() or "會計顧問"
role1_backstory = input("背景描述（預設：擅長稅務與財務分析）: ").strip() or "擅長稅務與財務分析"
role1_task = input("任務說明（預設：從財務角度提供建議）: ").strip() or "從財務角度提供建議"

print("\n👥 請設定第 2 位角色：")
role2_name = input("角色名稱（預設：法律顧問）: ").strip() or "法律顧問"
role2_backstory = input("背景描述（預設：擅長公司法與合規分析）: ").strip() or "擅長公司法與合規分析"
role2_task = input("任務說明（預設：從法律角度提供建議）: ").strip() or "從法律角度提供建議"

# 啟動互動模式
conversation_history = []

while True:
    print("\n💬 請輸入您的會議問題（輸入 exit 結束）：")
    user_question = input("> ").strip()

    if user_question.lower() == "exit":
        print("\n👋 感謝使用 AI 助手！")
        break

    if not user_question:
        print("⚠️  請輸入非空白的問題。")
        continue

    try:
        print("🧠 建立多角色分析任務...")
        crew, task1, task2 = build_custom_crew(
            user_question=user_question,
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

        print("🔍 分析中，請稍候...\n")
        result = crew.kickoff()

        # 儲存紀錄
        conversation_history.append({
            "question": user_question,
            "reply1": task1.output,
            "reply2": task2.output
        })

        print(f"🧑‍💼 {role1_name} 回覆：\n{task1.output}\n")
        print(f"🧑‍💼 {role2_name} 回覆：\n{task2.output}\n")

        # 總結紀錄
        print("📜 對話紀錄：")
        for idx, conv in enumerate(conversation_history, 1):
            print(f"{idx}. 問題：{conv['question']}")
            print(f"   {role1_name}：{conv['reply1'][:60]}...")
            print(f"   {role2_name}：{conv['reply2'][:60]}...\n")

    except Exception as e:
        print("\n❌ 發生錯誤：")
        print(f"錯誤類型：{type(e).__name__}")
        print(f"錯誤訊息：{e}")
        print("💡 檢查 API 金鑰與連線狀態")
