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

while True:
    user_question = input("請輸入您的問題（輸入 'exit' 結束程式）：\n")
    if user_question.lower() == 'exit':
        print("👋 感謝使用 AI 會議助手，再見！")
        break

    try:
        print("📝 建立 Crew...")
        crew = build_crew(user_question)

        print("🔄 執行任務...")
        result = crew.kickoff()

        print("\n✅ 最終建議輸出：\n")
        print(result)

    except Exception as e:
        print("\n❌ 執行過程中發生錯誤：")
        print(f"錯誤類型：{type(e).__name__}")
        print(f"錯誤訊息：{str(e)}")
        print("\n💡 可能的解決方案：")
        print("1. 檢查 .env 檔案中的 API 金鑰是否正確")
        print("2. 檢查網路連線")
        print("3. 確認 API 金鑰有足夠的額度")
