import os
from pathlib import Path

# 配置路径
VALID_DIR = r"H:\YOLO_Datasets\BrainTumor\BrainTumorYolov8_copy\valid"

# 支持的图像扩展名（YOLO 常用）
IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}

def main():
    valid_path = Path(VALID_DIR)
    images_dir = valid_path / "images"
    labels_dir = valid_path / "labels"

    if not images_dir.exists():
        print(f"错误：images 目录不存在 → {images_dir}")
        return
    if not labels_dir.exists():
        print(f"警告：labels 目录不存在 → {labels_dir}（所有图像将被视为负样本）")
        labels_dir = None

    # 获取所有图像文件（不含扩展名的 stem）
    image_files = {}
    for img in images_dir.iterdir():
        if img.suffix.lower() in IMG_EXTENSIONS:
            image_files[img.stem] = img

    # 获取所有标签文件
    label_files = {}
    label_empty_count = 0
    if labels_dir:
        for lbl in labels_dir.iterdir():
            if lbl.suffix.lower() == '.txt':
                label_files[lbl.stem] = lbl
                # 检查是否为空（负样本）
                if lbl.stat().st_size == 0:
                    label_empty_count += 1

    total_images = len(image_files)
    total_labels = len(label_files)

    # 找出匹配、缺失、多余的情况
    matched = set(image_files.keys()) & set(label_files.keys())
    images_no_label = set(image_files.keys()) - set(label_files.keys())
    labels_no_image = set(label_files.keys()) - set(image_files.keys())

    # 负样本 = 有图像 + 有标签文件 + 标签为空
    negative_samples = []
    if labels_dir:
        for stem in matched:
            lbl_path = labels_dir / f"{stem}.txt"
            if lbl_path.stat().st_size == 0:
                negative_samples.append(stem)

    # 输出结果
    print("=" * 60)
    print("🔍 YOLO 验证集分析报告")
    print("=" * 60)
    print(f"图像目录: {images_dir}")
    print(f"标签目录: {labels_dir}")
    print()
    print(f"✅ 总图像数: {total_images}")
    print(f"✅ 总标签文件数: {total_labels}")
    print(f"✅ 匹配的样本数（图像+标签）: {len(matched)}")
    print(f"⚠️ 负样本数（标签为空）: {len(negative_samples)}")
    print()
    print(f"❌ 有图像但无标签: {len(images_no_label)} 个")
    if images_no_label:
        print("   示例:", sorted(list(images_no_label))[:5])
    print()
    print(f"❌ 有标签但无图像: {len(labels_no_image)} 个")
    if labels_no_image:
        print("   示例:", sorted(list(labels_no_image))[:5])
    print()
    print("=" * 60)

    # 可选：保存负样本列表到文件
    if negative_samples:
        output_file = valid_path / "negative_samples.txt"
        with open(output_file, 'w') as f:
            for name in sorted(negative_samples):
                f.write(name + '\n')
        print(f"📝 负样本列表已保存至: {output_file}")

if __name__ == "__main__":
    main()