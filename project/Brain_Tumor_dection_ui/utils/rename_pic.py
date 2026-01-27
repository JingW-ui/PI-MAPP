import os
import time
import random
import string
from pathlib import Path


def generate_random_suffix(length=8):
    """生成指定长度的随机字母数字字符串"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def rename_images_in_directory(directory, image_extensions=None):
    """
    对指定目录下的图片文件进行批量重命名。

    :param directory: 要处理的目录路径（字符串或Path对象）
    :param image_extensions: 图片文件扩展名列表，默认包括常见格式
    """
    if image_extensions is None:
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    directory = Path(directory)
    if not directory.is_dir():
        print(f"错误：'{directory}' 不是一个有效目录。")
        return

    # 获取所有匹配的图片文件
    image_files = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    if not image_files:
        print("目录中没有找到支持的图片文件。")
        return

    renamed_count = 0
    for file_path in image_files:
        # 获取当前时间戳（微秒级）
        timestamp = int(time.time() * 1_000_000)  # 微秒时间戳
        random_part = generate_random_suffix()
        new_name = f"{timestamp}_{random_part}{file_path.suffix}"
        new_path = file_path.parent / new_name

        # 防止极小概率的重名冲突（虽然几乎不可能）
        while new_path.exists():
            random_part = generate_random_suffix()
            new_name = f"{timestamp}_{random_part}{file_path.suffix}"
            new_path = file_path.parent / new_name

        try:
            file_path.rename(new_path)
            print(f"重命名: {file_path.name} -> {new_name}")
            renamed_count += 1
        except Exception as e:
            print(f"重命名失败: {file_path.name} - 错误: {e}")

    print(f"\n完成！共重命名 {renamed_count} 个文件。")


if __name__ == "__main__":
    # 设置要处理的目录路径（可修改为你的目标路径）
    target_directory = input("请输入要处理的图片目录路径: ").strip().strip('"')
    rename_images_in_directory(target_directory)