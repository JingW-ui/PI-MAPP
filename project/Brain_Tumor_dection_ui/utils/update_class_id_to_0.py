import os
import argparse


def update_txt_labels(directory):
    # 遍历目录下所有 .txt 文件
    for filename in os.listdir(directory):
        if not filename.endswith('.txt'):
            continue

        filepath = os.path.join(directory, filename)

        with open(filepath, 'r') as f:
            lines = f.readlines()

        updated_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                updated_lines.append(line)  # 保留空行
                continue

            parts = line.split()
            if len(parts) < 1:
                updated_lines.append(line)
                continue

            # 将第一个字段（class_id）改为 '1'
            parts[0] = '0'
            updated_line = ' '.join(parts)
            updated_lines.append(updated_line)

        # 写回文件（覆盖原文件）
        with open(filepath, 'w') as f:
            f.write('\n'.join(updated_lines) + ('\n' if updated_lines else ''))

        print(f"Updated: {filepath}")


if __name__ == "__main__":
    path = r'H:\YOLO_Datasets\BrainTumor\BrainTumorYolov8\valid\labels'
    update_txt_labels(path)