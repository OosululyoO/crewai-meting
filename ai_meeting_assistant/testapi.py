import os
import google.generativeai as genai
from dotenv import load_dotenv

# 載入 .env 取得 API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# 確認 API Key 是否成功載入 (僅供測試用，實際應用時不要將金鑰直接印出)
print(f"API Key: {'已載入' if api_key else '未載入'}")

# 設定 Gemini API Key
genai.configure(api_key=api_key)

# 嘗試使用另一個已知的支援 generateContent 的模型
model = genai.GenerativeModel("gemini-1.5-pro")

response = model.generate_content("請用一句話介紹你自己")

print("✅ Gemini 回應：", response.text)