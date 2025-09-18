import os
import sys
import math
import csv
import shutil
from datetime import datetime
from glob import glob

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QGroupBox, QPushButton, QLabel, QTextEdit, QProgressBar,
                               QSpinBox, QFileDialog, QMessageBox, QTabWidget, QComboBox,
                               QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QFont, QTextCursor, QIcon


class StyleManager:
    """样式管理器 - 提供渐变和现代化UI样式"""

    @staticmethod
    def get_main_stylesheet():
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }

            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid rgba(52, 152, 219, 0.7);
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.9), stop:1 rgba(245, 245, 245, 0.9));
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #2c3e50;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton {
                padding: 2px 8px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                color: white;
                min-width: 65px;
                min-height: 25px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
                transform: translateY(-1px);
            }

            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f618d);
            }

            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #bdc3c7, stop:1 #95a5a6);
                color: #7f8c8d;
            }

            QComboBox {
                padding: 2px 8px;
                border: 2px solid rgba(189, 195, 199, 0.5);
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 white, stop:1 #f8f9fa);
                font-size: 12px;
                min-width: 150px;
                min-height: 25px;
            }

            QComboBox:focus {
                border-color: #3498db;
                background: white;
            }

            QProgressBar {
                border: 2px solid rgba(189, 195, 199, 0.5);
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 11px;
                max-height: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #d5dbdb);
            }

            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #27ae60);
                border-radius: 6px;
                margin: 1px;
            }

            QTextEdit {
                border: 2px solid rgba(189, 195, 199, 0.5);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.95);
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 8px;
                selection-background-color: #3498db;
            }

            QSlider::groove:horizontal {
                border: 1px solid rgba(189, 195, 199, 0.5);
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: 2px solid #2980b9;
                width: 20px;
                height: 20px;
                margin: -8px 0;
                border-radius: 12px;
            }

            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }

            QSpinBox, QDoubleSpinBox {
                padding: 6px 10px;
                border: 2px solid rgba(189, 195, 199, 0.5);
                border-radius: 6px;
                background: white;
                min-width: 80px;
                font-size: 12px;
            }

            QTabWidget::pane {
                border: 2px solid rgba(189, 195, 199, 0.5);
                border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95), stop:1 rgba(245, 245, 245, 0.95));
                margin-top: 5px;
            }

            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                border: 2px solid rgba(189, 195, 199, 0.5);
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 12px 25px;
                margin-right: 3px;
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
            }

            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border-color: rgba(52, 152, 219, 0.7);
            }

            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d5dbdb, stop:1 #bdc3c7);
            }

            QTableWidget {
                border: 2px solid rgba(189, 195, 199, 0.5);
                border-radius: 8px;
                background: white;
                gridline-color: rgba(189, 195, 199, 0.3);
                selection-background-color: rgba(52, 152, 219, 0.2);
                alternate-background-color: rgba(248, 249, 250, 0.5);
            }

            QTableWidget::item {
                padding: 8px;
                border: none;
            }

            QTableWidget::item:selected {
                background: rgba(52, 152, 219, 0.3);
                color: #2c3e50;
            }

            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34495e, stop:1 #2c3e50);
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }

            QListWidget {
                border: 2px solid rgba(189, 195, 199, 0.5);
                border-radius: 8px;
                background: white;
                selection-background-color: rgba(52, 152, 219, 0.2);
            }

            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(189, 195, 199, 0.2);
            }

            QListWidget::item:selected {
                background: rgba(52, 152, 219, 0.3);
                color: #2c3e50;
            }

            QScrollBar:vertical {
                background: rgba(236, 240, 241, 0.5);
                width: 12px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #bdc3c7, stop:1 #95a5a6);
                border-radius: 6px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #95a5a6, stop:1 #7f8c8d);
            }
        """

    @staticmethod
    def get_image_label_style():
        return """
            border: 3px solid rgba(52, 152, 219, 0.3);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(248, 249, 250, 0.9), stop:1 rgba(233, 236, 239, 0.9));
            color: #7f8c8d;
            font-weight: bold;
            font-size: 9px;
            border-radius: 10px;
            padding: 2px;
        """


class ImageProcessingThread(QThread):
    """图像处理线程基类"""
    progress = Signal(int)
    log_message = Signal(str)
    finished = Signal(bool, str)

    def __init__(self):
        super().__init__()
        self.is_running = True

    def stop(self):
        self.is_running = False


class SplitImagesThread(ImageProcessingThread):
    """分块处理线程"""

    def __init__(self, input_dir, output_dir, block_width, block_height):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.block_width = block_width
        self.block_height = block_height

    def run(self):
        try:
            # 获取所有图片文件
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
            image_files = []
            for extension in image_extensions:
                image_files.extend(glob(os.path.join(self.input_dir, extension)))
                image_files.extend(glob(os.path.join(self.input_dir, extension.upper())))

            if not image_files:
                self.log_message.emit("未找到任何图片文件！")
                self.finished.emit(False, "未找到任何图片文件")
                return

            total_files = len(image_files)
            self.log_message.emit(f"找到 {total_files} 个图片文件")

            # 创建输出目录
            os.makedirs(self.output_dir, exist_ok=True)

            # 处理每个图片
            for i, image_path in enumerate(image_files):
                if not self.is_running:
                    self.log_message.emit("操作被用户中止")
                    self.finished.emit(False, "操作被用户中止")
                    return

                self.log_message.emit(f"处理图片: {os.path.basename(image_path)}")

                # 读取图片
                img = cv2.imread(image_path)
                if img is None:
                    self.log_message.emit(f"无法读取图片: {image_path}")
                    continue

                # 获取图片尺寸
                h, w = img.shape[:2]

                # 检查分块是否合法
                if w % self.block_width != 0 or h % self.block_height != 0:
                    error_msg = f"图片 {os.path.basename(image_path)} 尺寸 ({w}x{h}) 无法被 {self.block_width}x{self.block_height} 整除"
                    self.log_message.emit(error_msg)
                    self.finished.emit(False, error_msg)
                    return

                # 计算行列数
                rows = h // self.block_height
                cols = w // self.block_width

                # 获取不带扩展名的文件名
                filename = os.path.splitext(os.path.basename(image_path))[0]

                # 分块处理
                for r in range(rows):
                    for c in range(cols):
                        # 计算块的位置
                        y_start = r * self.block_height
                        y_end = y_start + self.block_height
                        x_start = c * self.block_width
                        x_end = x_start + self.block_width

                        # 提取块
                        block = img[y_start:y_end, x_start:x_end]

                        # 保存块
                        block_filename = f"{filename}_{r:02d}_{c:02d}.png"
                        block_path = os.path.join(self.output_dir, block_filename)
                        cv2.imwrite(block_path, block)

                self.progress.emit(int((i + 1) / total_files * 100))

            self.log_message.emit("所有图片分块完成！")
            self.finished.emit(True, "分块完成")

        except Exception as e:
            self.log_message.emit(f"分块过程中发生错误: {str(e)}")
            self.finished.emit(False, str(e))


class MergeImagesThread(ImageProcessingThread):
    """整合处理线程"""

    def __init__(self, input_dir, output_dir):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir

    def run(self):
        try:
            # 获取所有分块图片
            image_files = glob(os.path.join(self.input_dir, "*.png"))
            if not image_files:
                self.log_message.emit("未找到任何分块图片文件！")
                self.finished.emit(False, "未找到任何分块图片文件")
                return

            # 按原始图片名分组
            image_groups = {}
            for file_path in image_files:
                filename = os.path.basename(file_path)
                # 解析文件名格式: 原文件名_行号_列号.png
                if "_" not in filename or filename.count("_") < 2:
                    continue

                parts = filename.rsplit("_", 2)
                if len(parts) < 3:
                    continue

                base_name = parts[0]
                row_col = parts[1] + "_" + parts[2].split(".")[0]

                if base_name not in image_groups:
                    image_groups[base_name] = {}

                image_groups[base_name][row_col] = file_path

            if not image_groups:
                self.log_message.emit("未找到有效的分块图片文件！")
                self.finished.emit(False, "未找到有效的分块图片文件")
                return

            total_groups = len(image_groups)
            self.log_message.emit(f"找到 {total_groups} 组图片分块")

            # 创建输出目录
            os.makedirs(self.output_dir, exist_ok=True)

            # 处理每组图片
            for i, (base_name, blocks) in enumerate(image_groups.items()):
                if not self.is_running:
                    self.log_message.emit("操作被用户中止")
                    self.finished.emit(False, "操作被用户中止")
                    return

                self.log_message.emit(f"整合图片: {base_name}")

                # 获取所有行列号
                rows = []
                cols = []
                for rc in blocks.keys():
                    r, c = rc.split("_")
                    rows.append(int(r))
                    cols.append(int(c))

                max_row = max(rows)
                max_col = max(cols)

                # 读取第一块获取尺寸
                first_block_path = list(blocks.values())[0]
                first_block = cv2.imread(first_block_path)
                if first_block is None:
                    self.log_message.emit(f"无法读取分块图片: {first_block_path}")
                    continue

                block_h, block_w = first_block.shape[:2]

                # 计算完整图片尺寸
                full_h = (max_row + 1) * block_h
                full_w = (max_col + 1) * block_w

                # 创建空白画布
                full_image = np.zeros((full_h, full_w, 3), dtype=np.uint8)

                # 填充图片
                for rc, block_path in blocks.items():
                    r, c = map(int, rc.split("_"))
                    block = cv2.imread(block_path)
                    if block is not None:
                        y_start = r * block_h
                        y_end = y_start + block_h
                        x_start = c * block_w
                        x_end = x_start + block_w
                        full_image[y_start:y_end, x_start:x_end] = block

                # 保存完整图片
                output_path = os.path.join(self.output_dir, f"{base_name}.png")
                cv2.imwrite(output_path, full_image)

                self.progress.emit(int((i + 1) / total_groups * 100))

            self.log_message.emit("所有图片整合完成！")
            self.finished.emit(True, "整合完成")

        except Exception as e:
            self.log_message.emit(f"整合过程中发生错误: {str(e)}")
            self.finished.emit(False, str(e))


class EvaluateImagesThread(ImageProcessingThread):
    """评估处理线程"""

    def __init__(self, pred_dir, gt_dir, output_dir):
        super().__init__()
        self.pred_dir = pred_dir
        self.gt_dir = gt_dir
        self.output_dir = output_dir
        self.results = []

    def run(self):
        try:
            # 获取预测图片
            pred_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
            pred_files = []
            for extension in pred_extensions:
                pred_files.extend(glob(os.path.join(self.pred_dir, extension)))
                pred_files.extend(glob(os.path.join(self.pred_dir, extension.upper())))

            if not pred_files:
                self.log_message.emit("未找到任何预测图片文件！")
                self.finished.emit(False, "未找到任何预测图片文件")
                return

            # 获取GT图片
            gt_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
            gt_files = []
            for extension in gt_extensions:
                gt_files.extend(glob(os.path.join(self.gt_dir, extension)))
                gt_files.extend(glob(os.path.join(self.gt_dir, extension.upper())))

            if not gt_files:
                self.log_message.emit("未找到任何GT图片文件！")
                self.finished.emit(False, "未找到任何GT图片文件")
                return

            total_files = len(pred_files)
            self.log_message.emit(f"找到 {total_files} 个预测图片文件")
            self.log_message.emit(f"找到 {len(gt_files)} 个GT图片文件")

            # 创建输出目录
            os.makedirs(self.output_dir, exist_ok=True)

            # 处理每个图片
            for i, pred_path in enumerate(pred_files):
                if not self.is_running:
                    self.log_message.emit("操作被用户中止")
                    self.finished.emit(False, "操作被用户中止")
                    return

                pred_filename = os.path.basename(pred_path)
                self.log_message.emit(f"评估图片: {pred_filename}")

                # 查找对应的GT图片
                gt_path = None
                for gt_file in gt_files:
                    if os.path.basename(gt_file) == pred_filename:
                        gt_path = gt_file
                        break

                if not gt_path:
                    self.log_message.emit(f"未找到 {pred_filename} 对应的GT图片")
                    continue

                # 读取图片
                pred_img = cv2.imread(pred_path)
                gt_img = cv2.imread(gt_path)

                if pred_img is None:
                    self.log_message.emit(f"无法读取预测图片: {pred_path}")
                    continue

                if gt_img is None:
                    self.log_message.emit(f"无法读取GT图片: {gt_path}")
                    continue

                # 检查尺寸是否一致
                if pred_img.shape != gt_img.shape:
                    self.log_message.emit(f"图片尺寸不匹配: {pred_filename}")
                    continue

                # 转换为灰度图用于SSIM计算
                pred_gray = cv2.cvtColor(pred_img, cv2.COLOR_BGR2GRAY)
                gt_gray = cv2.cvtColor(gt_img, cv2.COLOR_BGR2GRAY)

                # 计算评估指标
                ssim_value = ssim(pred_gray, gt_gray)
                psnr_value = psnr(gt_img, pred_img)

                # 保存结果
                self.results.append({
                    'filename': pred_filename,
                    'ssim': ssim_value,
                    'psnr': psnr_value
                })

                self.progress.emit(int((i + 1) / total_files * 100))

            # 保存结果到CSV文件
            if self.results:
                csv_path = os.path.join(self.output_dir,
                                        f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['filename', 'ssim', 'psnr']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for result in self.results:
                        writer.writerow(result)

                self.log_message.emit(f"评估结果已保存到: {csv_path}")

            self.log_message.emit("所有图片评估完成！")
            self.finished.emit(True, "评估完成", self.results)

        except Exception as e:
            self.log_message.emit(f"评估过程中发生错误: {str(e)}")
            self.finished.emit(False, str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图像处理工具")
        self.setGeometry(100, 100, 900, 700)

        # 设置样式
        self.setStyleSheet(StyleManager.get_main_stylesheet())

        # 初始化变量
        self.split_thread = None
        self.merge_thread = None
        self.evaluate_thread = None

        self.init_ui()

    def init_ui(self):
        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建选项卡
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # 分块选项卡
        split_tab = QWidget()
        split_layout = QVBoxLayout(split_tab)
        tabs.addTab(split_tab, "图像分块")

        # 整合选项卡
        merge_tab = QWidget()
        merge_layout = QVBoxLayout(merge_tab)
        tabs.addTab(merge_tab, "图像整合")

        # 评估选项卡
        evaluate_tab = QWidget()
        evaluate_layout = QVBoxLayout(evaluate_tab)
        tabs.addTab(evaluate_tab, "图像评估")

        # 日志区域
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # 初始化各选项卡
        self.setup_split_tab(split_layout)
        self.setup_merge_tab(merge_layout)
        self.setup_evaluate_tab(evaluate_layout)

    def setup_split_tab(self, layout):
        # 输入目录选择
        input_group = QGroupBox("输入目录")
        input_layout = QVBoxLayout()
        input_btn_layout = QHBoxLayout()

        self.split_input_edit = QLabel("未选择目录")
        self.split_input_edit.setStyleSheet(StyleManager.get_image_label_style())
        self.split_input_edit.setAlignment(Qt.AlignCenter)
        self.split_input_edit.setMinimumHeight(40)

        self.split_input_btn = QPushButton("选择目录")
        self.split_input_btn.clicked.connect(self.select_split_input_dir)

        input_btn_layout.addWidget(self.split_input_edit)
        input_btn_layout.addWidget(self.split_input_btn)
        input_layout.addLayout(input_btn_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 输出目录选择
        output_group = QGroupBox("输出目录")
        output_layout = QVBoxLayout()
        output_btn_layout = QHBoxLayout()

        self.split_output_edit = QLabel("未选择目录")
        self.split_output_edit.setStyleSheet(StyleManager.get_image_label_style())
        self.split_output_edit.setAlignment(Qt.AlignCenter)
        self.split_output_edit.setMinimumHeight(40)

        self.split_output_btn = QPushButton("选择目录")
        self.split_output_btn.clicked.connect(self.select_split_output_dir)

        output_btn_layout.addWidget(self.split_output_edit)
        output_btn_layout.addWidget(self.split_output_btn)
        output_layout.addLayout(output_btn_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # 分块参数设置
        param_group = QGroupBox("分块参数")
        param_layout = QHBoxLayout()

        param_layout.addWidget(QLabel("宽度:"))
        self.split_width_spin = QSpinBox()
        self.split_width_spin.setRange(1, 10000)
        self.split_width_spin.setValue(1024)
        param_layout.addWidget(self.split_width_spin)

        param_layout.addWidget(QLabel("高度:"))
        self.split_height_spin = QSpinBox()
        self.split_height_spin.setRange(1, 10000)
        self.split_height_spin.setValue(1024)
        param_layout.addWidget(self.split_height_spin)

        param_layout.addStretch()
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # 开始按钮
        self.split_start_btn = QPushButton("开始分块")
        self.split_start_btn.clicked.connect(self.start_split)
        layout.addWidget(self.split_start_btn)

        layout.addStretch()

    def setup_merge_tab(self, layout):
        # 输入目录选择
        input_group = QGroupBox("分块图片目录")
        input_layout = QVBoxLayout()
        input_btn_layout = QHBoxLayout()

        self.merge_input_edit = QLabel("未选择目录")
        self.merge_input_edit.setStyleSheet(StyleManager.get_image_label_style())
        self.merge_input_edit.setAlignment(Qt.AlignCenter)
        self.merge_input_edit.setMinimumHeight(40)

        self.merge_input_btn = QPushButton("选择目录")
        self.merge_input_btn.clicked.connect(self.select_merge_input_dir)

        input_btn_layout.addWidget(self.merge_input_edit)
        input_btn_layout.addWidget(self.merge_input_btn)
        input_layout.addLayout(input_btn_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 输出目录选择
        output_group = QGroupBox("输出目录")
        output_layout = QVBoxLayout()
        output_btn_layout = QHBoxLayout()

        self.merge_output_edit = QLabel("未选择目录")
        self.merge_output_edit.setStyleSheet(StyleManager.get_image_label_style())
        self.merge_output_edit.setAlignment(Qt.AlignCenter)
        self.merge_output_edit.setMinimumHeight(40)

        self.merge_output_btn = QPushButton("选择目录")
        self.merge_output_btn.clicked.connect(self.select_merge_output_dir)

        output_btn_layout.addWidget(self.merge_output_edit)
        output_btn_layout.addWidget(self.merge_output_btn)
        output_layout.addLayout(output_btn_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # 开始按钮
        self.merge_start_btn = QPushButton("开始整合")
        self.merge_start_btn.clicked.connect(self.start_merge)
        layout.addWidget(self.merge_start_btn)

        layout.addStretch()

    def setup_evaluate_tab(self, layout):
        # 预测图目录选择
        pred_group = QGroupBox("预测图目录")
        pred_layout = QVBoxLayout()
        pred_btn_layout = QHBoxLayout()

        self.eval_pred_edit = QLabel("未选择目录")
        self.eval_pred_edit.setStyleSheet(StyleManager.get_image_label_style())
        self.eval_pred_edit.setAlignment(Qt.AlignCenter)
        self.eval_pred_edit.setMinimumHeight(40)

        self.eval_pred_btn = QPushButton("选择目录")
        self.eval_pred_btn.clicked.connect(self.select_eval_pred_dir)

        pred_btn_layout.addWidget(self.eval_pred_edit)
        pred_btn_layout.addWidget(self.eval_pred_btn)
        pred_layout.addLayout(pred_btn_layout)
        pred_group.setLayout(pred_layout)
        layout.addWidget(pred_group)

        # GT图目录选择
        gt_group = QGroupBox("GT图目录")
        gt_layout = QVBoxLayout()
        gt_btn_layout = QHBoxLayout()

        self.eval_gt_edit = QLabel("未选择目录")
        self.eval_gt_edit.setStyleSheet(StyleManager.get_image_label_style())
        self.eval_gt_edit.setAlignment(Qt.AlignCenter)
        self.eval_gt_edit.setMinimumHeight(40)

        self.eval_gt_btn = QPushButton("选择目录")
        self.eval_gt_btn.clicked.connect(self.select_eval_gt_dir)

        gt_btn_layout.addWidget(self.eval_gt_edit)
        gt_btn_layout.addWidget(self.eval_gt_btn)
        gt_layout.addLayout(gt_btn_layout)
        gt_group.setLayout(gt_layout)
        layout.addWidget(gt_group)

        # 输出目录选择
        output_group = QGroupBox("输出目录")
        output_layout = QVBoxLayout()
        output_btn_layout = QHBoxLayout()

        self.eval_output_edit = QLabel("未选择目录")
        self.eval_output_edit.setStyleSheet(StyleManager.get_image_label_style())
        self.eval_output_edit.setAlignment(Qt.AlignCenter)
        self.eval_output_edit.setMinimumHeight(40)

        self.eval_output_btn = QPushButton("选择目录")
        self.eval_output_btn.clicked.connect(self.select_eval_output_dir)

        output_btn_layout.addWidget(self.eval_output_edit)
        output_btn_layout.addWidget(self.eval_output_btn)
        output_layout.addLayout(output_btn_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # 开始按钮
        self.eval_start_btn = QPushButton("开始评估")
        self.eval_start_btn.clicked.connect(self.start_evaluate)
        layout.addWidget(self.eval_start_btn)

        # 结果表格
        result_group = QGroupBox("评估结果")
        result_layout = QVBoxLayout()
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["文件名", "SSIM", "PSNR"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        result_layout.addWidget(self.result_table)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

    def select_split_input_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输入目录")
        if directory:
            self.split_input_edit.setText(directory)

    def select_split_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.split_output_edit.setText(directory)

    def select_merge_input_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择分块图片目录")
        if directory:
            self.merge_input_edit.setText(directory)

    def select_merge_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.merge_output_edit.setText(directory)

    def select_eval_pred_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择预测图目录")
        if directory:
            self.eval_pred_edit.setText(directory)

    def select_eval_gt_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择GT图目录")
        if directory:
            self.eval_gt_edit.setText(directory)

    def select_eval_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.eval_output_edit.setText(directory)

    def start_split(self):
        input_dir = self.split_input_edit.text()
        output_dir = self.split_output_edit.text()
        block_width = self.split_width_spin.value()
        block_height = self.split_height_spin.value()

        if input_dir == "未选择目录" or not os.path.exists(input_dir):
            QMessageBox.warning(self, "警告", "请选择有效的输入目录")
            return

        if output_dir == "未选择目录":
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return

        # 禁用按钮
        self.split_start_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        # 创建并启动线程
        self.split_thread = SplitImagesThread(input_dir, output_dir, block_width, block_height)
        self.split_thread.progress.connect(self.update_progress)
        self.split_thread.log_message.connect(self.log_message)
        self.split_thread.finished.connect(self.split_finished)
        self.split_thread.start()

    def start_merge(self):
        input_dir = self.merge_input_edit.text()
        output_dir = self.merge_output_edit.text()

        if input_dir == "未选择目录" or not os.path.exists(input_dir):
            QMessageBox.warning(self, "警告", "请选择有效的分块图片目录")
            return

        if output_dir == "未选择目录":
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return

        # 禁用按钮
        self.merge_start_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        # 创建并启动线程
        self.merge_thread = MergeImagesThread(input_dir, output_dir)
        self.merge_thread.progress.connect(self.update_progress)
        self.merge_thread.log_message.connect(self.log_message)
        self.merge_thread.finished.connect(self.merge_finished)
        self.merge_thread.start()

    def start_evaluate(self):
        pred_dir = self.eval_pred_edit.text()
        gt_dir = self.eval_gt_edit.text()
        output_dir = self.eval_output_edit.text()

        if pred_dir == "未选择目录" or not os.path.exists(pred_dir):
            QMessageBox.warning(self, "警告", "请选择有效的预测图目录")
            return

        if gt_dir == "未选择目录" or not os.path.exists(gt_dir):
            QMessageBox.warning(self, "警告", "请选择有效的GT图目录")
            return

        if output_dir == "未选择目录":
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return

        # 禁用按钮
        self.eval_start_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        # 创建并启动线程
        self.evaluate_thread = EvaluateImagesThread(pred_dir, gt_dir, output_dir)
        self.evaluate_thread.progress.connect(self.update_progress)
        self.evaluate_thread.log_message.connect(self.log_message)
        self.evaluate_thread.finished.connect(self.evaluate_finished)
        self.evaluate_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def log_message(self, message):
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        self.log_text.moveCursor(QTextCursor.End)

    def split_finished(self, success, message):
        self.split_start_btn.setEnabled(True)
        if not success:
            QMessageBox.warning(self, "分块失败", message)
        else:
            QMessageBox.information(self, "完成", message)

    def merge_finished(self, success, message):
        self.merge_start_btn.setEnabled(True)
        if not success:
            QMessageBox.warning(self, "整合失败", message)
        else:
            QMessageBox.information(self, "完成", message)

    def evaluate_finished(self, success, message, results=None):
        self.eval_start_btn.setEnabled(True)
        if not success:
            QMessageBox.warning(self, "评估失败", message)
        else:
            QMessageBox.information(self, "完成", message)
            if results:
                self.display_results(results)

    def display_results(self, results):
        self.result_table.setRowCount(len(results))

        for i, result in enumerate(results):
            self.result_table.setItem(i, 0, QTableWidgetItem(result['filename']))
            self.result_table.setItem(i, 1, QTableWidgetItem(f"{result['ssim']:.4f}"))
            self.result_table.setItem(i, 2, QTableWidgetItem(f"{result['psnr']:.2f}"))

    def closeEvent(self, event):
        # 停止所有运行的线程
        if self.split_thread and self.split_thread.isRunning():
            self.split_thread.stop()
            self.split_thread.wait()

        if self.merge_thread and self.merge_thread.isRunning():
            self.merge_thread.stop()
            self.merge_thread.wait()

        if self.evaluate_thread and self.evaluate_thread.isRunning():
            self.evaluate_thread.stop()
            self.evaluate_thread.wait()

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用程序字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())