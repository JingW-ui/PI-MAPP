import os
import argparse

# 支持的常见图像格式（可按需扩展）
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}


def create_empty_txt_files(image_dir, label_dir):
    # 确保标签目录存在
    os.makedirs(label_dir, exist_ok=True)

    # 遍历图片目录
    for filename in os.listdir(image_dir):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in IMAGE_EXTENSIONS:
            continue  # 跳过非图像文件

        txt_path = os.path.join(label_dir, name + '.txt')

        # 只有当文件不存在时才创建（避免覆盖已有标签）
        if not os.path.exists(txt_path):
            with open(txt_path, 'w') as f:
                pass  # 创建空文件
            print(f"Created empty label: {txt_path}")
        else:
            print(f"Skipped (already exists): {txt_path}")

    print("✅ 所有对应空白 .txt 文件已生成完成！")


if __name__ == "__main__":
    image_dir = 'H:\YOLO_Datasets\BrainTumor\own_data_A3'
    label_dir = r'H:\YOLO_Datasets\BrainTumor\BrainTumorYolov8\train\labels'
    create_empty_txt_files(image_dir, label_dir)