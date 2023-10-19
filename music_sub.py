import os
from datetime import datetime

#파일 이름 재설정 함수
def rename_files(folder_path, target_name, new_name):
    file_list = os.listdir(folder_path)

    for file_name in file_list:
        if file_name.startswith(target_name):
            file_path = os.path.join(folder_path, file_name)
            new_file_name = file_name.replace(target_name, new_name)
            new_file_path = os.path.join(folder_path, new_file_name)

            os.rename(file_path, new_file_path)
            print(f"파일 이름 변경: {file_name} -> {new_file_name}")

#파일 이름 변경 함수
def sanitize_filename(filename):
    return filename.replace('/', '-')

# 로그 파일 이름을 현재 날짜로 생성하는 함수
def get_log_file_name():
    current_date = datetime.now().strftime("%Y-%m-%d")  # "YYYY-MM-DD" 형식으로 포맷팅
    return f"log/log_{current_date}.txt"
