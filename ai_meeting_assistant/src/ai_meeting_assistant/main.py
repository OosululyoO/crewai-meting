from crew import crew

result = crew.kickoff(
    inputs={
        "user_question": "我想開公司，應該設立獨資、合夥還是有限公司？"
    }
)

print("\n\n✅ 最終建議：\n")
print(result)
