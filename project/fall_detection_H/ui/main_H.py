#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced UI Main - 主界面实现
包含完整的增强UI界面
"""

import sys
import os
import cv2
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import numpy as np

# 导入自定义模块
from Xmanager import StyleManager, CameraManager, ModelManager, DetectionThread, YOLO
from Components import (BatchDetectionThread, DetectionResultWidget,
                        ModelSelectionDialog, MonitoringWidget, VideoWidget, EnhancedMonitoringWidget, SnapshotWidget)


class EnhancedDetectionUI(QMainWindow):
    """增强的检测UI主窗口"""

    def __init__(self):
        super().__init__()
        self.model = None
        self.detection_thread = None
        self.batch_detection_thread = None
        self.current_source_type = 'image'
        self.current_source_path = None
        self.confidence_threshold = 0.25
        self.batch_results = []
        self.current_batch_index = 0

        # 快照相关属性
        self.is_auto_saving = False
        self.video_recorder = None
        self.history_dir = Path("detection_history")
        self.history_dir.mkdir(exist_ok=True)

        # 管理器
        self.camera_manager = CameraManager()
        self.model_manager = ModelManager()
        self.log_text = QTextEdit()
        self.init_ui()
        self.setWindowIcon(self.create_enhanced_icon())

        # 应用样式
        self.setStyleSheet(StyleManager.get_main_stylesheet())
        self.setup_title_shortcut()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("🚀 医院摔倒实时检测系统 ")
        self.setGeometry(100, 100, 1400, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)

        # 左侧控制面板
        left_widget = self.create_control_panel()
        left_widget.setMaximumWidth(500)
        left_widget.setMinimumWidth(400)

        # 右侧显示区域
        right_widget = self.create_display_area()

        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([450, 1250])

        main_layout.addWidget(main_splitter)

        # 状态栏
        self.statusBar().showMessage("🎯 就绪 - 请选择模型和检测源")

        # 尝试加载默认模型
        self.try_load_default_model()

    def setup_title_shortcut(self):
        """设置标题编辑快捷键"""
        title_shortcut = QShortcut(QKeySequence("F2"), self)
        title_shortcut.activated.connect(self.edit_window_title)
        # 添加新的 Ctrl+R 快捷键
        title_shortcut_ctrl_r = QShortcut(QKeySequence("Ctrl+R"), self)
        title_shortcut_ctrl_r.activated.connect(self.edit_window_title)

    def edit_window_title(self):
        """编辑窗口标题"""
        current_title = self.windowTitle().strip()
        new_title, ok = QInputDialog.getText(
            self,
            "编辑窗口标题",
            "请输入新的窗口标题:",
            text=current_title
        )

        if ok and new_title:
            self.setWindowTitle(new_title)
    def create_control_panel(self):
        """创建控制面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 模型配置
        model_group = QGroupBox("🤖 模型配置")
        model_layout = QVBoxLayout(model_group)

        # 模型选择
        model_select_layout = QHBoxLayout()
        model_select_layout.addWidget(QLabel("选择模型:"))

        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        self.init_model_combo()
        model_select_layout.addWidget(self.model_combo)

        advanced_model_btn = QPushButton("🔧 高级")
        advanced_model_btn.clicked.connect(self.show_model_selection_dialog)
        advanced_model_btn.setMaximumWidth(80)
        model_select_layout.addWidget(advanced_model_btn)

        model_layout.addLayout(model_select_layout)

        # 置信度配置
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("置信度阈值:"))

        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setMinimum(1)
        self.conf_slider.setMaximum(100)
        self.conf_slider.setValue(25)
        self.conf_slider.valueChanged.connect(self.on_confidence_changed)
        conf_layout.addWidget(self.conf_slider)

        self.conf_spinbox = QDoubleSpinBox()
        self.conf_spinbox.setRange(0.01, 1.0)
        self.conf_spinbox.setSingleStep(0.01)
        self.conf_spinbox.setValue(0.25)
        self.conf_spinbox.setDecimals(2)
        self.conf_spinbox.valueChanged.connect(self.on_confidence_spinbox_changed)
        conf_layout.addWidget(self.conf_spinbox)

        model_layout.addLayout(conf_layout)
        layout.addWidget(model_group)

        # 检测源配置
        source_group = QGroupBox("📁 检测源配置")
        source_layout = QVBoxLayout(source_group)

        # 检测模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("检测模式:"))

        self.source_combo = QComboBox()
        self.source_combo.addItems(["📷 单张图片", "🎬 视频文件", "📹 摄像头", "📂 文件夹批量"])
        self.source_combo.currentTextChanged.connect(self.on_source_changed)
        mode_layout.addWidget(self.source_combo)
        source_layout.addLayout(mode_layout)

        # 摄像头选择（仅摄像头模式显示）
        self.camera_select_layout = QHBoxLayout()
        self.camera_select_layout.addWidget(QLabel("摄像头:"))

        self.camera_combo = QComboBox()
        self.refresh_camera_list()
        self.camera_select_layout.addWidget(self.camera_combo)

        refresh_camera_btn = QPushButton("🔄")
        refresh_camera_btn.setMaximumWidth(40)
        refresh_camera_btn.clicked.connect(self.refresh_camera_list)
        self.camera_select_layout.addWidget(refresh_camera_btn)

        source_layout.addLayout(self.camera_select_layout)

        # 文件选择
        file_layout = QHBoxLayout()
        # self.select_file_btn = QPushButton("📁 选择文件/文件夹")
        self.select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.select_file_btn)
        source_layout.addLayout(file_layout)

        # 当前文件显示
        self.current_file_label = QLabel("未选择文件")
        self.current_file_label.setWordWrap(True)
        self.current_file_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 5px;")
        source_layout.addWidget(self.current_file_label)

        layout.addWidget(source_group)

        # 检测控制
        control_group = QGroupBox("🎮 检测控制")
        control_layout = QVBoxLayout(control_group)

        # 控制按钮
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶️ 开始检测")
        self.start_btn.clicked.connect(self.start_detection)
        self.start_btn.setEnabled(False)
        btn_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("⏸️ 暂停")
        self.pause_btn.clicked.connect(self.pause_detection)
        self.pause_btn.setEnabled(False)
        btn_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_detection)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        self.video_is_auto_saving = False
        self.kuaizhao_btn = QPushButton("🎬 快照")
        self.kuaizhao_btn.clicked.connect(self.kuaizhao_detection)
        self.kuaizhao_btn.setEnabled(False)
        btn_layout.addWidget(self.kuaizhao_btn)

        control_layout.addLayout(btn_layout)

        # 进度条
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("进度:"))

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        control_layout.addLayout(progress_layout)

        layout.addWidget(control_group)

        # 检测结果详情
        # self.result_detail_widget = DetectionResultWidget()
        # layout.addWidget(self.result_detail_widget)

        # 日志区域
        log_group = QGroupBox("📋 运行日志")
        log_layout = QVBoxLayout(log_group)


        self.log_text.setMinimumHeight(180)
        self.log_text.setFont(QFont("Consolas", 10))
        log_layout.addWidget(self.log_text)

        log_btn_layout = QHBoxLayout()
        log_btn_layout.addStretch()

        self.clear_log_btn = QPushButton("🗑️ 清除")
        self.clear_log_btn.clicked.connect(self.clear_log)
        self.clear_log_btn.setMaximumWidth(100)
        log_btn_layout.addWidget(self.clear_log_btn)

        log_layout.addLayout(log_btn_layout)
        layout.addWidget(log_group)

        # layout.addStretch()
        return widget

    def create_display_area(self):
        """创建显示区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 创建标签页
        self.tab_widget = QTabWidget()

        # 实时检测标签页
        realtime_tab = self.create_realtime_tab()
        self.tab_widget.addTab(realtime_tab, "🎯 实时检测")

        # 批量结果标签页
        batch_tab = self.create_batch_tab()
        self.tab_widget.addTab(batch_tab, "📊 批量结果")

        # 监控页面标签页
        monitor_tab = MonitoringWidget(self.model_manager, self.camera_manager)
        self.tab_widget.addTab(monitor_tab, "🖥️ 实时监控")
        
        # 监控快照标签页
        self.snapshot_widget = SnapshotWidget()
        self.tab_widget.addTab(self.snapshot_widget, "🎬 监控快照")
        
        layout.addWidget(self.tab_widget)
        return widget

    def create_realtime_tab(self):
        """创建实时检测标签页"""
        widget = QWidget()
        layout_top = QVBoxLayout(widget)
        layout = QHBoxLayout(widget)

        # 原图显示
        original_container = QWidget()
        original_layout = QVBoxLayout(original_container)

        original_title = QLabel("📷 源")
        original_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; margin: 0px;")
        original_layout.addWidget(original_title)

        self.original_label = QLabel("等待加载源...")
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setMinimumSize(500, 400)
        self.original_label.setStyleSheet(StyleManager.get_image_label_style())
        original_layout.addWidget(self.original_label)

        # 结果图显示
        result_container = QWidget()
        result_layout = QVBoxLayout(result_container)

        result_title = QLabel("🎯 检测结果")
        result_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; margin: 0px;")
        result_layout.addWidget(result_title)

        self.result_label = QLabel("等待检测结果...")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setMinimumSize(500, 400)
        self.result_label.setStyleSheet(StyleManager.get_image_label_style())
        result_layout.addWidget(self.result_label)

        layout.addWidget(original_container)
        layout.addWidget(result_container)
        layout_top.addLayout(layout)
        # 检测结果详情
        self.result_detail_widget = DetectionResultWidget()
        layout_top.addWidget(self.result_detail_widget)
        layout_top.addStretch()
        return widget

    def create_batch_tab(self):
        """创建批量结果标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 控制栏
        control_bar = QHBoxLayout()
        control_bar.addWidget(QLabel("📊 批量检测结果:"))
        control_bar.addStretch()

        # 导航按钮
        self.prev_result_btn = QPushButton("⬅️ 上一个")
        self.prev_result_btn.clicked.connect(self.show_prev_result)
        self.prev_result_btn.setEnabled(False)
        control_bar.addWidget(self.prev_result_btn)

        self.result_index_label = QLabel("0/0")
        self.result_index_label.setStyleSheet("font-weight: bold; margin: 0 10px;")
        control_bar.addWidget(self.result_index_label)

        self.next_result_btn = QPushButton("下一个 ➡️")
        self.next_result_btn.clicked.connect(self.show_next_result)
        self.next_result_btn.setEnabled(False)
        control_bar.addWidget(self.next_result_btn)

        # 保存按钮
        self.save_results_btn = QPushButton("💾 保存结果")
        self.save_results_btn.clicked.connect(self.save_batch_results)
        self.save_results_btn.setEnabled(False)
        control_bar.addWidget(self.save_results_btn)

        # 清空按钮
        self.clear_results_btn = QPushButton("🗑️ 清空结果")
        self.clear_results_btn.clicked.connect(self.clear_batch_results)
        self.clear_results_btn.setEnabled(False)
        control_bar.addWidget(self.clear_results_btn)

        layout.addLayout(control_bar)

        # 图像显示
        image_layout = QHBoxLayout()

        self.batch_original_label = QLabel("📷 批量检测: 原图")
        self.batch_original_label.setAlignment(Qt.AlignCenter)
        self.batch_original_label.setMinimumSize(500, 400)
        self.batch_original_label.setStyleSheet(StyleManager.get_image_label_style())

        self.batch_result_label = QLabel("🎯 批量检测: 结果图")
        self.batch_result_label.setAlignment(Qt.AlignCenter)
        self.batch_result_label.setMinimumSize(500, 400)
        self.batch_result_label.setStyleSheet(StyleManager.get_image_label_style())

        image_layout.addWidget(self.batch_original_label)
        image_layout.addWidget(self.batch_result_label)
        layout.addLayout(image_layout)

        # 结果信息
        self.batch_info_label = QLabel("📁 选择文件夹开始批量检测...")
        self.batch_info_label.setWordWrap(True)
        self.batch_info_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(236, 240, 241, 0.9), stop:1 rgba(189, 195, 199, 0.9));
            padding: 15px;
            border-radius: 8px;
            font-size: 12px;
            color: #2c3e50;
        """)
        layout.addWidget(self.batch_info_label)

        return widget



    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"🕒 {current_time}")

    def start_all_cameras(self):
        """启动所有选中的摄像头"""
        selected_cameras = [i for i, cb in enumerate(self.camera_checkboxes) if cb.isChecked()]
        for cam_idx in selected_cameras:
            self.start_camera(cam_idx)

    def pause_all_cameras(self):
        """暂停所有摄像头"""
        for widget in self.video_widgets:
            if widget.isVisible():
                widget.pause_detection()

    def stop_all_cameras(self):
        """停止所有摄像头"""
        for widget in self.video_widgets:
            if widget.isVisible():
                widget.stop_detection()

    def clear_all_cameras(self):
        """清空所有摄像头画面"""
        for widget in self.video_widgets:
            if widget.isVisible():
                widget.clear_frame()

    def monitor_all_cameras(self):
        """将所有摄像头切换为监控模式"""
        for widget in self.video_widgets:
            if widget.isVisible():
                widget.set_monitor_mode(True)

    def start_camera(self, camera_index):
        """启动指定摄像头"""
        if 0 <= camera_index < len(self.video_widgets):
            widget = self.video_widgets[camera_index]
            widget.show()
            widget.start_detection(camera_index + 1)  # 假设摄像头ID从1开始

    def update_stats(self, fall_count=0, normal_count=0):
        """更新统计信息"""
        total = fall_count + normal_count
        self.stats_label.setText(f"📊 今日检测: {total} | 跌倒: {fall_count} | 正常: {normal_count}")

    def init_model_combo(self):
        """初始化模型下拉框"""
        self.model_combo.clear()
        models = self.model_manager.scan_models()

        if not models:
            self.model_combo.addItem("无可用模型")
            self.model_combo.setEnabled(False)
        else:
            self.model_combo.addItems([model['name'] for model in models])
            self.model_combo.setEnabled(True)

    def try_load_default_model(self):
        """尝试加载默认模型"""
        if self.model_combo.count() > 0 and self.model_combo.itemText(0) != "无可用模型":
            first_model = self.model_combo.itemText(0)
            self.load_model_by_name(first_model)

    def load_model_by_name(self, model_name):
        """根据名称加载模型"""
        models = self.model_manager.scan_models()
        for model in models:
            if model['name'] == model_name:
                self.load_model(model['path'])
                break

    def load_model(self, model_path):
        """加载模型"""
        try:
            self.model = YOLO(model_path)
            self.log_message(f"✅ 模型加载成功: {Path(model_path).name}")
            self.select_file_btn = QPushButton("📁 选择文件/文件夹")
            self.update_button_states()
            return True
        except Exception as e:
            self.log_message(f"❌ 模型加载失败: {str(e)}")
            self.model = None
            return False

    def show_model_selection_dialog(self):
        """显示模型选择对话框"""
        dialog = ModelSelectionDialog(self.model_manager, self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_model:
            if self.load_model(dialog.selected_model):
                model_name = Path(dialog.selected_model).name
                # 更新下拉框
                index = self.model_combo.findText(model_name)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)
                else:
                    self.model_combo.addItem(model_name)
                    self.model_combo.setCurrentText(model_name)

    def refresh_camera_list(self):
        """刷新摄像头列表"""
        self.camera_manager.scan_cameras()
        self.camera_combo.clear()

        cameras = self.camera_manager.get_available_cameras()
        if cameras:
            for camera in cameras:
                self.camera_combo.addItem(f"{camera['name']} ({camera['resolution']})", camera['id'])
        else:
            self.camera_combo.addItem("未检测到摄像头", -1)

    def on_model_changed(self, model_text):
        """模型选择改变"""
        if model_text != "无可用模型":
            self.load_model_by_name(model_text)

    def on_confidence_changed(self, value):
        """置信度滑块改变"""
        conf_value = value / 100.0
        self.confidence_threshold = conf_value
        self.conf_spinbox.blockSignals(True)
        self.conf_spinbox.setValue(conf_value)
        self.conf_spinbox.blockSignals(False)

    def on_confidence_spinbox_changed(self, value):
        """置信度数值框改变"""
        self.confidence_threshold = value
        self.conf_slider.blockSignals(True)
        self.conf_slider.setValue(int(value * 100))
        self.conf_slider.blockSignals(False)

    def on_source_changed(self, source_text):
        """检测源改变"""
        source_map = {
            "📷 单张图片": "image",
            "🎬 视频文件": "video",
            "📹 摄像头": "camera",
            "📂 文件夹批量": "batch"
        }
        self.current_source_type = source_map.get(source_text)

        # 显示/隐藏摄像头选择
        is_camera = self.current_source_type == "camera"
        for i in range(self.camera_select_layout.count()):
            item = self.camera_select_layout.itemAt(i)
            if item.widget():
                item.widget().setVisible(is_camera)

        self.current_source_path = None
        self.current_file_label.setText("未选择文件")
        self.clear_display_windows()
        self.update_button_states()

    def update_button_states(self):
        """更新按钮状态"""
        has_model = self.model is not None

        if self.current_source_type == "camera":
            has_source = self.camera_combo.currentData() != -1
            self.select_file_btn.setEnabled(False)
        else:
            has_source = self.current_source_path is not None
            self.select_file_btn.setEnabled(True)

        self.start_btn.setEnabled(has_model and has_source)

    def select_file(self):
        """选择文件或文件夹"""
        if self.current_source_type == "image":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择图片", "",
                "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff *.webp);;所有文件 (*)"
            )
        elif self.current_source_type == "video":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择视频", "",
                "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv);;所有文件 (*)"
            )
        elif self.current_source_type == "batch":
            file_path = QFileDialog.getExistingDirectory(self, "选择包含图片的文件夹")
        else:
            return

        if file_path:
            self.current_source_path = file_path
            self.current_file_label.setText(f"📁 已选择: {Path(file_path).name}")
            self.log_message(f"📁 已选择: {file_path}")
            self.update_button_states()

            if self.current_source_type in ["image", "video"]:
                self.preview_file(file_path)

    def preview_file(self, file_path):
        """预览文件"""
        try:
            if self.current_source_type == "image":
                img = cv2.imread(file_path)
                if img is not None:
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    self.display_image(img_rgb, self.original_label)
                    self.result_label.clear()
                    self.result_label.setText("等待检测结果...")
        except Exception as e:
            self.log_message(f"❌ 预览文件失败: {str(e)}")

    def start_detection(self):
        """开始检测"""
        if not self.model:
            self.log_message("❌ 错误: 模型未加载")
            return

        if self.current_source_type == "batch":
            self.start_batch_detection()
        else:
            self.start_single_detection()

    def start_single_detection(self):
        """开始单个检测"""
        camera_id = 0
        if self.current_source_type == "camera":
            camera_id = self.camera_combo.currentData()
            if camera_id == -1:
                self.log_message("❌ 错误: 没有可用的摄像头")
                return

        self.detection_thread = DetectionThread(
            self.model, self.current_source_type, self.current_source_path, camera_id, self.confidence_threshold
        )
        self.detection_thread.result_ready.connect(self.on_detection_result)
        self.detection_thread.progress_updated.connect(self.progress_bar.setValue)
        self.detection_thread.status_changed.connect(self.statusBar().showMessage)
        self.detection_thread.error_occurred.connect(self.log_message)
        self.detection_thread.finished.connect(self.on_detection_finished)

        self.update_detection_ui_state(True)
        self.tab_widget.setCurrentIndex(0)  # 切换到实时检测

        self.detection_thread.start()
        self.log_message(f"🚀 开始{self.current_source_type}检测...")

    def start_batch_detection(self):
        """开始批量检测"""
        self.batch_results.clear()

        self.batch_detection_thread = BatchDetectionThread(
            self.model, self.current_source_path, self.confidence_threshold
        )
        self.batch_detection_thread.result_ready.connect(self.on_batch_result)
        self.batch_detection_thread.progress_updated.connect(self.progress_bar.setValue)
        self.batch_detection_thread.current_file_changed.connect(self.statusBar().showMessage)
        self.batch_detection_thread.finished.connect(self.on_batch_finished)

        self.update_detection_ui_state(True)
        self.tab_widget.setCurrentIndex(1)  # 切换到批量结果

        self.batch_detection_thread.start()
        self.log_message("🚀 开始批量检测...")

    def update_detection_ui_state(self, detecting):
        """更新检测状态的UI"""
        self.start_btn.setEnabled(not detecting)
        self.pause_btn.setEnabled(detecting and self.current_source_type != "batch")
        self.stop_btn.setEnabled(detecting)
        self.source_combo.setEnabled(not detecting)
        self.select_file_btn.setEnabled(not detecting and self.current_source_type != "camera")
        self.model_combo.setEnabled(not detecting)
        # 更新快照按钮状态
        self.kuaizhao_btn.setEnabled(detecting and self.current_source_type in ["camera", "video"])

    def pause_detection(self):
        """暂停/恢复检测"""
        if self.detection_thread and self.detection_thread.is_running:
            if self.detection_thread.is_paused:
                self.detection_thread.resume()
                self.pause_btn.setText("⏸️ 暂停")
                self.log_message("▶️ 检测已恢复")
            else:
                self.detection_thread.pause()
                self.pause_btn.setText("▶️ 继续")
                self.log_message("⏸️ 检测已暂停")

    def stop_detection(self):
        """停止检测"""
        if self.detection_thread and self.detection_thread.is_running:
            self.detection_thread.stop()
            self.detection_thread.wait()

        if self.batch_detection_thread and self.batch_detection_thread.is_running:
            self.batch_detection_thread.stop()
            self.batch_detection_thread.wait()

        self.on_detection_finished()

    def kuaizhao_detection(self):
        """切换自动保存监控快照状态"""
        if not self.video_is_auto_saving:
            self.start_auto_save()
        else:
            self.stop_auto_save()

    def start_auto_save(self):
        """开始自动保存快照"""
        if not self.model:
            QMessageBox.warning(self, "警告", "请先选择模型")
            return

        # 初始化视频录制器
        source_name = "摄像头" if self.current_source_type == "camera" else "视频"
        if self.current_source_type == "camera":
            source_id = self.camera_combo.currentData()
            source_name = f"摄像头{source_id}"
        elif self.current_source_type == "video":
            source_name = Path(self.current_source_path).stem

        self.video_recorder = DetectionVideoRecorder(
            source_name, self.history_dir
        )
        self.video_recorder.start_recording()

        self.video_is_auto_saving = True
        self.kuaizhao_btn.setText("⏹️ 停止快照")
        self.log_message("🎬 开始记录快照")

    def stop_auto_save(self):
        """停止自动保存快照"""
        if self.video_recorder:
            self.video_recorder.stop_recording()
            self.video_recorder = None

        self.video_is_auto_saving = False
        self.kuaizhao_btn.setText("🎬 快照")
        self.log_message("⏹️ 停止记录快照")

    def on_detection_result(self, original_img, result_img, inference_time, results, class_names):
        """检测结果回调"""
        # 显示图像
        self.display_image(original_img, self.original_label)
        self.display_image(result_img, self.result_label)

        # 更新结果详情
        self.result_detail_widget.update_results(results, class_names, inference_time)

        # 如果正在录制快照，添加帧
        if self.video_is_auto_saving and self.video_recorder:
            detection_info = {
                'results': results,
                'class_names': class_names,
                'inference_time': inference_time
            }

            self.video_recorder.add_frame(result_img, detection_info)

        # 记录日志（简化版，避免过多输出）
        if results and results[0].boxes and len(results[0].boxes) > 0:
            object_count = len(results[0].boxes)

            # 统计类别
            classes = results[0].boxes.cls.cpu().numpy().astype(int)
            class_counts = {}
            for cls in classes:
                class_name = class_names[cls] if cls < len(class_names) else f"类别{cls}"
                class_counts[class_name] = class_counts.get(class_name, 0) + 1

            class_summary = ", ".join([f"{name}:{count}" for name, count in class_counts.items()])
            self.log_message(f"🎯 检测到 {object_count} 个目标: {class_summary} (耗时: {inference_time:.3f}s)")
        else:
            self.log_message(f"⚪ 未检测到目标 (耗时: {inference_time:.3f}s)")

    def on_batch_result(self, file_path, original_img, result_img, inference_time, results, class_names):
        """批量检测结果回调"""
        # 计算目标数量
        object_count = len(results[0].boxes) if results and results[0].boxes else 0

        # 保存结果
        result_data = {
            'file_path': file_path,
            'original_img': original_img,
            'result_img': result_img,
            'inference_time': inference_time,
            'results': results,
            'class_names': class_names,
            'object_count': object_count
        }

        self.batch_results.append(result_data)

        # 显示第一个结果
        if len(self.batch_results) == 1:
            self.current_batch_index = 0
            self.show_batch_result(0)

        self.update_batch_navigation()

        # 记录日志
        filename = Path(file_path).name
        if object_count > 0:
            self.log_message(f"✅ {filename}: {object_count} 个目标 ({inference_time:.3f}s)")
        else:
            self.log_message(f"⚪ {filename}: 无目标 ({inference_time:.3f}s)")

    def on_batch_finished(self):
        """批量检测完成"""
        total_count = len(self.batch_results)
        total_objects = sum(result['object_count'] for result in self.batch_results)

        self.log_message(f"🎉 批量检测完成! 处理了 {total_count} 张图片，检测到 {total_objects} 个目标")
        self.statusBar().showMessage(f"批量检测完成 - {total_count} 张图片，{total_objects} 个目标")

        self.save_results_btn.setEnabled(True)
        self.clear_results_btn.setEnabled(True)
        self.result_index_label.setText(f"1/{len(self.batch_results)}")
        self.on_detection_finished()

    def on_detection_finished(self):
        """检测完成回调"""
        self.update_detection_ui_state(False)
        self.pause_btn.setText("⏸️ 暂停")
        self.progress_bar.setValue(0)

        # 停止快照录制
        if self.video_is_auto_saving:
            self.stop_auto_save()

    def show_batch_result(self, index):
        """显示批量结果"""
        if 0 <= index < len(self.batch_results):
            result = self.batch_results[index]

            self.display_image(result['original_img'], self.batch_original_label)
            self.display_image(result['result_img'], self.batch_result_label)

            filename = Path(result['file_path']).name
            object_count = result['object_count']
            inference_time = result['inference_time']

            info_text = f"📁 文件: {filename}\n"
            info_text += f"🎯 检测目标: {object_count} 个\n"
            info_text += f"⏱️ 推理耗时: {inference_time:.3f} 秒\n"

            if result['results'] and result['results'][0].boxes and len(result['results'][0].boxes) > 0:
                # 显示类别统计
                classes = result['results'][0].boxes.cls.cpu().numpy().astype(int)
                confidences = result['results'][0].boxes.conf.cpu().numpy()

                class_counts = {}
                for cls in classes:
                    class_name = result['class_names'][cls] if cls < len(result['class_names']) else f"类别{cls}"
                    class_counts[class_name] = class_counts.get(class_name, 0) + 1

                info_text += "📊 类别统计: " + ", ".join(
                    [f"{name}:{count}" for name, count in class_counts.items()]) + ""
                info_text += f"🎯 平均置信度: {np.mean(confidences):.3f}"

            self.batch_info_label.setText(info_text)
            self.result_index_label.setText(f"{index + 1}/{len(self.batch_results)}")

    def show_prev_result(self):
        """显示上一个结果"""
        if self.current_batch_index > 0:
            self.current_batch_index -= 1
            self.show_batch_result(self.current_batch_index)
            self.update_batch_navigation()

    def show_next_result(self):
        """显示下一个结果"""
        if self.current_batch_index < len(self.batch_results) - 1:
            self.current_batch_index += 1
            self.show_batch_result(self.current_batch_index)
            self.update_batch_navigation()

    def update_batch_navigation(self):
        """更新批量结果导航"""
        has_results = len(self.batch_results) > 0
        self.prev_result_btn.setEnabled(has_results and self.current_batch_index > 0)
        self.next_result_btn.setEnabled(has_results and self.current_batch_index < len(self.batch_results) - 1)

    def clear_batch_results(self):
        self.batch_results.clear()
        self.batch_result_label.setText('🎯 批量检测: 结果图')
        self.batch_original_label.setText('📷 批量检测: 原图')
        self.batch_info_label.setText('📁 选择文件夹开始批量检测...')
        self.result_index_label.setText("0/0")
        self.save_results_btn.setEnabled(False)
        self.next_result_btn.setEnabled(False)
        self.prev_result_btn.setEnabled(False)
        self.clear_results_btn.setEnabled(False)


    def save_batch_results(self):
        """保存批量检测结果"""
        if not self.batch_results:
            QMessageBox.information(self, "提示", "没有可保存的结果")
            return

        save_dir = QFileDialog.getExistingDirectory(self, "选择保存目录")
        if not save_dir:
            return

        try:
            save_path = Path(save_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_dir = save_path / f"detection_results_{timestamp}"
            result_dir.mkdir(exist_ok=True)

            # 保存检测结果图片
            for i, result in enumerate(self.batch_results):
                file_name = Path(result['file_path']).stem
                result_img = cv2.cvtColor(result['result_img'], cv2.COLOR_RGB2BGR)
                result_save_path = result_dir / f"{file_name}_result.jpg"
                cv2.imwrite(str(result_save_path), result_img)

            # 保存检测报告
            self.save_detection_report(result_dir)

            QMessageBox.information(self, "成功", f"结果已保存到:\n{result_dir}")
            self.log_message(f"💾 结果已保存到: {result_dir}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
            self.log_message(f"❌ 保存失败: {str(e)}")

    def save_detection_report(self, result_dir):
        """保存检测报告"""
        report_path = result_dir / "detection_report.txt"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("🎯 Enhanced Object Detection System - 批量检测报告\n")
            f.write("=" * 60 + "\n")
            f.write(f"📅 处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"🎚️ 置信度阈值: {self.confidence_threshold}\n")
            f.write(f"📂 处理图片数量: {len(self.batch_results)}\n")
            f.write(f"🎯 总检测目标数: {sum(r['object_count'] for r in self.batch_results)}\n")
            f.write("\n📊 详细结果:\n")
            f.write("-" * 60 + "\n")

            for i, result in enumerate(self.batch_results, 1):
                f.write(f"{i}. 📁 {Path(result['file_path']).name}\n")
                f.write(f"   🎯 检测目标: {result['object_count']} 个\n")
                f.write(f"   ⏱️ 推理耗时: {result['inference_time']:.3f} 秒\n")

                if result['results'] and result['results'][0].boxes and len(result['results'][0].boxes) > 0:
                    confidences = result['results'][0].boxes.conf.cpu().numpy()
                    classes = result['results'][0].boxes.cls.cpu().numpy().astype(int)

                    f.write(f"   📈 置信度范围: {np.min(confidences):.3f} - {np.max(confidences):.3f}\n")

                    # 类别统计
                    class_counts = {}
                    for cls in classes:
                        class_name = result['class_names'][cls] if cls < len(result['class_names']) else f"类别{cls}"
                        class_counts[class_name] = class_counts.get(class_name, 0) + 1

                    f.write("   📊 类别分布: " + ", ".join(
                        [f"{name}:{count}" for name, count in class_counts.items()]) + "\n")

                f.write("\n")

    def clear_display_windows(self):
        """清空显示窗口"""
        self.original_label.clear()
        self.original_label.setText("等待加载源...")
        self.result_label.clear()
        self.result_label.setText("等待检测结果...")

    def display_image(self, img_array, label):
        """显示图像"""
        if img_array is None:
            return

        height, width, channel = img_array.shape
        bytes_per_line = 3 * width
        q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
    def clear_display(self,lable):
        pass

    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

        # 限制日志行数
        max_lines = 1000
        lines = self.log_text.toPlainText().split('\n')
        if len(lines) > max_lines:
            keep_lines = lines[-500:]
            self.log_text.setPlainText('\n'.join(keep_lines))

        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        """清除日志"""
        self.log_text.clear()
        self.log_message("🗑️ 日志已清除")

    def create_enhanced_icon(self, size=64):
        """创建增强的应用图标"""
        icon = QIcon()

        for s in [16, 32, 48, 64, 128, 256]:
            pixmap = QPixmap(s, s)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # 渐变背景
            gradient = QRadialGradient(s / 2, s / 2, s / 2)
            gradient.setColorAt(0, QColor("#3498db"))
            gradient.setColorAt(1, QColor("#2c3e50"))

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, s, s)

            # 十字准星
            painter.setPen(QPen(QColor("white"), max(1, s // 32), Qt.SolidLine))
            center = s / 2
            arm_len = s * 0.25

            painter.drawLine(center - arm_len, center, center + arm_len, center)
            painter.drawLine(center, center - arm_len, center, center + arm_len)

            # 中心圆点
            painter.setBrush(QBrush(QColor("white")))
            r = max(2, s // 16)
            painter.drawEllipse(center - r, center - r, 2 * r, 2 * r)

            # AI 眼睛效果
            painter.setPen(QPen(QColor("#e74c3c"), max(1, s // 64), Qt.SolidLine))
            painter.setBrush(Qt.NoBrush)

            # 外圈
            outer_r = s * 0.35
            painter.drawEllipse(center - outer_r, center - outer_r, 2 * outer_r, 2 * outer_r)

            painter.end()
            icon.addPixmap(pixmap)

        return icon


class DetectionVideoRecorder:
    """检测视频录制器，用于记录实时检测的快照"""
    
    def __init__(self, source_name, output_dir, fps=20):
        self.source_name = source_name
        self.output_dir = output_dir
        self.fps = fps
        self.is_recording = False
        self.video_writer = None
        self.frames = []
        self.detection_stats = {}
        self.total_detections = 0
        self.start_time = None
        self.end_time = None
        self.max_frames_per_file = fps * 60*60*24  # 24小时的视频
        
    def start_recording(self):
        """开始录制"""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.start_time = time.time()
        self.frames.clear()
        self.detection_stats.clear()
        self.total_detections = 0
        
        # 生成文件名
        timestamp = int(self.start_time)
        self.filename_base = f"{self.source_name}_{timestamp}"
        self.mp4_path = self.output_dir / f"{self.filename_base}.mp4"
        self.json_path = self.output_dir / f"{self.filename_base}.json"
        
        # 初始化视频写入器（稍后在添加第一帧时设置）
        self.video_writer = None
    
    def add_frame(self, frame, detection_info):
        """添加帧"""
        if not self.is_recording:
            return
        # 检查是否有检测结果
        if not detection_info or not detection_info.get('results'):
            return

        results = detection_info['results']
        if not hasattr(results[0], 'boxes') or not results[0].boxes or len(results[0].boxes) == 0:
            return
        # 如果是第一帧，初始化视频写入器
        if self.video_writer is None:
            height, width = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(str(self.mp4_path), fourcc, self.fps, (width, height))
        
        # 写入帧 - 解决色差问题：将RGB转换为BGR
        if frame.shape[2] == 3:  # 确保是3通道彩色图像
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.video_writer.write(bgr_frame)
        else:
            self.video_writer.write(frame)
            
        self.frames.append(frame.copy())
        
        # 更新检测统计
        if detection_info and detection_info.get('results'):
            results = detection_info['results']
            if hasattr(results[0], 'boxes') and results[0].boxes and len(results[0].boxes) > 0:
                self.total_detections += len(results[0].boxes)
                
                # 统计类别
                if hasattr(results[0].boxes, 'cls'):
                    classes = results[0].boxes.cls.cpu().numpy().astype(int)
                    class_names = detection_info.get('class_names', [])
                    
                    for cls in classes:
                        if cls < len(class_names):
                            class_name = class_names[cls]
                            self.detection_stats[class_name] = self.detection_stats.get(class_name, 0) + 1
        
        # 检查是否需要保存文件
        if len(self.frames) >= self.max_frames_per_file:
            self.save_recording()
            self.start_recording()  # 开始新的录制
    
    def stop_recording(self):
        """停止录制"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.end_time = time.time()
        
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        # 保存录制
        if self.frames:
            self.save_recording()
    
    def save_recording(self):
        """保存录制"""
        if not self.frames or not self.start_time:
            return
        
        # 确保视频写入器已释放
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        # 保存JSON元数据
        metadata = {
            'camera_id': self.source_name,
            'source_name': self.source_name,
            'start_time': self.start_time,
            'end_time': self.end_time or time.time(),
            'fps': self.fps,
            'total_detections': self.total_detections,
            'detection_stats': self.detection_stats,
            'frame_count': len(self.frames),
            'mp4_filename': self.mp4_path.name,
            'json_filename': self.json_path.name
        }
        
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"保存检测快照: {self.source_name} - {len(self.frames)} 帧, {self.total_detections} 次检测")
        print(f"文件路径: {self.mp4_path}")
        print(f"JSON路径: {self.json_path}")


def main():
    app = QApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName("Enhanced Object Detection System")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("AI Vision Lab")

    # 设置高DPI缩放
    # app.setAttribute(Qt.AA_EnableHighDpiScaling)
    # app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # 创建主窗口
    window = EnhancedDetectionUI()
    window.show()

    # 启动消息
    window.log_message("🚀 医院摔倒实时检测系统 已启动")
    window.log_message("✨ 新功能: 渐变UI、多摄像头支持、实时监控、增强日志等")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()