from crew import crew

result = crew.kickoff(
    inputs={
        "user_question": "我準備成立一家公司，請問要選擇獨資還是股份有限公司比較有利？"
    }
)

print("\n\n最終建議：\n")
print(result)
