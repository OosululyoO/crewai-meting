import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai # 用於 ListModels 檢查

# 載入環境變數
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# 再次確認 API Key 是否成功載入
print(f"API Key: {'已載入' if api_key else '未載入'}")

# 設定 Gemini API Key (對 ChatGoogleGenerativeAI 也有幫助，確保底層配置正確)
genai.configure(api_key=api_key)

print("\n--- 檢查可用的 Gemini 模型 ---")
found_target_model = False
target_model_name = "models/gemini-1.5-pro" # 你正在使用的模型
for m in genai.list_models():
    if m.name == target_model_name and "generateContent" in m.supported_generation_methods:
        print(f"✅ 模型 {target_model_name} 已找到並支援 generateContent。")
        found_target_model = True
        break
    elif m.name == target_model_name:
        print(f"❌ 模型 {target_model_name} 已找到，但**不支援** generateContent。")
        print(f"支援方法：{m.supported_generation_methods}")
        found_target_model = True
        break

if not found_target_model:
    print(f"❌ 模型 {target_model_name} 在您的 API 權限下未找到。")
    print("請確認模型名稱是否正確，或檢查區域可用性。")

print("-----------------------------\n")


# 獨立測試 ChatGoogleGenerativeAI
if found_target_model:
    try:
        print("--- 獨立測試 ChatGoogleGenerativeAI ---")
        gemini_llm_test = ChatGoogleGenerativeAI(
            model=target_model_name,
            temperature=0.3
        )
        test_message = "請用一句話介紹你自己。"
        response = gemini_llm_test.invoke(test_message) # 使用 invoke 方法
        print("✅ ChatGoogleGenerativeAI 獨立測試成功！")
        print("回應:", response.content)
        print("--------------------------------------\n")
    except Exception as e:
        print(f"❌ ChatGoogleGenerativeAI 獨立測試失敗：{e}")
        print("這表示問題可能在 LangChain 整合層或底層 Gemini API 請求本身。")
else:
    print("由於目標模型未找到或不支援，無法進行 ChatGoogleGenerativeAI 的獨立測試。")