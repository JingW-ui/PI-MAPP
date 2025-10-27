以下是根据您提供的代码完善的 README.md 文件：

🧠 基于 YOLO 的脑部肿瘤智能检测系统（UI 版）

<div align="center">

https://img.shields.io/badge/Python-3.8%2B-blue](https://www.python.org/)
https://img.shields.io/badge/PySide6-1.0%2B-blue](https://doc.qt.io/qtforpython/)
https://img.shields.io/badge/YOLO-检测引擎-green](https://github.com/ultralytics/ultralytics)
https://img.shields.io/badge/License-MIT-blue](LICENSE)

</div>

🎯 项目简介

本项目面向医疗影像辅助诊断场景，构建了基于 YOLO（You Only Look Once） 的 脑部肿瘤智能检测平台，旨在提升 胶质瘤（glioma）、脑膜瘤（meningioma）、垂体瘤（pituitary） 等常见脑部肿瘤的检出率与工作效率，有效缓解基层与专科医师的阅片压力，降低漏诊与误诊风险。

系统提供可视化检测结果、批量处理、历史追溯与报告生成等功能，服务于临床决策支持与医学科研分析。

🏥 项目定位与适用场景

维度 说明

🎯 核心目标 提升脑部肿瘤（胶质瘤、脑膜瘤、垂体瘤）的智能识别与辅助诊断能力

🏥 适用领域 医疗健康 / 医学影像

👥 适用对象 神经外科医生、放射科医师、科研人员、基层医疗单位

📍 应用场景 门诊初筛、术中辅助诊断、回顾性病例研究、数据集标注与质控等

✨ 主要功能特性

🔍 多源输入检测支持

• 单张图片：支持常见医学/日常图像格式（.jpg, .png, .bmp, .tiff, .webp 等）

• 视频文件：支持 .mp4, .avi, .mov, .mkv 等主流视频格式的逐帧检测

• 摄像头实时：支持本地摄像头接入，实现实时检测与监控

• 批量文件夹：支持一次性导入整个文件夹的图像进行批量分析与结果导出

🧠 模型与参数管理

• 本地模型加载：支持加载自定义训练的 YOLO 模型（如 .pt 格式），默认检测类别为：

  • 0: glioma（胶质瘤）

  • 1: meningioma（脑膜瘤）

  • 2: pituitary（垂体瘤）

• 灵活参数调节：支持实时调整置信度阈值（0.01 ~ 1.0），以平衡检测灵敏度与误报率

🖼️ 检测结果可视化

• 原图 vs 检测结果对比展示

• 目标类别与置信度标注

• 实时统计信息与推理耗时展示

• 支持检测快照与录像（摄像头模式下）

📊 批量处理与报告

• 批量图片检测：一键导入文件夹，自动批量处理所有图像

• 结果导出：支持将检测结果（含标注图）批量保存至指定目录

• 智能报告生成：自动生成包含文件名、检测目标数、推理时间、类别分布、置信度统计等信息的 TXT 格式检测报告

• 历史追溯：支持结果查看与导航（上一张/下一张）

🛠 系统工具与扩展

• NIfTI 格式转换：支持医学影像 NIfTI 文件（.nii/.nii.gz）按指定方向（矢状位/冠状位/水平位）切片并转换为 PNG 序列，便于后续分析

• 多摄像头管理：支持多摄像头同时接入与切换（高级功能）

• 日志监控：实时记录系统运行状态、检测结果与异常信息

• 快照与录制：摄像头模式下支持手动快照或自动录制检测过程

🛠 技术架构

组件 技术方案

🖥️ 开发框架 Python + PySide6（跨平台桌面 GUI 应用）

🧠 检测引擎 YOLO 目标检测模型 + OpenCV 图像处理

🧩 多线程 检测任务与 UI 解耦，保障界面流畅响应

🎛️ 交互设计 标签页分组、直观控件布局，操作简洁易上手

📁 模块化 功能分层清晰（模型管理、摄像头管理、日志、检测线程等）

📂 项目结构概览


Brain_Tumor_dection_ui/
├── Brain_Tumor_detection_ui.py      # 主程序入口
├── README.md                        # 项目说明文档（本文件）
├── img/                             # 示例截图与界面展示
│   ├── ScreenShot_2025-10-27_094533_666.png     # 界面预览图
│   ├── ScreenShot_2025-10-27_094608_900.png     # 批量保存效果图
│   └── ScreenShot_2025-10-27_094629_087.png     # 检测报告内容示例
├── models/                          # （建议）存放 YOLO 模型文件，如 *.pt
├── utils/                           # （可选）工具函数/模块
├── requirements.txt                 # （建议）Python 依赖包列表
└── ...                              # 其他资源/工具（如爬虫、检测工具等）


