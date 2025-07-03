from crew import build_crew

user_question = "我打算開一家公司，要選擇有限公司還是獨資？"

crew = build_crew(user_question)

result = crew.kickoff()
print("\n✅ 最終建議輸出：\n")
print(result)
