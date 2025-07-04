import os
import datetime

# 設定根目錄（你要輸出的資料夾）
root_folder = './'  # ← 請改成你自己的資料夾路徑
output_file = 'all_code.txt'
output_file = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M')}_{output_file}"

# 設定輸出資料夾
output_folder = './coderocord/'
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.join(output_folder, output_file)

def prompt_user(path):
    rel_path = os.path.relpath(path, root_folder)
    while True:
        choice = input(f"是否要輸出 '{rel_path}' 的內容？(Y/N): ").strip().upper()
        if choice in ['Y', 'N']:
            return choice == 'Y'
        print("請輸入 Y 或 N。")

with open(output_file, 'w', encoding='utf-8') as out:
    for name in os.listdir(root_folder):
        full_path = os.path.join(root_folder, name)

        if prompt_user(full_path):
            if os.path.isfile(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        out.write(f"\n\n=== {name} ===\n")
                        out.write(f.read())
                except Exception as e:
                    out.write(f"\n\n=== {name} ===\n")
                    out.write(f"[無法讀取此檔案: {e}]\n")

            elif os.path.isdir(full_path):
                for foldername, _, filenames in os.walk(full_path):
                    for filename in filenames:
                        file_path = os.path.join(foldername, filename)
                        rel = os.path.relpath(file_path, root_folder)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                out.write(f"\n\n=== {rel} ===\n")
                                out.write(f.read())
                        except Exception as e:
                            out.write(f"\n\n=== {rel} ===\n")
                            out.write(f"[無法讀取此檔案: {e}]\n")

print(f"\n✅ 輸出完成，請查看 {output_file}")