📌 注意：

- 您需要自行下载并放置 YOLO 模型文件（如 .pt 文件） 到项目目录（如 models/），或确保模型能被正确扫描与加载。

- 建议通过 requirements.txt 或直接在代码中安装所需依赖（如 PySide6, ultralytics, opencv-python, nibabel, Pillow, numpy, matplotlib 等）。

🚀 快速开始

1. 克隆项目

git clone [项目地址]
cd Brain_Tumor_dection_ui


🔗 https://github.com/junior6666/PI-MAPP/tree/main/project/Brain_Tumor_dection_ui  

（点击上方链接查看源码、提交反馈或参与协作）

2. 安装依赖

请根据实际使用的依赖库安装，例如可通过 requirements.txt 安装（如存在）：

pip install -r requirements.txt


若无 requirements.txt，请手动安装常用依赖，例如：

```bash

pip install PySide6 ultralytics opencv-python numpy pillow matplotlib nibabel

```

3. 运行主程序

python Brain_Tumor_detection_ui.py


⚠️ 注意：

- 请确保已正确配置并放置 YOLO 模型文件（如 .pt 文件）于项目目录中，或模型路径能被程序正确识别。

- 首次运行会尝试自动加载默认模型（如有）。

📖 使用指南

界面概览

系统采用多标签页 + 左右分栏布局，主要包括：

• 左侧控制面板：模型配置、检测源选择、参数调节、检测控制、日志监控

• 右侧显示区域：实时检测视图、批量结果浏览、NIfTI转换工具、监控模块等

主要功能入口

标签页 功能说明

🎯 实时检测 支持单张图片、视频、摄像头实时检测，原图与检测结果对比展示

📊 批量结果 批量图片检测结果浏览、导航、保存与报告生成

NIfTI 转换 医学 NIfTI 文件按切片方向导出为 PNG 序列

🖥️ 实时监控 （高级）多摄像头接入与监控模式

🎬 监控快照 （高级）摄像头快照管理

操作流程举例

• 单张/视频/摄像头检测：

  1. 选择对应检测模式（如“📷 单张图片”）
  2. 点击“📁 选择文件/文件夹”选择待检测内容
  3. 调节置信度阈值（如需要）
  4. 点击“▶️ 开始检测”查看实时结果

• 批量检测：

  1. 选择“📂 文件夹批量”
  2. 选择包含多张图片的文件夹
  3. 点击“▶️ 开始检测”，系统将自动批量处理
  4. 查看结果并可导出所有检测图片与生成报告

• NIfTI 转换：

  1. 切换到“NIfTI 转换”标签页
  2. 浏览并选择 NIfTI 文件（.nii 或 .nii.gz）
  3. 设置输出目录与切片参数
  4. 点击“🔄 转换”生成 PNG 切片序列

⚠️ 免责声明

⚠️ 重要提醒：

本项目仅供学习、科研与技术交流使用，不可直接用于临床诊断或医疗决策。  

检测结果仅供参考，实际诊断请以专业医师判断为准。  

开发者不对因使用本项目导致的任何直接或间接后果承担责任。

📎 项目资源

• 🔗 源码地址（GitHub）：  

  https://github.com/junior6666/PI-MAPP/tree/main/project/Brain_Tumor_dection_ui  
  （欢迎 Star ⭐ & Fork 🍴，提交 Issue 或 Pull Request！）

• 📷 界面与功能截图：

  • !img/ScreenShot_2025-10-27_094533_666.png

  • !img/ScreenShot_2025-10-27_094608_900.png

  • !img/ScreenShot_2025-10-27_094629_087.png

🤝 持续更新与协作

• 本项目持续更新中，欢迎广大开发者、医疗AI研究者、使用者 Star ⭐、Fork 🍴、提交反馈或贡献代码！

• 如有问题、建议或合作意向，欢迎通过 GitHub Issues 或 Pull Requests 与我们联系！

📌 补充说明

1. 模型文件请自行下载，并放在项目根目录（或 models/ 子目录）下。
2. 支持批量检测结果保存与可视化报告生成，详见“📊 批量结果”标签页。
3. NIfTI 转换功能适用于医学影像数据预处理与科研分析。

祝您使用愉快，助力医疗 AI 发展！ 🌟

--- 

✅ 推荐操作：
• 配置好您的 YOLO 模型文件（如 .pt 格式），确保模型类别与代码中一致（0: glioma, 1: meningioma, 2: pituitary）。

• 根据需要修改 requirements.txt 或直接在代码中安装依赖。

• 如需扩展功能（如 DICOM 支持、更多医学图像格式、云端模型部署等），欢迎贡献代码或提出 Issue！

--- 

最后更新于 2025 年 10 月 27 日