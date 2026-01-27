import os
import random
import argparse
from pathlib import Path

# 支持的图片扩展名（可按需扩展）
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.svg'}


def is_image_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in IMAGE_EXTENSIONS


def prune_images_in_directory(root_dir: str, keep_ratio: float = 0.1, dry_run: bool = True):
    root = Path(root_dir).resolve()
    if not root.is_dir():
        raise ValueError(f"输入路径不是有效目录: {root}")

    # 递归收集所有图片文件
    all_images = [f for f in root.rglob("*") if f.is_file() and is_image_file(f)]

    if not all_images:
        print("⚠️  没有找到任何支持的图片文件。")
        return

    total = len(all_images)
    keep_count = max(1, int(total * keep_ratio))  # 至少保留1张
    to_delete_count = total - keep_count

    print(f"📁 扫描目录: {root}")
    print(f"🖼️  共找到 {total} 张图片")
    print(f"🎯 将保留 {keep_count} 张（{keep_ratio:.1%}），删除 {to_delete_count} 张")

    if to_delete_count <= 0:
        print("✅ 无需删除（保留比例 ≥ 100% 或 图片太少）")
        return

    # 随机打乱并选择要保留的文件
    random.shuffle(all_images)
    keep_set = set(all_images[:keep_count])
    delete_list = [f for f in all_images if f not in keep_set]

    # 排序以便日志可读
    delete_list.sort()

    # 日志文件路径
    log_file = root / "deleted_images.log"

    if dry_run:
        print("\n🔍 [DRY RUN] 以下文件将被删除（实际未删除）:")
        with open(log_file, 'w', encoding='utf-8') as lf:
            lf.write(f"DRY RUN - 预计删除 {len(delete_list)} 张图片\n")
            for f in delete_list:
                rel_path = f.relative_to(root)
                print(f"  ❌ {rel_path}")
                lf.write(str(rel_path) + "\n")
        print(f"\n📝 删除清单已保存至: {log_file}")
        print("💡 使用 --no-dry-run 参数执行真实删除。")
    else:
        print("\n🗑️  正在删除文件...")
        deleted_count = 0
        with open(log_file, 'w', encoding='utf-8') as lf:
            lf.write(f"实际删除 {len(delete_list)} 张图片\n")
            for f in delete_list:
                try:
                    f.unlink()  # 删除文件
                    rel_path = f.relative_to(root)
                    print(f"  ✅ 已删除: {rel_path}")
                    lf.write(str(rel_path) + "\n")
                    deleted_count += 1
                except Exception as e:
                    print(f"  ❌ 删除失败: {f} - {e}")
                    lf.write(f"[FAILED] {f} - {e}\n")

        print(f"\n✅ 删除完成！共删除 {deleted_count} 张图片。")
        print(f"📄 删除日志已保存至: {log_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="随机删除指定目录下 90% 的图片（仅保留 10%）"
    )
    parser.add_argument(
        "-d", "--dir",
        required=True,
        help="要处理的根目录路径"
    )
    parser.add_argument(
        "-r", "--ratio",
        type=float,
        default=0.1,
        help="保留比例（0.0 ～ 1.0），默认 0.1（即保留10%）"
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="禁用预览模式，执行真实删除（默认为 dry-run）"
    )

    args = parser.parse_args()

    if not (0.0 < args.ratio <= 1.0):
        raise ValueError("保留比例必须在 (0, 1] 范围内")

    prune_images_in_directory(
        root_dir=args.dir,
        keep_ratio=args.ratio,
        dry_run=not args.no_dry_run
    )

    #python random_prune_images.py -d "H:\YOLO_Datasets\BrainTumor\own_data_A3" --no-dry-run