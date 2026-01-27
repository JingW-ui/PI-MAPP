import cv2
import nibabel as nib
import numpy as np
from ultralytics import YOLO
import os

# ----------------------------
# 配置
# ----------------------------
model_path = r'H:\pycharm_project\PI-MAPP\project\detection_train\tumor\runs\detect\train_yolo12_try_owndata2\weights\best.pt'
nii_path = 'data_test/MRBrainTumor2.nii.gz'
output_project = 'best_slices_results'
os.makedirs(output_project, exist_ok=True)
conf = 0.65

model = YOLO(model_path)
img = nib.load(nii_path)
data = img.get_fdata()

# 获取体素间距 (spacing in mm) —— 顺序与 data.shape 一致: (axis0, axis1, axis2)
spacing = img.header.get_zooms()  # e.g., (0.9375, 0.9375, 1.2)
print(f"📏 Voxel spacing (mm): {spacing}")

# 归一化到 uint8
if data.dtype != np.uint8:
    data = np.clip(data, 0, np.percentile(data, 99))
    data = ((data - data.min()) / (data.max() - data.min()) * 255).astype(np.uint8)

I, J, K = data.shape  # axis0, axis1, axis2

# ==========================================
# Step 1: 沿 axis=2（axial）找最大目标切片
# ==========================================
print("🔍 Step 1: Searching along axis=2 (axial slices)...")
max_area_k = -1
best_k = -1
best_box_in_k = None

for k in range(K):
    slice_2d = data[:, :, k]
    slice_rgb = np.stack([slice_2d] * 3, axis=-1)
    results = model.predict(source=slice_rgb, conf=conf, verbose=False, device=None, save=False)

    current_max_area = 0
    best_box = None
    for result in results:
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes.xywh.cpu().numpy()
            areas = boxes[:, 2] * boxes[:, 3]
            max_idx = areas.argmax()
            if areas[max_idx] > current_max_area:
                current_max_area = areas[max_idx]
                best_box = boxes[max_idx]

    if current_max_area > max_area_k:
        max_area_k = current_max_area
        best_k = k
        best_box_in_k = best_box

print(f"✅ Best axial slice (k={best_k}), max area: {max_area_k:.2f}")
if best_box_in_k is None:
    raise RuntimeError("No tumor detected in any axial slice!")

cx, cy, w, h = best_box_in_k

# Map to volume indices
i_center = int(round(cy))  # axis=0
j_center = int(round(cx))  # axis=1
k_center = best_k          # axis=2

print(f"🎯 Tumor center at volume index: (i={i_center}, j={j_center}, k={k_center})")

# ==============================
# 🔬 使用空间分辨率计算物理尺寸，并转换为各轴的搜索半径（voxel）
# ==============================

# Bounding box physical size (in mm)
physical_width_mm = w * spacing[1]   # w is along axis=1 (J)
physical_height_mm = h * spacing[0]  # h is along axis=0 (I)

# Define search radius in physical space (e.g., use full extent or fraction)
# Here we use the same physical extent as the bbox, but you could also use a fixed value like 15.0 mm
search_radius_mm_i = physical_height_mm / 3.0  # vertical direction
search_radius_mm_j = physical_width_mm / 3.0   # horizontal direction

# Convert physical radius back to voxel counts for each axis
search_radius_i_vox = int(np.ceil(search_radius_mm_i / spacing[0]))  # for axis=0
search_radius_j_vox = int(np.ceil(search_radius_mm_j / spacing[1]))  # for axis=1

# Ensure at least 1 voxel radius
search_radius_i_vox = max(1, search_radius_i_vox)
search_radius_j_vox = max(1, search_radius_j_vox)

# Bounds for local search
i_start = max(0, i_center - search_radius_i_vox)
i_end = min(I, i_center + search_radius_i_vox + 1)
j_start = max(0, j_center - search_radius_j_vox)
j_end = min(J, j_center + search_radius_j_vox + 1)

print(f"📏 Using spacing {spacing} → search radii: "
      f"axis0={search_radius_i_vox} vox, axis1={search_radius_j_vox} vox")
print(f"🔍 Search sagittal (i) in [{i_start}, {i_end})")
print(f"🔍 Search coronal  (j) in [{j_start}, {j_end})")

# ==========================================
# Step 2: 在 axis=0（sagittal）局部搜索
# ==========================================
print("🔍 Step 2: Searching sagittal slices (fixing i)...")
max_area_i = -1
best_i = -1
for i in range(i_start, i_end):
    slice_2d = data[i, :, :]
    slice_rgb = np.stack([slice_2d] * 3, axis=-1)
    results = model.predict(source=slice_rgb, conf=0.92, verbose=False, device=None, save=False)

    current_max_area = 0
    for result in results:
        if result.boxes is not None and len(result.boxes) > 0:
            areas = result.boxes.xywh[:, 2] * result.boxes.xywh[:, 3]
            current_max_area = max(current_max_area, areas.max().item())

    if current_max_area > max_area_i:
        max_area_i = current_max_area
        best_i = i

print(f"✅ Best sagittal slice (i={best_i}), max area: {max_area_i:.2f}")

# ==========================================
# Step 3: 在 axis=1（coronal）局部搜索
# ==========================================
print("🔍 Step 3: Searching coronal slices (fixing j)...")
max_area_j = -1
best_j = -1
for j in range(j_start, j_end):
    slice_2d = data[:, j, :]
    slice_rgb = np.stack([slice_2d] * 3, axis=-1)
    results = model.predict(source=slice_rgb, conf=0.92, verbose=False, device=None, save=False)

    current_max_area = 0
    for result in results:
        if result.boxes is not None and len(result.boxes) > 0:
            areas = result.boxes.xywh[:, 2] * result.boxes.xywh[:, 3]
            current_max_area = max(current_max_area, areas.max().item())

    if current_max_area > max_area_j:
        max_area_j = current_max_area
        best_j = j

print(f"✅ Best coronal slice (j={best_j}), max area: {max_area_j:.2f}")

# ==========================================
# Step 4: 保存结果
# ==========================================
best_indices = {0: best_i, 1: best_j, 2: best_k}
plane_names = ['sagittal', 'coronal', 'axial']

for axis, idx in best_indices.items():
    if axis == 0:
        slice_2d = data[idx, :, :]
    elif axis == 1:
        slice_2d = data[:, idx, :]
    else:
        slice_2d = data[:, :, idx]

    slice_rgb = np.stack([slice_2d] * 3, axis=-1)
    slice_rgb = np.ascontiguousarray(slice_rgb)

    results = model.predict(
        source=slice_rgb,
        conf=conf,
        save=False,
        verbose=False,
        device=None
    )

    plotted_img = results[0].plot()
    output_dir = os.path.join(output_project, f"best_{plane_names[axis]}_slice_{idx:04d}")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "image.jpg")
    cv2.imwrite(output_path, plotted_img)

print("\n✅ All best slices saved with spacing-aware search.")
print(f"Results are in: {os.path.abspath(output_project)}")