import os
import cv2
import torch
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from tqdm import tqdm

# ================== 配置区 ==================
WEIGHTS_PATH = r"H:\pycharm_project\PI-MAPP\project\detection_train\tumor\runs\detect\train_yolo12_try_owndata2\weights\best.pt"
VALID_IMAGES_DIR = r"H:\YOLO_Datasets\BrainTumor\BrainTumorYolov8_copy\valid\images"
VALID_LABELS_DIR = r"H:\YOLO_Datasets\BrainTumor\BrainTumorYolov8_copy\valid\labels"

OUTPUT_DIR = r"H:\YOLO_Datasets\BrainTumor\BrainTumorYolov8_copy/output_1_0.75"  # 输出目录（可改）
CONF_THRES = 0.75         # 置信度阈值（建议与 val 一致）
IOU_THRES = 0.5           # IoU 匹配阈值（mAP50 标准）
IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp'}

# ============================================

def read_yolo_segment_label(label_path, img_w, img_h):
    """
    读取 YOLO segmentation 标签（多边形格式），返回最小外接矩形 [x1, y1, x2, y2]
    格式: class x1 y1 x2 y2 ... xn yn （归一化坐标）
    """
    boxes = []
    if not label_path.exists():
        return boxes

    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 7:  # 至少 1 class + 3 points (6 coords)
                continue
            try:
                cls = int(parts[0])
                coords = list(map(float, parts[1:]))
                if len(coords) % 2 != 0:
                    continue  # 坐标必须成对
                xs = [x * img_w for x in coords[0::2]]
                ys = [y * img_h for y in coords[1::2]]
                if xs and ys:
                    x1, y1 = max(0, int(min(xs))), max(0, int(min(ys)))
                    x2, y2 = min(img_w, int(max(xs))), min(img_h, int(max(ys)))
                    if x2 > x1 and y2 > y1:
                        boxes.append([x1, y1, x2, y2])
            except Exception as e:
                print(f"警告：解析标签出错 {label_path} - {e}")
                continue
    return boxes

def bbox_iou(box1, box2):
    """计算两个框的 IoU"""
    x1, y1, x2, y2 = box1
    x1_p, y1_p, x2_p, y2_p = box2

    inter_x1 = max(x1, x1_p)
    inter_y1 = max(y1, y1_p)
    inter_x2 = min(x2, x2_p)
    inter_y2 = min(y2, y2_p)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area1 = (x2 - x1) * (y2 - y1)
    area2 = (x2_p - x1_p) * (y2_p - y1_p)
    union_area = area1 + area2 - inter_area

    return inter_area / union_area if union_area > 0 else 0

def draw_boxes(image, boxes, color, label_prefix=""):
    """在图像上绘制边界框"""
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        if label_prefix:
            cv2.putText(image, f"{label_prefix}{i}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return image

def main():
    # 创建输出目录
    output_dir = Path(OUTPUT_DIR)
    fn_dir = output_dir / "fn"
    fp_dir = output_dir / "fp"
    fn_dir.mkdir(parents=True, exist_ok=True)
    fp_dir.mkdir(parents=True, exist_ok=True)

    # 加载模型
    print("Loading model...")
    model = YOLO(WEIGHTS_PATH)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)

    # 获取所有图像
    image_paths = [p for p in Path(VALID_IMAGES_DIR).iterdir() if p.suffix.lower() in IMG_EXTENSIONS]
    print(f"Found {len(image_paths)} images in validation set.")

    fn_count = 0
    fp_count = 0

    for img_path in tqdm(image_paths, desc="Processing"):
        # 读取图像
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        h, w = img.shape[:2]

        # 读取真实标签（支持 segmentation 格式）
        label_path = Path(VALID_LABELS_DIR) / f"{img_path.stem}.txt"
        true_boxes = read_yolo_segment_label(label_path, w, h)

        # 模型推理（目标检测）
        results = model.predict(
            source=img,
            conf=CONF_THRES,
            iou=0.45,
            verbose=False,
            device=device
        )
        pred_boxes = []
        if results[0].boxes is not None:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                pred_boxes.append([x1, y1, x2, y2])

        # 初始化匹配标记
        matched_true = [False] * len(true_boxes)
        matched_pred = [False] * len(pred_boxes)

        # 匹配预测框和真实框（IoU >= IOU_THRES）
        for i, tb in enumerate(true_boxes):
            for j, pb in enumerate(pred_boxes):
                if not matched_pred[j] and bbox_iou(tb, pb) >= IOU_THRES:
                    matched_true[i] = True
                    matched_pred[j] = True
                    break

        # 判断是否包含 FN 或 FP
        has_fn = any(not m for m in matched_true)
        has_fp = any(not m for m in matched_pred)

        if has_fn:
            fn_count += 1
            vis_img = img.copy()
            vis_img = draw_boxes(vis_img, true_boxes, (0, 255, 0), "GT")
            vis_img = draw_boxes(vis_img, pred_boxes, (255, 0, 0), "Pred")
            cv2.imwrite(str(fn_dir / f"{img_path.name}"), vis_img)

        if has_fp:
            fp_count += 1
            vis_img = img.copy()
            vis_img = draw_boxes(vis_img, true_boxes, (0, 255, 0), "GT")
            vis_img = draw_boxes(vis_img, pred_boxes, (255, 0, 0), "Pred")
            cv2.imwrite(str(fp_dir / f"{img_path.name}"), vis_img)

    print(f"\n✅ 分析完成！")
    print(f"   FN 样本数（漏检）: {fn_count}")
    print(f"   FP 样本数（误检）: {fp_count}")
    print(f"   可视化结果已保存至: {output_dir.absolute()}")

if __name__ == "__main__":
    main()