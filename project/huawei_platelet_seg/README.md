# 血小板检测与分割项目

## 项目概述

本项目是一个基于YOLO模型的血小板检测与分割系统，使用华为云平台进行模型训练和推理。项目利用深度学习技术对显微镜下的血小板图像进行精确识别、定位和分割。

## 功能特性

- **目标检测**: 使用YOLO模型检测显微镜图像中的血小板
- **实例分割**: 对检测到的血小板进行像素级分割
- **结果可视化**: 叠加掩码到原始图像以可视化分割结果
- **模型验证**: 提供模型性能评估功能
- **模型训练**: 支持使用自定义数据集训练模型

## 项目结构

```
project/
└── huawei_platelet_seg/
    ├── cfg.yaml              # 数据集配置文件
    ├── dataset_demo/         # 示例数据集
    │   ├── images/
    │   └── labels/
    ├── pt/                   # 预训练模型权重
    │   └── best.pt
    ├── runs/                 # 训练和推理结果
    │   ├── masks/
    │   ├── masks_my/
    │   ├── results/
    │   └── segment/
    ├── main.py               # 主推理脚本
    ├── train.py              # 模型训练脚本
    ├── val.py                # 模型验证脚本
    ├── mask_overlay.py       # 掩码叠加可视化脚本
    └── upload_from_book.py   # 华为云上传脚本
```

## 环境配置

### 依赖安装

```bash
pip install ultralytics
pip install pillow
pip install numpy
```

## 使用方法

### 1. 模型训练

使用[train.py](file:///H:/pycharm_project/PI-MAPP/project/huawei_platelet_seg/train.py)脚本训练模型：

```bash
python train.py
```

该脚本将使用[cfg.yaml](file:///H:/pycharm_project/PI-MAPP/project/huawei_platelet_seg/cfg.yaml)中定义的数据集配置进行训练，训练100个epoch，图像尺寸设置为512x512。

### 2. 模型推理

使用[main.py](file:///H:/pycharm_project/PI-MAPP/project/huawei_platelet_seg/main.py)脚本进行推理：

```bash
python main.py
```

此脚本将加载预训练模型并对指定目录中的图像进行预测，同时保存分割结果和文本标签。

### 3. 模型验证

使用[val.py](file:///H:/pycharm_project/PI-MAPP/project/huawei_platelet_seg/val.py)脚本验证模型性能：

```bash
python val.py
```

此脚本将计算模型在验证集上的mAP50-95指标。

### 4. 结果可视化

使用[mask_overlay.py](file:///H:/pycharm_project/PI-MAPP/project/huawei_platelet_seg/mask_overlay.py)脚本将分割掩码叠加到原始图像上：

```bash
python mask_overlay.py
```

此脚本将从训练和验证集的标签中读取分割信息，并将其可视化地叠加到原始图像上，便于直观评估模型性能。

## 配置文件说明

[cfg.yaml](file:///H:/pycharm_project/PI-MAPP/project/huawei_platelet_seg/cfg.yaml)包含以下配置：
- `path`: 数据集根目录路径
- `train`: 训练集图像路径
- `val`: 验证集图像路径
- `names`: 类别名称列表（本项目只有一种类别：platelet）

## 数据集要求

数据集应按照以下结构组织：

```
dataset_demo/
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
```

标签文件采用YOLO格式，每行包含：类别ID + 归一化的多边形坐标。

## 输出结果

- 分割结果保存在[runs/segment/](file:///H:/pycharm_project/PI-MAPP/project/huawei_platelet_seg/runs/segment/)目录
- 掩码可视化结果保存在[runs/masks_my/](file:///H:/pycharm_project/PI-MAPP/project/huawei_platelet_seg/runs/masks_my/)目录
- 训练结果保存在[runs/results/](file:///H:/pycharm_project/PI-MAPP/project/huawei_platelet_seg/runs/results/)目录

## 注意事项

- 请确保有足够的GPU内存来训练模型
- 训练时间会根据数据集大小和硬件配置而变化
- 模型权重文件可能很大，请确保有足够存储空间
- 使用[mask_overlay.py](file:///H:/pycharm_project/PI-MAPP/project/huawei_platelet_seg/mask_overlay.py)时，确保标签文件和图像文件名匹配

## 华为云集成

[upload_from_book.py](file:///H:/pycharm_project/PI-MAPP/project/huawei_platelet_seg/upload_from_book.py)脚本展示了如何使用华为云对象存储服务上传模型或数据（需适当配置）。