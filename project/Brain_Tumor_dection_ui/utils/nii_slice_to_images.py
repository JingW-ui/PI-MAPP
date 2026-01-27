import os
import random
import string
import time
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image


def generate_unique_suffix(length=8):
    """生成时间戳+随机字符串，用于唯一命名"""
    timestamp = str(int(time.time() * 1_000_000))  # 微秒级时间戳
    rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return f"{timestamp}_{rand_str}"


def normalize_to_uint8(data):
    """将任意数值范围的数组归一化到 0-255 并转为 uint8"""
    data = data.astype(np.float32)
    min_val = np.min(data)
    max_val = np.max(data)
    if max_val == min_val:
        normalized = np.zeros_like(data, dtype=np.uint8)
    else:
        normalized = ((data - min_val) / (max_val - min_val)) * 255
    return normalized.astype(np.uint8)


def slice_nii_and_save(nii_path: Path, output_dir: Path):
    """
    对单个 .nii.gz 文件进行切片并保存为图片
    """
    try:
        nii_img = nib.load(str(nii_path))
        data = nii_img.get_fdata()  # shape: (H, W, D) 或更高维
    except Exception as e:
        print(f"❌ 加载失败: {nii_path.name} - {e}")
        return 0

    if data.ndim < 3:
        print(f"⚠️  跳过 {nii_path.name}：维度小于3")
        return 0

    # 取前三个维度处理（忽略时间/通道等）
    if data.ndim > 3:
        # 尝试取第一个时间点或通道
        data = data[..., 0] if data.shape[-1] > 1 else np.squeeze(data)
        if data.ndim > 3:
            print(f"⚠️  {nii_path.name} 维度过高 ({data.ndim})，仅处理前3维")
            data = data[tuple(0 for _ in range(data.ndim - 3))]  # 取各额外维度的第0个

    if data.ndim != 3:
        print(f"⚠️  无法处理非3D数据: {nii_path.name} (shape={data.shape})")
        return 0

    axes = [0, 1, 2]
    selected_axes = random.sample(axes, 2)  # 随机选两个不同轴
    saved_count = 0

    for axis in selected_axes:
        depth = data.shape[axis]
        if depth <= 1:
            continue

        step = random.randint(2, 4)
        # 确保至少有一个切片（即使 depth 很小）
        indices = list(range(0, depth, step)) or [0]

        for idx in indices:
            if axis == 0:
                slice_2d = data[idx, :, :]
            elif axis == 1:
                slice_2d = data[:, idx, :]
            else:  # axis == 2
                slice_2d = data[:, :, idx]

            # 归一化并转为图像
            img_array = normalize_to_uint8(slice_2d)
            img = Image.fromarray(img_array)

            # 唯一文件名
            unique_part = generate_unique_suffix()
            out_name = f"{nii_path.stem}_axis{axis}_idx{idx}_{unique_part}.png"
            out_path = output_dir / out_name

            # 防冲突（极小概率）
            counter = 0
            while out_path.exists():
                out_name = f"{nii_path.stem}_axis{axis}_idx{idx}_{unique_part}_{counter}.png"
                out_path = output_dir / out_name
                counter += 1

            try:
                img.save(out_path)
                saved_count += 1
            except Exception as e:
                print(f"❌ 保存失败: {out_path.name} - {e}")

    return saved_count


def process_nii_directory(input_dir: str, output_dir: str):
    input_path = Path(input_dir).resolve()
    output_path = Path(output_dir).resolve()

    if not input_path.is_dir():
        raise ValueError(f"输入路径不是有效目录: {input_path}")

    output_path.mkdir(parents=True, exist_ok=True)

    nii_files = list(input_path.rglob("*.nii.gz"))
    if not nii_files:
        print("⚠️  指定目录及其子目录中没有找到 .nii.gz 文件")
        return

    total_saved = 0
    for nii_file in nii_files:
        print(f"📦 处理: {nii_file.name}")
        count = slice_nii_and_save(nii_file, output_path)
        total_saved += count

    print(f"\n✅ 完成！共处理 {len(nii_files)} 个文件，生成 {total_saved} 张图片。")


if __name__ == "__main__":
    input_dir = r"H:/data/QSM/SCA3_Data_raw/anat_niigz/"
    output_dir = r"H:\YOLO_Datasets\BrainTumor\own_data_A3"
    process_nii_directory(input_dir, output_dir)