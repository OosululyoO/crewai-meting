from crew import build_crew
import os

print("🚀 開始 AI 會議助手...")

# 檢查環境變數
openai_key = os.getenv("OPENAI_API_KEY")
google_key = os.getenv("GOOGLE_API_KEY")

if not openai_key:
    print("⚠️  警告：未找到 OPENAI_API_KEY")
if not google_key:
    print("⚠️  警告：未找到 GOOGLE_API_KEY")

# 初始化對話紀錄
conversation_history = []

# 進入互動式對話迴圈
while True:
    print("\n請輸入您的會議問題（輸入 exit 結束）：")
    user_question = input("> ").strip()

    if user_question.lower() == "exit":
        print("\n👋 感謝使用 AI 會議助理！")
        break

    if not user_question:
        print("⚠️  請輸入非空白的問題。")
        continue

    try:
        print("📝 建立 Crew...")
        crew = build_crew(user_question)

        print("🔄 執行任務中，請稍候...")
        result = crew.kickoff()

        # 儲存對話紀錄
        conversation_history.append({"question": user_question, "answer": result})

        # 顯示最新回應
        print("\n✅ 分析完成：\n")
        print(result)

        # 顯示完整對話紀錄
        print("\n📜 對話紀錄：")
        for idx, entry in enumerate(conversation_history, 1):
            print(f"{idx}. 問題：{entry['question']}")
            print(f"   回應：{entry['answer']}\n")

    except Exception as e:
        print("\n❌ 執行過程中發生錯誤：")
        print(f"錯誤類型：{type(e).__name__}")
        print(f"錯誤訊息：{str(e)}")
        print("\n💡 可能的解決方案：")
        print("1. 檢查 .env 檔案中的 API 金鑰是否正確")
        print("2. 檢查網路連線")
        print("3. 確認 API 金鑰有足夠的額度")
