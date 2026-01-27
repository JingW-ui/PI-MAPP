import os
import argparse

def is_file_empty(file_path):
    """判断文件是否为空（包括只含空白字符的情况）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return len(content) == 0
    except Exception as e:
        print(f"无法读取文件 {file_path}: {e}")
        return None  # 表示读取失败

def analyze_txt_files(directory):
    total_files = 0
    empty_files = 0
    non_empty_files = 0
    unreadable_files = 0

    if not os.path.isdir(directory):
        print(f"错误：'{directory}' 不是一个有效的目录。")
        return

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.txt'):
                total_files += 1
                full_path = os.path.join(root, file)
                is_empty = is_file_empty(full_path)
                if is_empty is True:
                    empty_files += 1
                    print(f"[空] {full_path}")
                elif is_empty is False:
                    non_empty_files += 1
                else:
                    unreadable_files += 1

    # 输出统计结果
    print("\n=== 统计结果 ===")
    print(f"总 .txt 文件数: {total_files}")
    print(f"内容为空的文件数: {empty_files}")
    print(f"内容非空的文件数: {non_empty_files}")
    if unreadable_files > 0:
        print(f"无法读取的文件数: {unreadable_files}")

def main():
    directory = r'H:\YOLO_Datasets\BrainTumor\BrainTumorYolov8_copy\valid\labels'

    analyze_txt_files(directory)

if __name__ == "__main__":
    main()