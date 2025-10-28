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

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Components - 增强组件模块
包含批量检测、结果显示、监控等组件
"""
import sys
import threading

import cv2
import time
import numpy as np
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ultralytics import YOLO

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Universal Object Detection System v2.0
优化的通用目标检测系统 - 主程序

新功能特性:
✨ 渐变UI样式效果
📱 优化的响应式布局
📊 增强的日志显示（类别识别信息）
📁 支持自定义模型目录加载
📹 多摄像头支持和选择
🖥️ 实时监控页面
🎨 优化的图标设计
⚡ 性能优化和错误处理
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

try:
    from ultralytics import YOLO
except ImportError:
    print("错误: 请安装ultralytics库: pip install ultralytics")
    sys.exit(1)


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
            #startBtn {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #10B981, stop:1 #059669);
            color: white;
            border: none;
            border-radius: 3px;  /* 减小圆角 */
            min-width: 10px;  /* 减小最小宽度 */
            min-height: 10px;  /* 添加最小高度 */
            font-size: 8px;  /* 减小字体大小 */
        }
        #startBtn:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #059669, stop:1 #047857);
        }

        #pauseBtn {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #F59E0B, stop:1 #D97706);
            color: white;
            border: none;
            border-radius: 3px;  /* 减小圆角 */
            min-width: 10px;  /* 减小最小宽度 */
            min-height: 10px;  /* 添加最小高度 */
            font-size: 8px;  /* 减小字体大小 */
        }
        #pauseBtn:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #D97706, stop:1 #B45309);
        }

        #stopBtn {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #EF4444, stop:1 #DC2626);
            color: white;
            border: none;
            border-radius: 3px;  /* 减小圆角 */
            min-width: 10px;  /* 减小最小宽度 */
            min-height: 10px;  /* 添加最小高度 */
            font-size: 8px;  /* 减小字体大小 */
        }
        #stopBtn:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #DC2626, stop:1 #B91C1C);
        }

        #monitorBtn {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #3B82F6, stop:1 #2563EB);
            color: white;
            border: none;
            border-radius: 3px;  /* 减小圆角 */
            min-width: 10px;  /* 减小最小宽度 */
            min-height: 10px;  /* 添加最小高度 */
            font-size: 8px;  /* 减小字体大小 */
        }
        #monitorBtn:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #2563EB, stop:1 #1D4ED8);
        }

        #clearBtn {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #94A3B8, stop:1 #64748B);
            color: white;
            border: none;
            border-radius: 3px;  /* 减小圆角 */
            min-width: 10px;  /* 减小最小宽度 */
            min-height: 10px;  /* 添加最小高度 */
            font-size: 8px;  /* 减小字体大小 */
        }
        #clearBtn:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #64748B, stop:1 #475569);
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
            font-size: 14px;
            border-radius: 10px;
            padding: 15px;
        """

    @staticmethod
    def get_video_label_style():
        return """
            border: 1px solid rgba(52, 152, 219, 0.3);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(248, 249, 250, 0.9), stop:1 rgba(233, 236, 239, 0.9));
            color: #7f8c8d;
            font-weight: bold;
            font-size: 14px;
            border-radius: 10px;
        """


class CameraManager:
    """摄像头管理器 - 处理多摄像头检测和管理"""

    def __init__(self):
        self.cameras = []
        self.scan_cameras()

    def scan_cameras(self):
        """扫描可用摄像头"""
        self.cameras = []

        # 检测摄像头（检测前8个索引）
        for i in range(8):  # 扩展到8个摄像头检测
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    # 获取摄像头信息
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)

                    camera_info = {
                        'id': i,
                        'name': f"摄像头 {i}",
                        'resolution': f"{width}x{height}",
                        'fps': fps if fps > 0 else 30,
                        'available': True,
                        'cap': None  # 保留摄像头对象位置
                    }
                    self.cameras.append(camera_info)
                cap.release()

        # 如果没有摄像头，添加虚拟摄像头用于测试
        if not self.cameras:
            self.cameras.append({
                'id': -1,
                'name': "虚拟摄像头",
                'resolution': "640x480",
                'fps': 30,
                'available': False,
                'cap': None
            })

    def get_camera_count(self):
        """返回可用摄像头数量

        Returns:
            int: 可用摄像头数量
        """
        return len(self.get_available_cameras())

    def get_available_cameras(self):
        """获取可用摄像头列表

        Returns:
            list: 可用摄像头信息字典列表
        """
        return [cam for cam in self.cameras if cam['available']]

    def get_camera_info(self, camera_id):
        """获取指定摄像头的详细信息

        Args:
            camera_id (int): 摄像头ID

        Returns:
            dict: 摄像头信息字典，包含以下键：
                - id: 摄像头索引
                - name: 摄像头名称
                - resolution: 分辨率字符串(如"640x480")
                - fps: 帧率
                - available: 是否可用
        """
        for cam in self.cameras:
            if cam['id'] == camera_id:
                return cam
        return None

    def get_camera_names(self):
        """获取所有摄像头名称列表

        Returns:
            list: 摄像头名称字符串列表
        """
        return [cam['name'] for cam in self.cameras]

    def release_all(self):
        """释放所有摄像头资源"""
        for cam in self.cameras:
            if cam['cap'] is not None:
                cam['cap'].release()
                cam['cap'] = None


class ModelManager:
    """模型管理器 - 处理模型扫描和加载"""

    def __init__(self):
        self.models_paths = [
            Path("pt_models"),
            Path("../models"),
            Path("weights"),
        ]
        self.current_model = None
        self.class_names = []

    def scan_models(self, custom_path=None):
        """扫描模型文件"""
        models = []
        search_paths = self.models_paths.copy()

        if custom_path and Path(custom_path).exists():
            search_paths.insert(0, Path(custom_path))

        for model_dir in search_paths:
            if model_dir.exists():
                try:
                    pt_files = sorted(model_dir.glob("*.pt"))
                    for pt_file in pt_files:
                        models.append({
                            'name': pt_file.name,
                            'path': str(pt_file),
                            'size': self._get_file_size(pt_file),
                            'modified': self._get_modification_time(pt_file)
                        })
                except Exception as e:
                    print(f"扫描目录 {model_dir} 时出错: {e}")

        return models

    def load_model(self, model_path):
        """加载模型"""
        try:
            self.current_model = YOLO(model_path)
            self.class_names = list(self.current_model.names.values())
            return True
        except Exception as e:
            print(f"模型加载失败: {e}")
            return False

    def get_class_names(self):
        """获取类别名称"""
        return self.class_names

    def _get_file_size(self, file_path):
        """获取文件大小"""
        try:
            size = file_path.stat().st_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"

    def _get_modification_time(self, file_path):
        """获取修改时间"""
        try:
            timestamp = file_path.stat().st_mtime
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
        except:
            return "Unknown"

class DetectionThread(QThread):
    """增强的检测线程"""
    result_ready = Signal(object, object, float, object, list)  # 原图, 结果图, 耗时, 检测结果, 类别名称
    progress_updated = Signal(int)
    status_changed = Signal(str)
    error_occurred = Signal(str)
    fps_updated = Signal(float)
    finished = Signal()

    def __init__(self, model, source_type, source_path=None, camera_id=0, confidence_threshold=0.25):
        super().__init__()
        self.model = model
        self.source_type = source_type
        self.source_path = source_path
        self.camera_id = camera_id
        self.confidence_threshold = confidence_threshold
        self.is_running = False
        self.is_paused = False
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()

    def run(self):
        self.is_running = True
        try:
            if self.source_type == 'image':
                self._process_image()
            elif self.source_type == 'video':
                self._process_video()
            elif self.source_type == 'camera':
                self._process_camera()
        except Exception as e:
            self.error_occurred.emit(f"检测过程发生错误: {str(e)}")
        finally:
            self.is_running = False
            self.finished.emit()

    def _process_image(self):
        """处理单张图片"""
        if not self.source_path or not Path(self.source_path).exists():
            self.error_occurred.emit("图片文件不存在")
            return

        self.status_changed.emit("正在处理图片...")

        start_time = time.time()
        results = self.model(self.source_path, conf=self.confidence_threshold, verbose=False)
        end_time = time.time()

        original_img = cv2.imread(self.source_path)
        if original_img is None:
            self.error_occurred.emit("无法读取图片文件")
            return

        original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        result_img = results[0].plot()
        result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
        class_names = list(self.model.names.values())

        self.result_ready.emit(original_img, result_img, end_time - start_time, results, class_names)
        self.progress_updated.emit(100)

    def _process_video(self):
        """处理视频文件"""
        if not self.source_path or not Path(self.source_path).exists():
            self.error_occurred.emit("视频文件不存在")
            return

        cap = cv2.VideoCapture(self.source_path)
        if not cap.isOpened():
            self.error_occurred.emit("无法打开视频文件")
            return

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0
        class_names = list(self.model.names.values())

        self.status_changed.emit(f"开始处理视频 (共{total_frames}帧)...")

        while cap.isOpened() and self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret:
                break

            start_time = time.time()
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            end_time = time.time()

            original_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result_img = results[0].plot()
            result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)

            self.result_ready.emit(original_img, result_img, end_time - start_time, results, class_names)

            frame_count += 1
            if total_frames > 0:
                progress = int((frame_count / total_frames) * 100)
                self.progress_updated.emit(progress)

            # 更新FPS
            self._update_fps()

            # 状态更新（每30帧更新一次）
            if frame_count % 30 == 0:
                current_fps = self._get_current_fps()
                self.status_changed.emit(f"处理中... {frame_count}/{total_frames} 帧 (FPS: {current_fps:.1f})")

            time.sleep(0.033)  # 约30fps

        cap.release()

    def _process_camera(self):
        """处理摄像头"""
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            self.error_occurred.emit(f"无法打开摄像头 {self.camera_id}")
            return

        # 设置摄像头参数
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        class_names = list(self.model.names.values())
        self.status_changed.emit(f"摄像头 {self.camera_id} 已启动...")

        while cap.isOpened() and self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret:
                break

            start_time = time.time()
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            end_time = time.time()

            original_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result_img = results[0].plot()
            result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)

            self.result_ready.emit(original_img, result_img, end_time - start_time, results, class_names)

            # 更新FPS
            self._update_fps()

            # 状态更新（每60帧更新一次）
            if self.frame_count % 60 == 0:
                current_fps = self._get_current_fps()
                self.status_changed.emit(f"摄像头运行中 (FPS: {current_fps:.1f})")

            time.sleep(0.033)  # 约30fps

        cap.release()

    def _update_fps(self):
        """更新FPS计算"""
        self.frame_count += 1
        self.fps_counter += 1

        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            fps = self.fps_counter / (current_time - self.last_fps_time)
            self.fps_updated.emit(fps)
            self.fps_counter = 0
            self.last_fps_time = current_time

    def _get_current_fps(self):
        """获取当前FPS"""
        current_time = time.time()
        if current_time - self.last_fps_time > 0:
            return self.fps_counter / (current_time - self.last_fps_time)
        return 0

    def pause(self):
        self.is_paused = True
        self.status_changed.emit(f"暂停中...")

    def resume(self):
        self.is_paused = False
        self.status_changed.emit(f"恢复检测")


    def stop(self):
        self.is_running = False
        self.status_changed.emit(f"检测结束!")

class BatchDetectionThread(QThread):
    """批量检测线程"""
    result_ready = Signal(str, object, object, float, object, list)  # 文件路径, 原图, 结果图, 耗时, 检测结果, 类别名称
    progress_updated = Signal(int)
    current_file_changed = Signal(str)
    status_changed = Signal(str)
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(self, model, folder_path, confidence_threshold=0.25, supported_formats=None):
        super().__init__()
        self.model = model
        self.folder_path = folder_path
        self.confidence_threshold = confidence_threshold
        self.supported_formats = supported_formats or ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.tif']
        self.is_running = False
        self.processed_count = 0
        self.error_count = 0

    def run(self):
        self.is_running = True

        try:
            # 收集所有支持的图片文件
            image_files = []
            for fmt in self.supported_formats:
                image_files.extend(Path(self.folder_path).rglob(f'*{fmt}'))
                # image_files.extend(Path(self.folder_path).rglob(f'*{fmt.upper()}'))

            total_files = len(image_files)
            if total_files == 0:
                self.status_changed.emit("文件夹中没有找到支持的图片格式")
                self.finished.emit()
                return

            self.status_changed.emit(f"开始批量处理 {total_files} 个文件...")

            # 获取类别名称
            class_names = list(self.model.names.values())

            for i, img_path in enumerate(image_files):
                if not self.is_running:
                    break

                self.current_file_changed.emit(str(img_path))

                try:
                    # 处理单个图片
                    start_time = time.time()
                    results = self.model(str(img_path), conf=self.confidence_threshold, verbose=False)
                    end_time = time.time()

                    # 获取原图
                    original_img = cv2.imread(str(img_path))
                    if original_img is not None:
                        original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)

                        # 获取结果图
                        result_img = results[0].plot()
                        result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)

                        self.result_ready.emit(str(img_path), original_img, result_img,
                                               end_time - start_time, results, class_names)
                        self.processed_count += 1

                except Exception as e:
                    self.error_occurred.emit(f"处理文件 {img_path.name} 时发生错误: {str(e)}")
                    self.error_count += 1

                # 更新进度
                progress = int(((i + 1) / total_files) * 100)
                self.progress_updated.emit(progress)

                # 状态更新
                if (i + 1) % 10 == 0 or i == total_files - 1:
                    self.status_changed.emit(
                        f"处理进度: {i + 1}/{total_files} (成功: {self.processed_count}, 错误: {self.error_count})")

        except Exception as e:
            self.error_occurred.emit(f"批量处理发生错误: {str(e)}")
        finally:
            self.is_running = False
            # self.finished.emit()

    def stop(self):
        """停止批量检测"""
        self.is_running = False


class MultiCameraMonitorThread(QThread):
    camera_result_ready = Signal(int, object, object, float, object, list)
    camera_error = Signal(int, str)
    camera_status = Signal(int, str)
    finished = Signal()

    def __init__(self, model, camera_ids, conf=0.25, fps=10):
        super().__init__()
        self.model = model
        self.cam_ids = camera_ids
        self.conf = conf
        self.period = 1.0 / fps  # 帧间隔
        self.caps = {}  # {id: cv2.VideoCapture}
        self.active = {}  # {id: bool} 是否在线
        self.last_t = {}  # {id: float}

        # 线程同步
        self._run_flag = True
        self._pause_cond = QWaitCondition()
        self._pause_mutex = QMutex()
        self._paused_flag = False

    # ----------------- 生命周期 -----------------
    def run(self):
        self._open_all()
        if not self.caps:
            self.finished.emit()
            return

        cls_names = list(self.model.names.values())

        while self._run_flag:
            self._pause_mutex.lock()
            if self._paused_flag:
                self._pause_cond.wait(self._pause_mutex)
            self._pause_mutex.unlock()

            for cid in list(self.caps.keys()):
                if not self._run_flag:
                    break
                if not self._grab_and_infer(cid, cls_names):
                    self._reconnect_later(cid)  # 断线后异步重连
            self.msleep(10)

        self._close_all()
        self.finished.emit()

    def stop(self):
        self._run_flag = False
        self.resume()  # 确保等待线程被唤醒
        self.wait()

    def pause(self):
        self._pause_mutex.lock()
        self._paused_flag = True
        self._pause_mutex.unlock()

    def resume(self):
        self._pause_mutex.lock()
        self._paused_flag = False
        self._pause_mutex.unlock()
        self._pause_cond.wakeAll()

    # ----------------- 私有工具 -----------------
    def _open_all(self):
        for cid in self.cam_ids:
            cap = cv2.VideoCapture(cid, cv2.CAP_DSHOW)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                self.caps[cid] = cap
                self.active[cid] = True
                self.last_t[cid] = 0.0
                self.camera_status.emit(cid, "已连接")
            else:
                self.camera_error.emit(cid, "无法打开")
                cap.release()

    def _close_all(self):
        for cap in self.caps.values():
            cap.release()
        self.caps.clear()

    def _grab_and_infer(self, cid, cls_names):
        cap = self.caps.get(cid)
        if not cap or not cap.isOpened():
            return False

        # 读帧非阻塞：先 grab 再 retrieve
        if not cap.grab():
            return False

        now = time.time()
        if now - self.last_t[cid] < self.period:
            return True  # 未超时，但帧已 grab，避免堆积
        self.last_t[cid] = now

        ret, frame = cap.retrieve()
        if not ret:
            return False

        try:
            t0 = time.time()
            results = self.model(frame, conf=self.conf, verbose=False)
            infer_ms = (time.time() - t0) * 1000
            out_img = results[0].plot()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_out = cv2.cvtColor(out_img, cv2.COLOR_BGR2RGB)
            self.camera_result_ready.emit(cid, rgb_frame, rgb_out,
                                          infer_ms / 1000.0, results, cls_names)
            return True
        except Exception as e:
            self.camera_error.emit(cid, f"推理异常: {e}")
            return False

    def _reconnect_later(self, cid):
        # 简单策略：5 秒后重试
        if self.active.get(cid) is False:
            return
        self.active[cid] = False
        self.camera_status.emit(cid, "重连中…")
        threading.Timer(5.0, lambda: self._try_reopen(cid)).start()

    def _try_reopen(self, cid):
        if cid in self.caps:
            self.caps[cid].release()
        cap = cv2.VideoCapture(cid)
        if cap.isOpened():
            self.caps[cid] = cap
            self.active[cid] = True
            self.camera_status.emit(cid, "已重连")
        else:
            cap.release()
            self._reconnect_later(cid)


class ModelSelectionDialog(QDialog):
    """模型选择对话框"""

    def __init__(self, model_manager, parent=None):
        super().__init__(parent)
        self.model_manager = model_manager
        self.selected_model = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🔧 高级模型选择")
        self.setModal(True)
        self.resize(700, 450)

        layout = QVBoxLayout(self)

        # 自定义路径
        path_group = QGroupBox("📁 自定义模型路径")
        path_layout = QHBoxLayout(path_group)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("输入自定义模型目录路径...")
        path_layout.addWidget(self.path_edit)

        browse_btn = QPushButton("📂 浏览")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_btn)

        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.refresh_models)
        path_layout.addWidget(refresh_btn)

        layout.addWidget(path_group)

        # 模型列表
        models_group = QGroupBox("📋 可用模型")
        models_layout = QVBoxLayout(models_group)

        self.model_table = QTableWidget()
        self.model_table.setColumnCount(4)
        self.model_table.setHorizontalHeaderLabels(["模型名称", "大小", "修改时间", "路径"])
        self.model_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.model_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.model_table.setAlternatingRowColors(True)
        self.model_table.doubleClicked.connect(self.accept)

        models_layout.addWidget(self.model_table)
        layout.addWidget(models_group)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)

        self.refresh_models()

    def browse_path(self):
        """浏览自定义路径"""
        path = QFileDialog.getExistingDirectory(self, "选择模型目录")
        if path:
            self.path_edit.setText(path)
            self.refresh_models()

    def refresh_models(self):
        """刷新模型列表"""
        custom_path = self.path_edit.text() if self.path_edit.text() else None
        models = self.model_manager.scan_models(custom_path)

        self.model_table.setRowCount(len(models))

        for i, model in enumerate(models):
            self.model_table.setItem(i, 0, QTableWidgetItem(model['name']))
            self.model_table.setItem(i, 1, QTableWidgetItem(model['size']))
            self.model_table.setItem(i, 2, QTableWidgetItem(model['modified']))
            self.model_table.setItem(i, 3, QTableWidgetItem(model['path']))

    def accept(self):
        """确认选择"""
        current_row = self.model_table.currentRow()
        if current_row >= 0:
            self.selected_model = self.model_table.item(current_row, 3).text()
        super().accept()


class DetectionResultWidget(QWidget):
    """检测结果显示组件"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("🎯 检测结果详情表")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        # title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["序号", "类别", "置信度", "坐标 (x,y)", "尺寸 (w×h)"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                font-size: 10pt;
                font-weight: bold;
                height: 12px;     /* 在 QSS 里 height 对表头 section 生效 */
            }
        """)
        self.result_table.setMaximumHeight(200)
        self.result_table.setAlternatingRowColors(True)

        layout.addWidget(self.result_table)

        # 统计信息
        self.stats_label = QLabel("等待检测结果...")
        self.stats_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(236, 240, 241, 0.9), stop:1 rgba(189, 195, 199, 0.9));
            padding: 12px;
            border-radius: 8px;
            font-size: 12px;
            color: #2c3e50;
            font-weight: bold;
        """)
        layout.addWidget(self.stats_label)

    def update_results(self, results, class_names, inference_time):
        """更新检测结果"""
        if not results or not results[0].boxes or len(results[0].boxes) == 0:
            self.result_table.setRowCount(0)
            self.stats_label.setText("❌ 未检测到目标")
            return

        boxes = results[0].boxes
        confidences = boxes.conf.cpu().numpy()
        classes = boxes.cls.cpu().numpy().astype(int)
        xyxy = boxes.xyxy.cpu().numpy()

        # 更新表格
        self.result_table.setRowCount(len(confidences))

        class_counts = {}
        for i, (conf, cls, box) in enumerate(zip(confidences, classes, xyxy)):
            class_name = class_names[cls] if cls < len(class_names) else f"类别{cls}"

            # 统计类别数量
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

            self.result_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.result_table.setItem(i, 1, QTableWidgetItem(class_name))

            # 置信度带颜色
            conf_item = QTableWidgetItem(f"{conf:.3f}")
            if conf > 0.8:
                conf_item.setBackground(QColor(46, 204, 113, 100))  # 绿色
            elif conf > 0.5:
                conf_item.setBackground(QColor(241, 196, 15, 100))  # 黄色
            else:
                conf_item.setBackground(QColor(231, 76, 60, 100))  # 红色
            self.result_table.setItem(i, 2, conf_item)

            self.result_table.setItem(i, 3, QTableWidgetItem(f"({box[0]:.0f},{box[1]:.0f})"))
            self.result_table.setItem(i, 4, QTableWidgetItem(f"{box[2] - box[0]:.0f}×{box[3] - box[1]:.0f}"))

        # 更新统计信息
        total_objects = len(confidences)
        avg_confidence = np.mean(confidences)

        stats_text = f"✅ 检测到 {total_objects} 个目标 | "
        stats_text += f"🎯 平均置信度: {avg_confidence:.3f} | "
        stats_text += f"⏱️ 耗时: {inference_time:.3f}秒\n"
        stats_text += "📊 类别统计: " + " | ".join([f"{name}: {count}" for name, count in class_counts.items()])

        self.stats_label.setText(stats_text)


class MonitoringWidget(QWidget):
    """监控页面组件"""

    def __init__(self, model_manager, camera_manager):
        super().__init__()
        self.model_manager = model_manager
        self.camera_manager = camera_manager
        self.monitoring_thread = None
        self.camera_labels = {}
        self.current_model = None
        self.start_monitor_btn = QPushButton("🚀 开始监控")

        # 自动保存监控快照相关属性
        self.is_auto_saving = False
        self.camera_recorders = {}  # {camera_id: VideoRecorder}
        self.monitor_history_dir = Path("monitor_history")
        self.monitor_history_dir.mkdir(exist_ok=True)
        self.current_memory_usage = 0  # MB
        self.max_memory_limit = 500  # MB

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 控制面板
        control_group = QGroupBox("🖥️ 监控控制")
        control_group.setMaximumHeight(120)  # 增加高度以容纳新控件
        control_layout = QVBoxLayout(control_group)

        # 第一行：模型和摄像头选择
        first_row_layout = QHBoxLayout()

        # 模型选择
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型:"))
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        self.init_model_combo()
        model_layout.addWidget(self.model_combo)
        select_model_btn = QPushButton("🔧 选择模型")
        select_model_btn.clicked.connect(self.select_model)
        model_layout.addWidget(select_model_btn)
        first_row_layout.addLayout(model_layout)

        # 摄像头选择
        camera_layout = QHBoxLayout()
        camera_layout.addWidget(QLabel("摄像头:"))
        self.camera_list = QListWidget()
        self.camera_list.setMaximumWidth(300)
        self.camera_list.setSelectionMode(QListWidget.MultiSelection)
        self.refresh_cameras()
        camera_layout.addWidget(self.camera_list)
        refresh_camera_btn = QPushButton("🔄 刷新")
        refresh_camera_btn.clicked.connect(self.refresh_cameras)
        camera_layout.addWidget(refresh_camera_btn)
        first_row_layout.addLayout(camera_layout)

        control_layout.addLayout(first_row_layout)

        # 第二行：监控控制和自动保存设置
        second_row_layout = QHBoxLayout()

        # 监控控制按钮
        monitor_btn_layout = QHBoxLayout()
        self.start_monitor_btn.clicked.connect(self.start_monitoring)
        self.start_monitor_btn.setEnabled(True)
        monitor_btn_layout.addWidget(self.start_monitor_btn)

        self.stop_monitor_btn = QPushButton("⏸️ 暂停")
        self.stop_monitor_btn.clicked.connect(self.stop_monitoring)
        monitor_btn_layout.addWidget(self.stop_monitor_btn)

        self.clear_monitor_btn = QPushButton("🗑️ 清除监控")
        self.clear_monitor_btn.clicked.connect(self.clear_monitoring)
        self.clear_monitor_btn.setEnabled(False)
        self.stop_monitor_btn.setEnabled(False)
        monitor_btn_layout.addWidget(self.clear_monitor_btn)

        second_row_layout.addLayout(monitor_btn_layout)

        # 自动保存监控快照控制
        snapshot_control_layout = QHBoxLayout()

        self.auto_save_btn = QPushButton("🎬 自动保存监控快照")
        self.auto_save_btn.clicked.connect(self.toggle_auto_save)
        self.auto_save_btn.setEnabled(False)
        snapshot_control_layout.addWidget(self.auto_save_btn)

        # 录制设置
        snapshot_control_layout.addWidget(QLabel("帧率:"))
        self.recording_fps_spinbox = QSpinBox()
        self.recording_fps_spinbox.setRange(5, 60)
        self.recording_fps_spinbox.setValue(20)
        self.recording_fps_spinbox.setSuffix(" fps")
        snapshot_control_layout.addWidget(self.recording_fps_spinbox)

        snapshot_control_layout.addWidget(QLabel("内存限制:"))
        self.memory_limit_spinbox = QSpinBox()
        self.memory_limit_spinbox.setRange(100, 2000)
        self.memory_limit_spinbox.setValue(500)
        self.memory_limit_spinbox.setSuffix(" MB")
        snapshot_control_layout.addWidget(self.memory_limit_spinbox)

        second_row_layout.addLayout(snapshot_control_layout)

        control_layout.addLayout(second_row_layout)

        layout.addWidget(control_group)

        # 监控显示区域
        self.monitor_scroll = QScrollArea()
        self.monitor_scroll.setStyleSheet("""
            QScrollArea {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(236, 240, 241, 0.9),
                    stop:1 rgba(189, 195, 199, 0.9));
                border-radius: 8px;
            }
            QScrollArea > QWidget > QWidget {   /* viewport */
                background: transparent;
            }
            QScrollArea::corner {               /* 右下角空白三角 */
                background: transparent;
            }
        """)
        self.monitor_widget = QWidget()
        self.monitor_layout = QGridLayout(self.monitor_widget)
        self.monitor_scroll.setWidget(self.monitor_widget)
        self.monitor_scroll.setWidgetResizable(True)

        layout.addWidget(self.monitor_scroll)

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
            self.try_load_default_model()

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

    def on_model_changed(self, model_text):
        """模型选择改变"""
        if model_text != "无可用模型":
            self.load_model_by_name(model_text)

    def load_model(self, model_path):

        """加载模型"""
        try:
            self.current_model = YOLO(model_path)
            self.start_monitor_btn.setEnabled(True)
            return True
        except Exception as e:
            pass

            return False

    def select_model(self):
        """选择模型"""
        dialog = ModelSelectionDialog(self.model_manager, self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_model:
            try:
                self.current_model = YOLO(dialog.selected_model)
                model_name = Path(dialog.selected_model).name
                self.model_combo.clear()
                self.model_combo.addItem(model_name)
                self.start_monitor_btn.setEnabled(True)
                QMessageBox.information(self, "成功", f"模型加载成功: {model_name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"模型加载失败: {str(e)}")

    def refresh_cameras(self):
        """刷新摄像头列表"""
        self.camera_manager.scan_cameras()
        self.camera_list.clear()

        for camera in self.camera_manager.get_available_cameras():
            item = QListWidgetItem(f"📹 {camera['name']} ({camera['resolution']})")
            item.setData(Qt.UserRole, camera['id'])
            self.camera_list.addItem(item)

    def start_monitoring(self):
        """开始监控"""
        if not self.current_model:
            QMessageBox.warning(self, "警告", "请先选择模型")
            return

        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请选择至少一个摄像头")
            return

        camera_ids = [item.data(Qt.UserRole) for item in selected_items]

        # 清空之前的显示
        self.clear_monitor_display()
        self.clear_monitor_btn.setEnabled(True)

        # 创建显示标签
        self.create_camera_labels(camera_ids)
        # 设置等高宽
        self.set_equal_column_stretch()
        # 启动监控线程
        self.monitoring_thread = MultiCameraMonitorThread(self.current_model, camera_ids)
        self.monitoring_thread.camera_result_ready.connect(self.update_camera_display)
        self.monitoring_thread.camera_error.connect(self.handle_camera_error)
        self.monitoring_thread.finished.connect(self.on_monitoring_finished)

        self.monitoring_thread.start()

        self.start_monitor_btn.setEnabled(False)
        self.stop_monitor_btn.setEnabled(True)
        self.auto_save_btn.setEnabled(True)  # 启用自动保存按钮

    def stop_monitoring(self):
        """暂停/继续监控"""
        if self.monitoring_thread and self.monitoring_thread._run_flag:
            if self.monitoring_thread._paused_flag:  # 监测是否已暂停
                self.monitoring_thread.resume()  # 恢复
                self.stop_monitor_btn.setText("⏸️ 暂停")  # 按钮文字：暂停
            else:
                self.monitoring_thread.pause()  # 暂停
                self.stop_monitor_btn.setText("▶️ 继续")  # 按钮文字：继续

    def clear_monitoring(self):
        """停止监控"""
        self.monitoring_thread.stop()
        self.clear_monitor_display()

        # 停止自动保存
        if self.is_auto_saving:
            self.stop_auto_save()

        # 重置按钮状态
        self.start_monitor_btn.setEnabled(True)
        self.stop_monitor_btn.setEnabled(False)
        self.clear_monitor_btn.setEnabled(False)
        self.auto_save_btn.setEnabled(False)

    def create_camera_labels(self, camera_ids):
        """创建摄像头显示标签"""
        self.camera_labels = {}

        cols = 2  # 每行2个摄像头
        for i, camera_id in enumerate(camera_ids):
            row = i // cols
            col = i % cols

            # 创建摄像头组
            camera_group = QGroupBox(f"📹 摄像头 {camera_id}")
            camera_group.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(248, 249, 250, 0.9), stop:1 rgba(233, 236, 239, 0.9));
                color: #7f8c8d;
                font-weight: bold;
                font-size: 14px;
                border-radius: 10px;

            """)
            # camera_group.setMaximumHeight(350)
            camera_layout = QVBoxLayout(camera_group)
            self.start_btn = QPushButton("▶️")
            self.start_btn.setObjectName("startBtn")
            self.start_btn.setToolTip("启动检测")
            # self.start_btn.clicked.connect(self.start_detection)

            self.pause_btn = QPushButton("⏸️")
            self.pause_btn.setObjectName("pauseBtn")
            self.pause_btn.setToolTip("暂停检测")
            # self.pause_btn.clicked.connect(self.pause_detection)

            self.stop_btn = QPushButton("⏹️")
            self.stop_btn.setObjectName("stopBtn")
            self.stop_btn.setToolTip("停止检测")
            # self.stop_btn.clicked.connect(self.stop_detection)

            self.monitor_btn = QPushButton("👁️")
            self.monitor_btn.setObjectName("monitorBtn")
            self.monitor_btn.setToolTip("监控模式")
            # self.monitor_btn.clicked.connect(self.toggle_monitor_mode)

            self.clear_btn = QPushButton("🗑️")
            self.clear_btn.setObjectName("clearBtn")
            self.clear_btn.setToolTip("清空画面")
            # self.clear_btn.clicked.connect(self.clear_frame)

            # 状态标签
            status_label = QLabel("状态: 初始化中...")
            status_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")

            control_layout = QHBoxLayout()
            control_layout.addWidget(self.start_btn)
            control_layout.addWidget(self.pause_btn)
            control_layout.addWidget(self.stop_btn)
            control_layout.addWidget(self.monitor_btn)
            control_layout.addWidget(self.clear_btn)
            control_layout.addStretch()
            control_layout.addWidget(status_label)

            # 图像显示标签
            image_label = QLabel("等待连接...")
            image_label.setMinimumSize(300, 240)
            # image_label.setMaximumHeight(350)
            image_label.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(248, 249, 250, 0.9), stop:1 rgba(233, 236, 239, 0.9));
                color: #7f8c8d;
                font-weight: bold;
                font-size: 14px;
                border-radius: 10px;

            """)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setScaledContents(True)

            camera_layout.addWidget(image_label, stretch=6)

            camera_layout.addLayout(control_layout)
            camera_layout.addStretch()

            self.camera_labels[camera_id] = {
                'image': image_label,
                'status': status_label,
                'group': camera_group
            }
            self.setStyleSheet("""
                QPushButton#startBtn {
                    max-width: 24px;
                    text-align: left;
                    padding: 5px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #f8f9fa;
                    color: #7f8c8d;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton#startBtn:hover {
                    background-color: #e9ecef;
                }
                QPushButton#startBtn:pressed {
                    background-color: #dcdcdc;
                }

                QPushButton#pauseBtn {
                    max-width: 24px;
                    text-align: left;
                    padding: 5px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #f8f9fa;
                    color: #7f8c8d;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton#pauseBtn:hover {
                    background-color: #e9ecef;
                }
                QPushButton#pauseBtn:pressed {
                    background-color: #dcdcdc;
                }

                QPushButton#stopBtn {
                    max-width: 24px;
                    text-align: left;
                    padding: 5px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #f8f9fa;
                    color: #7f8c8d;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton#stopBtn:hover {
                    background-color: #e9ecef;
                }
                QPushButton#stopBtn:pressed {
                    background-color: #dcdcdc;
                }

                QPushButton#monitorBtn {
                    max-width: 24px;
                    text-align: left;
                    padding: 5px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #f8f9fa;
                    color: #7f8c8d;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton#monitorBtn:hover {
                    background-color: #e9ecef;
                }
                QPushButton#monitorBtn:pressed {
                    background-color: #dcdcdc;
                }

                QPushButton#clearBtn {
                    max-width: 24px;
                    text-align: left;
                    padding: 5px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #f8f9fa;
                    color: #7f8c8d;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton#clearBtn:hover {
                    background-color: #e9ecef;
                }
                QPushButton#clearBtn:pressed {
                    background-color: #dcdcdc;
                }

                QLabel {
                    color: #7f8c8d;
                    font-size: 10px;
                }
            """)
            self.monitor_layout.addWidget(camera_group, row, col)

    def set_equal_column_stretch(self):
        for c in range(self.monitor_layout.columnCount()):
            self.monitor_layout.setColumnStretch(c, 1)
        for r in range(self.monitor_layout.rowCount()):
            self.monitor_layout.setRowStretch(r, 1)

    def clear_monitor_display(self):
        """清空监控显示"""
        for camera_id in list(self.camera_labels.keys()):
            self.camera_labels[camera_id]['group'].deleteLater()
        self.camera_labels.clear()

    def update_camera_display(self, camera_id, original_img, result_img, inference_time, results, class_names):
        """更新摄像头显示"""
        if camera_id not in self.camera_labels:
            return

        # 显示结果图
        self.display_image(result_img, self.camera_labels[camera_id]['image'])

        # 更新状态
        if results and results[0].boxes and len(results[0].boxes) > 0:
            object_count = len(results[0].boxes)
            self.camera_labels[camera_id]['status'].setText(
                f"状态: 检测到 {object_count} 个目标 | 耗时: {inference_time:.3f}s"
            )

            # 添加检测帧到自动保存系统
            detection_info = {
                'results': results,
                'class_names': class_names,
                'inference_time': inference_time
            }
            self.add_detection_frame(camera_id, result_img, detection_info)
        else:
            self.camera_labels[camera_id]['status'].setText(
                f"状态: 无目标 | 耗时: {inference_time:.3f}s"
            )

    def handle_camera_error(self, camera_id, error_msg):
        """处理摄像头错误"""
        if camera_id in self.camera_labels:
            self.camera_labels[camera_id]['status'].setText(f"错误: {error_msg}")
            self.camera_labels[camera_id]['status'].setStyleSheet("color: red; font-size: 10px;")

    def on_monitoring_finished(self):
        """监控结束"""
        self.start_monitor_btn.setEnabled(True)
        self.stop_monitor_btn.setEnabled(False)

        for camera_id in self.camera_labels:
            self.camera_labels[camera_id]['status'].setText("状态: 已停止")

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

    def toggle_auto_save(self):
        """切换自动保存监控快照状态"""
        if not self.is_auto_saving:
            self.start_auto_save()
        else:
            self.stop_auto_save()

    def start_auto_save(self):
        """开始自动保存监控快照"""
        if not self.current_model:
            QMessageBox.warning(self, "警告", "请先选择模型")
            return

        self.is_auto_saving = True
        self.max_memory_limit = self.memory_limit_spinbox.value()

        self.auto_save_btn.setText("⏹️ 停止自动保存")

        # 禁用设置控件
        self.recording_fps_spinbox.setEnabled(False)
        self.memory_limit_spinbox.setEnabled(False)

        QMessageBox.information(self, "成功", "自动保存监控快照已启动")

    def stop_auto_save(self):
        """停止自动保存监控快照"""
        self.is_auto_saving = False

        # 停止所有录制器
        for recorder in self.camera_recorders.values():
            recorder.stop_recording()
        self.camera_recorders.clear()

        self.auto_save_btn.setText("🎬 自动保存监控快照")
        # 启用设置控件
        self.recording_fps_spinbox.setEnabled(True)
        self.memory_limit_spinbox.setEnabled(True)

        QMessageBox.information(self, "成功", "自动保存监控快照已停止")

    def add_detection_frame(self, camera_id, frame, detection_info):
        """添加检测帧到自动保存系统"""
        if not self.is_auto_saving:
            return

        # 检查是否有检测结果
        if not detection_info or not detection_info.get('results'):
            return

        results = detection_info['results']
        if not hasattr(results[0], 'boxes') or not results[0].boxes or len(results[0].boxes) == 0:
            return

        # 获取摄像头名称
        camera_name = f"摄像头{camera_id}"
        if camera_id in self.camera_labels:
            camera_name = f"摄像头{camera_id}"

        # 创建或获取录制器
        if camera_id not in self.camera_recorders:
            self.camera_recorders[camera_id] = CameraVideoRecorder(
                camera_id, camera_name, self.monitor_history_dir,
                self.recording_fps_spinbox.value()
            )
            # 开始录制
            self.camera_recorders[camera_id].start_recording()

        # 添加帧到录制器
        self.camera_recorders[camera_id].add_frame(frame, detection_info)

        # 检查内存使用情况
        self.check_memory_usage()

    def check_memory_usage(self):
        """检查内存使用情况，超过限制时清理最旧的记录"""
        # 计算当前内存使用
        total_size = 0
        for json_file in self.monitor_history_dir.glob("*.json"):
            mp4_file = json_file.with_suffix('.mp4')
            if mp4_file.exists():
                total_size += mp4_file.stat().st_size

        current_usage_mb = total_size / (1024 * 1024)

        if current_usage_mb > self.max_memory_limit:
            # 删除最旧的记录
            self.cleanup_oldest_records()

    def cleanup_oldest_records(self):
        """清理最旧的记录"""
        json_files = list(self.monitor_history_dir.glob("*.json"))
        if not json_files:
            return

        # 按修改时间排序，删除最旧的
        json_files.sort(key=lambda x: x.stat().st_mtime)

        for json_file in json_files[:len(json_files) // 4]:  # 删除25%的最旧记录
            mp4_file = json_file.with_suffix('.mp4')
            try:
                if json_file.exists():
                    json_file.unlink()
                if mp4_file.exists():
                    mp4_file.unlink()
            except Exception as e:
                print(f"清理文件失败 {json_file}: {e}")


class CameraVideoRecorder:
    """摄像头视频录制器"""

    def __init__(self, camera_id, camera_name, output_dir, fps=20):
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.output_dir = output_dir
        self.fps = fps
        self.is_recording = False
        self.video_writer = None
        self.frames = []
        self.detection_stats = {}
        self.total_detections = 0
        self.start_time = None
        self.end_time = None
        self.max_frames_per_file = fps * 30  # 30秒的视频

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
        self.filename_base = f"{self.camera_name}_{timestamp}"
        self.mp4_path = self.output_dir / f"{self.filename_base}.mp4"
        self.json_path = self.output_dir / f"{self.filename_base}.json"

        # 初始化视频写入器（稍后在添加第一帧时设置）
        self.video_writer = None

    def add_frame(self, frame, detection_info):
        """添加帧"""
        if not self.is_recording:
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
            'camera_id': self.camera_id,
            'camera_name': self.camera_name,
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

        print(f"保存监控快照: {self.camera_name} - {len(self.frames)} 帧, {self.total_detections} 次检测")
        print(f"文件路径: {self.mp4_path}")
        print(f"JSON路径: {self.json_path}")


class VideoWidget(QWidget):
    """自定义视频显示组件，带控制功能"""

    def __init__(self, camera_id=0, parent=None):
        super().__init__(parent)
        self.camera_id = camera_id
        self.current_frame = None
        self.detection_state = "NORMAL"  # {0: 'Fall Detected', 1: 'Walking', 2: 'Sitting'}
        self.confidence = 0.0
        self.is_monitoring = False

        self.setup_ui()
        self.setMinimumSize(320, 240)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # 视频显示区域
        self.video_label = QLabel('视频显示区域')
        self.video_label.setStyleSheet(StyleManager.get_video_label_style())
        self.video_label.setAlignment(Qt.AlignCenter)
        # 控制按钮区域
        control_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶️")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setToolTip("启动检测")
        self.start_btn.clicked.connect(self.start_detection)

        self.pause_btn = QPushButton("⏸️")
        self.pause_btn.setObjectName("pauseBtn")
        self.pause_btn.setToolTip("暂停检测")
        self.pause_btn.clicked.connect(self.pause_detection)

        self.stop_btn = QPushButton("⏹️")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setToolTip("停止检测")
        self.stop_btn.clicked.connect(self.stop_detection)

        self.monitor_btn = QPushButton("👁️")
        self.monitor_btn.setObjectName("monitorBtn")
        self.monitor_btn.setToolTip("监控模式")
        self.monitor_btn.clicked.connect(self.toggle_monitor_mode)

        self.clear_btn = QPushButton("🗑️")
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.setToolTip("清空画面")
        self.clear_btn.clicked.connect(self.clear_frame)

        # 状态标签
        self.status_label = QLabel("🟢 就绪")

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.monitor_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.status_label)

        control_layout.addStretch()

        layout.addWidget(self.video_label, stretch=6)
        layout.addLayout(control_layout)
        self.setStyleSheet(StyleManager.get_main_stylesheet())

    def update_frame(self, frame, state="NORMAL", confidence=0.0):
        """更新视频帧"""
        if self.is_monitoring:
            # 监控模式下只显示原始画面
            self.current_frame = frame
            self.display_frame(frame)
            return

        self.current_frame = frame
        self.detection_state = state
        self.confidence = confidence

        # 根据状态设置显示样式  {0: 'Fall Detected', 1: 'Walking', 2: 'Sitting'}
        if state == "Fall Detected":
            self.status_label.setText(f"⚠️ 跌倒检测 (置信度: {confidence:.2f})")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #B91C1C;
                    background: rgba(220, 38, 38, 0.1);
                    border: 1px solid #DC2626;
                }
            """)
        elif state == "Walking":
            self.status_label.setText(f"🚶 行走中 (置信度: {confidence:.2f})")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #2563EB;
                    background: rgba(59, 130, 246, 0.1);
                    border: 1px solid #3B82F6;
                }
            """)
        else:
            self.status_label.setText(f"🪑 坐着 (置信度: {confidence:.2f})")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #059669;
                    background: rgba(16, 185, 129, 0.1);
                    border: 1px solid #10B981;
                }
            """)

        self.display_frame(frame)

    def display_frame(self, frame):
        """显示视频帧"""
        if frame is None:
            return

        # 转换OpenCV图像到QImage
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        # 缩放图像适应标签大小
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    def start_detection(self, camera_id=None):
        """启动检测"""
        if camera_id is not None:
            self.camera_id = camera_id

        self.is_monitoring = False
        self.status_label.setText("🟡 检测中...")

        # TODO: 实际启动摄像头检测逻辑
        print(f"启动摄像头 {self.camera_id} 检测")

    def pause_detection(self):
        """暂停检测"""
        self.status_label.setText("⏸️ 已暂停")

        # TODO: 实际暂停检测逻辑
        print(f"暂停摄像头 {self.camera_id} 检测")

    def stop_detection(self):
        """停止检测"""
        self.status_label.setText("⏹️ 已停止")

        # TODO: 实际停止检测逻辑
        print(f"停止摄像头 {self.camera_id} 检测")

    def toggle_monitor_mode(self):
        """切换监控模式"""
        self.is_monitoring = not self.is_monitoring
        if self.is_monitoring:
            self.monitor_btn.setText("🔍")
            self.monitor_btn.setToolTip("退出监控模式")
            self.status_label.setText("👁️ 监控模式")

        else:
            self.monitor_btn.setText("👁️")
            self.monitor_btn.setToolTip("监控模式")
            self.status_label.setText("🟢 就绪")

        print(f"摄像头 {self.camera_id} 监控模式: {self.is_monitoring}")

    def clear_frame(self):
        """清空画面"""
        self.video_label.clear()
        self.video_label.setText("摄像头未激活")
        self.status_label.setText("⚪ 空闲")

        print(f"清空摄像头 {self.camera_id} 画面")

    def set_monitor_mode(self, enable):
        """设置监控模式"""
        self.is_monitoring = enable
        self.toggle_monitor_mode()


import time
import cv2
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
                               QLabel, QListWidget, QListWidgetItem, QGroupBox, QScrollArea,
                               QMessageBox, QComboBox, QDialog, QFileDialog, QTableWidget,
                               QTableWidgetItem, QHeaderView, QSlider, QSpinBox, QTextEdit)
from PySide6.QtCore import Qt, QTimer, QDateTime, QThread, Signal, Slot, QSize
from PySide6.QtGui import QImage, QPixmap, QFont, QColor
from pathlib import Path
import os
import json


class CameraThread(QThread):
    """摄像头线程，负责捕获和处理视频流"""
    frame_ready = Signal(int, np.ndarray, str, int)  # camera_id, image, status, detection_result

    def __init__(self, camera_id, model=None):
        super().__init__()
        self.camera_id = camera_id
        self.model = model
        self._run_flag = True
        self._paused_flag = False
        self.cap = None

    def run(self):
        """主线程逻辑"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                self.frame_ready.emit(self.camera_id, None, f"错误: 无法打开摄像头 {self.camera_id}", -1)
                return

            self.frame_ready.emit(self.camera_id, None, "状态: 运行中", -1)

            while self._run_flag:
                if not self._paused_flag:
                    ret, frame = self.cap.read()
                    if not ret:
                        self.frame_ready.emit(self.camera_id, None, f"错误: 无法读取摄像头 {self.camera_id}", -1)
                        break

                    # 转换颜色空间 BGR -> RGB
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # 如果有模型，进行检测
                    detection_result = -1  # -1表示无检测结果
                    if self.model:
                        # 这里应该是您的模型检测逻辑
                        # 假设模型返回检测结果 (0: 摔倒, 1: 行走, 2: 坐下)
                        # 实际实现需要根据您的模型调整
                        detection_result = self.detect_with_model(rgb_image)

                    self.frame_ready.emit(self.camera_id, rgb_image,
                                          f"状态: 运行中 - {self.get_status_text(detection_result)}",
                                          detection_result)

                # 控制帧率
                time.sleep(0.03)  # ~30fps

        except Exception as e:
            self.frame_ready.emit(self.camera_id, None, f"错误: {str(e)}", -1)
        finally:
            if self.cap:
                self.cap.release()

    def detect_with_model(self, image):
        """使用模型进行检测"""
        # 这里应该是您的实际模型检测代码
        # 返回检测结果 (0: 摔倒, 1: 行走, 2: 坐下)
        # 示例: 随机返回一个结果用于演示
        return np.random.randint(0, 3)

    def get_status_text(self, result):
        """获取状态文本"""
        status_map = {
            -1: "无检测",
            0: "检测到摔倒",
            1: "检测到行走",
            2: "检测到坐下"
        }
        return status_map.get(result, "未知状态")

    def stop(self):
        """停止线程"""
        self._run_flag = False
        self.wait()

    def pause(self):
        """暂停线程"""
        self._paused_flag = True

    def resume(self):
        """恢复线程"""
        self._paused_flag = False


class EnhancedMonitoringWidget(QWidget):
    """增强版监控页面组件，支持四分屏动态布局"""

    def __init__(self, model_manager, camera_manager):
        super().__init__()
        self.model_manager = model_manager
        self.camera_manager = camera_manager
        self.camera_threads = {}  # 存储摄像头线程
        self.camera_widgets = {}  # 存储每个摄像头的控件和状态
        self.current_model = None
        self.detection_stats = {0: 0, 1: 0, 2: 0}  # 摔倒检测统计
        self.init_ui()
        self.init_timer()

    def init_timer(self):
        """初始化定时器用于更新时间"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 每秒更新一次

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 顶部控制区域
        self.init_control_panel(layout)

        # 监控显示区域
        self.init_monitor_area(layout)

    def init_control_panel(self, parent_layout):
        """初始化控制面板"""
        control_group = QGroupBox("🖥️ 监控控制")
        control_layout = QHBoxLayout(control_group)

        # 左侧区域：模型和摄像头选择
        left_panel = QVBoxLayout()

        # 模型选择
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型:"))

        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        self.init_model_combo()
        model_layout.addWidget(self.model_combo)

        select_model_btn = QPushButton("🔧 选择模型")
        select_model_btn.clicked.connect(self.select_model)
        model_layout.addWidget(select_model_btn)
        left_panel.addLayout(model_layout)

        # 摄像头选择
        camera_layout = QHBoxLayout()
        camera_layout.addWidget(QLabel("摄像头:"), stretch=4)

        self.camera_list = QListWidget()
        self.camera_list.setMaximumWidth(300)
        self.camera_list.setSelectionMode(QListWidget.MultiSelection)
        self.refresh_cameras()
        camera_layout.addWidget(self.camera_list)

        refresh_camera_btn = QPushButton("🔄 刷新")
        refresh_camera_btn.clicked.connect(self.refresh_cameras)
        camera_layout.addWidget(refresh_camera_btn)
        left_panel.addLayout(camera_layout)

        control_layout.addLayout(left_panel)

        # 中间区域：全局控制按钮
        center_panel = QVBoxLayout()
        btn_layout = QHBoxLayout()

        self.start_all_btn = QPushButton("🚀 全部开始")
        self.start_all_btn.clicked.connect(self.start_all_cameras)
        btn_layout.addWidget(self.start_all_btn)

        self.pause_all_btn = QPushButton("⏸️ 全部暂停")
        self.pause_all_btn.clicked.connect(self.pause_all_cameras)
        self.pause_all_btn.setEnabled(False)
        btn_layout.addWidget(self.pause_all_btn)

        self.stop_all_btn = QPushButton("🛑 全部停止")
        self.stop_all_btn.clicked.connect(self.stop_all_cameras)
        self.stop_all_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_all_btn)

        self.clear_all_btn = QPushButton("🗑️ 全部清除")
        self.clear_all_btn.clicked.connect(self.clear_all_cameras)
        self.clear_all_btn.setEnabled(False)
        btn_layout.addWidget(self.clear_all_btn)

        center_panel.addLayout(btn_layout)
        control_layout.addLayout(center_panel, stretch=4)

        # 右侧区域：状态信息
        right_panel = QVBoxLayout()

        # 系统时间显示
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignRight)
        self.update_time()
        right_panel.addWidget(self.time_label)

        # 检测统计
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(QLabel("检测统计:"))

        self.fall_label = QLabel("摔倒: 0")
        self.walk_label = QLabel("行走: 0")
        self.sit_label = QLabel("坐下: 0")

        stats_layout.addWidget(self.fall_label)
        stats_layout.addWidget(self.walk_label)
        stats_layout.addWidget(self.sit_label)
        right_panel.addLayout(stats_layout)

        control_layout.addLayout(right_panel)

        parent_layout.addWidget(control_group)

    def init_monitor_area(self, parent_layout):
        """初始化监控显示区域"""
        self.monitor_scroll = QScrollArea()
        self.monitor_scroll.setStyleSheet("""
            QScrollArea {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(236, 240, 241, 0.9),
                    stop:1 rgba(189, 195, 199, 0.9));
                border-radius: 8px;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollArea::corner {
                background: transparent;
            }
        """)

        self.monitor_widget = QWidget()
        self.monitor_layout = QGridLayout(self.monitor_widget)
        self.monitor_scroll.setWidget(self.monitor_widget)
        self.monitor_scroll.setWidgetResizable(True)

        parent_layout.addWidget(self.monitor_scroll)

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
            self.try_load_default_model()

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

    def on_model_changed(self, model_text):
        """模型选择改变"""
        if model_text != "无可用模型":
            self.load_model_by_name(model_text)

    def load_model(self, model_path):
        """加载模型"""
        try:
            self.current_model = YOLO(model_path)
            self.start_all_btn.setEnabled(True)
            return True
        except Exception as e:
            print(f"模型加载失败: {e}")
            return False

    def select_model(self):
        """选择模型"""
        dialog = ModelSelectionDialog(self.model_manager, self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_model:
            try:
                self.current_model = YOLO(dialog.selected_model)
                model_name = Path(dialog.selected_model).name
                self.model_combo.clear()
                self.model_combo.addItem(model_name)
                self.start_all_btn.setEnabled(True)
                QMessageBox.information(self, "成功", f"模型加载成功: {model_name}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"模型加载失败: {str(e)}")

    def refresh_cameras(self):
        """刷新摄像头列表"""
        self.camera_manager.scan_cameras()
        self.camera_list.clear()

        for camera in self.camera_manager.get_available_cameras():
            item = QListWidgetItem(f"📹 {camera['name']} ({camera['resolution']})")
            item.setData(Qt.UserRole, camera['id'])
            self.camera_list.addItem(item)

    def start_all_cameras(self):
        """启动所有选中的摄像头"""
        if not self.current_model:
            QMessageBox.warning(self, "警告", "请先选择模型")
            return

        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请选择至少一个摄像头")
            return

        camera_ids = [item.data(Qt.UserRole) for item in selected_items]
        self.clear_monitor_display()

        # 根据摄像头数量设置布局
        self.setup_grid_layout(len(camera_ids))

        for cam_id in camera_ids:
            self.add_camera_widget(cam_id)
            self.start_camera_thread(cam_id)

        self.start_all_btn.setEnabled(False)
        self.pause_all_btn.setEnabled(True)
        self.stop_all_btn.setEnabled(True)
        self.clear_all_btn.setEnabled(True)

    def setup_grid_layout(self, num_cameras):
        """根据摄像头数量设置网格布局"""
        # 清除现有布局
        for i in reversed(range(self.monitor_layout.count())):
            widget = self.monitor_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # 设置新的网格布局
        if num_cameras == 1:
            rows, cols = 1, 1
        elif num_cameras == 2:
            rows, cols = 1, 2
        elif num_cameras == 3:
            rows, cols = 2, 2  # 3个摄像头时使用2x2网格，最后一个位置留空
        else:  # 4个或更多
            rows, cols = 2, 2

        # 设置行列伸缩
        for r in range(rows):
            self.monitor_layout.setRowStretch(r, 1)
        for c in range(cols):
            self.monitor_layout.setColumnStretch(c, 1)

    def add_camera_widget(self, camera_id):
        """为摄像头添加显示和控制部件"""
        camera_group = QGroupBox(f"📹 摄像头 {camera_id}")
        camera_group.setStyleSheet("""
            QGroupBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(248, 249, 250, 0.9), stop:1 rgba(233, 236, 239, 0.9));
                color: #7f8c8d;
                font-weight: bold;
                font-size: 14px;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(camera_group)

        # 图像显示区域
        image_label = QLabel("等待连接...")
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("background-color: #ecf0f1;")
        layout.addWidget(image_label)

        # 状态标签
        status_label = QLabel("状态: 初始化中...")
        status_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addWidget(status_label)

        # 控制按钮
        btn_layout = QHBoxLayout()

        start_btn = QPushButton("▶️ 开始")
        start_btn.clicked.connect(lambda: self.start_camera(camera_id))
        btn_layout.addWidget(start_btn)

        pause_btn = QPushButton("⏸️ 暂停")
        pause_btn.clicked.connect(lambda: self.pause_camera(camera_id))
        pause_btn.setEnabled(False)
        btn_layout.addWidget(pause_btn)

        stop_btn = QPushButton("🛑 停止")
        stop_btn.clicked.connect(lambda: self.stop_camera(camera_id))
        stop_btn.setEnabled(False)
        btn_layout.addWidget(stop_btn)

        layout.addLayout(btn_layout)

        # 添加到布局
        position = self.get_next_grid_position()
        self.monitor_layout.addWidget(camera_group, position[0], position[1])

        # 保存控件引用
        self.camera_widgets[camera_id] = {
            'group': camera_group,
            'image': image_label,
            'status': status_label,
            'start_btn': start_btn,
            'pause_btn': pause_btn,
            'stop_btn': stop_btn,
            'running': False,
            'paused': False
        }

    def get_next_grid_position(self):
        """获取下一个网格位置"""
        count = len(self.camera_widgets)
        if count == 0:
            return (0, 0)
        elif count == 1:
            return (0, 1)
        elif count == 2:
            return (1, 0)
        elif count == 3:
            return (1, 1)
        else:
            # 超过4个时循环使用位置
            row = (count // 2) % 2
            col = count % 2
            return (row, col)

    def start_camera_thread(self, camera_id):
        """启动摄像头线程"""
        if camera_id in self.camera_widgets and camera_id not in self.camera_threads:
            thread = CameraThread(camera_id, self.current_model)
            thread.frame_ready.connect(self.update_camera_display)
            thread.finished.connect(lambda: self.on_camera_thread_finished(camera_id))
            self.camera_threads[camera_id] = thread
            thread.start()
            self.start_camera(camera_id)

    def start_camera(self, camera_id):
        """启动单个摄像头"""
        if camera_id in self.camera_widgets:
            self.camera_widgets[camera_id]['status'].setText("状态: 运行中")
            self.camera_widgets[camera_id]['start_btn'].setEnabled(False)
            self.camera_widgets[camera_id]['pause_btn'].setEnabled(True)
            self.camera_widgets[camera_id]['stop_btn'].setEnabled(True)
            self.camera_widgets[camera_id]['running'] = True
            self.camera_widgets[camera_id]['paused'] = False

    def pause_camera(self, camera_id):
        """暂停/继续单个摄像头"""
        if camera_id in self.camera_widgets and camera_id in self.camera_threads:
            widget = self.camera_widgets[camera_id]
            thread = self.camera_threads[camera_id]

            if widget['paused']:
                # 恢复
                thread.resume()
                widget['status'].setText("状态: 运行中")
                widget['pause_btn'].setText("⏸️ 暂停")
                widget['paused'] = False
            else:
                # 暂停
                thread.pause()
                widget['status'].setText("状态: 已暂停")
                widget['pause_btn'].setText("▶️ 继续")
                widget['paused'] = True

    def stop_camera(self, camera_id):
        """停止单个摄像头"""
        if camera_id in self.camera_threads:
            self.camera_threads[camera_id].stop()
            self.camera_threads[camera_id].wait()
            del self.camera_threads[camera_id]

        if camera_id in self.camera_widgets:
            self.camera_widgets[camera_id]['status'].setText("状态: 已停止")
            self.camera_widgets[camera_id]['start_btn'].setEnabled(True)
            self.camera_widgets[camera_id]['pause_btn'].setEnabled(False)
            self.camera_widgets[camera_id]['stop_btn'].setEnabled(False)
            self.camera_widgets[camera_id]['running'] = False
            self.camera_widgets[camera_id]['paused'] = False

    def on_camera_thread_finished(self, camera_id):
        """摄像头线程结束时的处理"""
        if camera_id in self.camera_threads:
            del self.camera_threads[camera_id]

        if camera_id in self.camera_widgets:
            self.camera_widgets[camera_id]['status'].setText("状态: 已停止")
            self.camera_widgets[camera_id]['start_btn'].setEnabled(True)
            self.camera_widgets[camera_id]['pause_btn'].setEnabled(False)
            self.camera_widgets[camera_id]['stop_btn'].setEnabled(False)
            self.camera_widgets[camera_id]['running'] = False
            self.camera_widgets[camera_id]['paused'] = False

    def pause_all_cameras(self):
        """暂停/继续所有摄像头"""
        if any(w['running'] for w in self.camera_widgets.values()):
            all_paused = all(w['paused'] for w in self.camera_widgets.values() if w['running'])

            for cam_id, widget in self.camera_widgets.items():
                if widget['running']:
                    if all_paused:
                        # 全部恢复
                        self.pause_camera(cam_id)
                        self.pause_all_btn.setText("⏸️ 全部暂停")
                    else:
                        # 全部暂停
                        if not widget['paused']:
                            self.pause_camera(cam_id)
                        self.pause_all_btn.setText("▶️ 全部继续")

    def stop_all_cameras(self):
        """停止所有摄像头"""
        for cam_id in list(self.camera_threads.keys()):
            self.stop_camera(cam_id)

        self.start_all_btn.setEnabled(True)
        self.pause_all_btn.setEnabled(False)
        self.stop_all_btn.setEnabled(False)

    def clear_all_cameras(self):
        """清除所有摄像头"""
        self.stop_all_cameras()
        self.clear_monitor_display()
        self.start_all_btn.setEnabled(True)
        self.clear_all_btn.setEnabled(False)
        self.detection_stats = {0: 0, 1: 0, 2: 0}
        self.update_stats()

    def clear_monitor_display(self):
        """清空监控显示"""
        for cam_id in list(self.camera_widgets.keys()):
            self.camera_widgets[cam_id]['group'].deleteLater()
        self.camera_widgets.clear()

    def update_time(self):
        """更新时间显示"""
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.time_label.setText(f"🕒 系统时间: {current_time}")

    def update_stats(self):
        """更新检测统计"""
        self.fall_label.setText(f"摔倒: {self.detection_stats[0]}")
        self.walk_label.setText(f"行走: {self.detection_stats[1]}")
        self.sit_label.setText(f"坐下: {self.detection_stats[2]}")

    @Slot(int, np.ndarray, str, int)
    def update_camera_display(self, camera_id, image, status, detection_result):
        """更新摄像头显示"""
        if camera_id in self.camera_widgets:
            # 显示图像
            if image is not None:
                height, width, channel = image.shape
                bytes_per_line = 3 * width
                q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                self.camera_widgets[camera_id]['image'].setPixmap(
                    pixmap.scaled(self.camera_widgets[camera_id]['image'].size(),
                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )

            # 更新状态
            if status:
                self.camera_widgets[camera_id]['status'].setText(status)

            # 更新检测统计
            if detection_result in self.detection_stats:
                self.detection_stats[detection_result] += 1
                self.update_stats()
class SliceDetailDialog(QDialog):
        """切片详细信息弹窗"""

        def __init__(self, nii_data, slice_index, direction, parent=None):
            super().__init__(parent)
            self.nii_data = nii_data
            self.current_slice_index = slice_index
            self.direction = direction
            self.max_slices = nii_data.shape[direction]

            self.init_ui()
            self.update_slice_display()
            # 启用鼠标跟踪以捕获滚轮事件
            self.setMouseTracking(True)

        def init_ui(self):
            self.setWindowTitle(f"切片详细信息 - Slice {self.current_slice_index}")
            self.resize(600, 600)

            layout = QVBoxLayout(self)

            # 图像显示区域
            self.image_label = QLabel()
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setMinimumSize(400, 400)
            # 启用图像标签的鼠标事件
            self.image_label.setMouseTracking(True)
            self.image_label.installEventFilter(self)  # 安装事件过滤器
            layout.addWidget(self.image_label)

            # 控制按钮区域
            button_layout = QHBoxLayout()

            self.prev_button = QPushButton("⬆️ 上一张")
            self.prev_button.clicked.connect(self.show_previous_slice)
            button_layout.addWidget(self.prev_button)

            self.slice_info_label = QLabel(f"Slice {self.current_slice_index}/{self.max_slices - 1}")
            self.slice_info_label.setAlignment(Qt.AlignCenter)
            button_layout.addWidget(self.slice_info_label)

            self.next_button = QPushButton("⬇️ 下一张")
            self.next_button.clicked.connect(self.show_next_slice)
            button_layout.addWidget(self.next_button)

            layout.addLayout(button_layout)

            # 关闭按钮
            close_button = QPushButton("关闭")
            close_button.clicked.connect(self.accept)
            layout.addWidget(close_button)

            # 更新按钮状态
            self.update_button_states()
        def eventFilter(self, obj, event):
            """事件过滤器，用于处理鼠标滚轮事件"""
            if obj == self.image_label and event.type() == QEvent.Wheel:
                if event.angleDelta().y() > 0:  # 向上滚动
                    self.show_previous_slice()
                else:  # 向下滚动
                    self.show_next_slice()
                return True
            return super().eventFilter(obj, event)
        def update_slice_display(self):
            """更新切片显示"""
            try:
                # 提取切片数据
                if self.direction == 0:  # Sagittal
                    slice_data = self.nii_data[self.current_slice_index, :, :]
                elif self.direction == 1:  # Coronal
                    slice_data = self.nii_data[:, self.current_slice_index, :]
                else:  # Axial
                    slice_data = self.nii_data[:, :, self.current_slice_index]

                # 确保数据是连续的
                if not slice_data.flags['C_CONTIGUOUS']:
                    slice_data = np.ascontiguousarray(slice_data)

                # 转换为 QImage 显示
                # 归一化数据到 0-255 范围
                slice_normalized = ((slice_data - slice_data.min()) /
                                    (slice_data.max() - slice_data.min()) * 255).astype(np.uint8)

                height, width = slice_normalized.shape
                bytes_per_line = width
                q_img = QImage(slice_normalized.data, width, height, bytes_per_line, QImage.Format_Grayscale8)

                # 缩放图像以适应显示区域
                pixmap = QPixmap.fromImage(q_img)
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)

                # 更新切片信息
                self.slice_info_label.setText(f"Slice {self.current_slice_index}/{self.max_slices - 1}")

                # 更新按钮状态
                self.update_button_states()

            except Exception as e:
                self.image_label.setText(f"显示错误: {str(e)}")

        def update_button_states(self):
            """更新按钮状态"""
            self.prev_button.setEnabled(bool(self.current_slice_index > 0))
            self.next_button.setEnabled(bool(self.current_slice_index < self.max_slices - 1))

        def show_previous_slice(self):
            """显示上一张切片"""
            if self.current_slice_index > 0:
                self.current_slice_index -= 1
                self.update_slice_display()

        def show_next_slice(self):
            """显示下一张切片"""
            if self.current_slice_index < self.max_slices - 1:
                self.current_slice_index += 1
                self.update_slice_display()


class SnapshotWidget(QWidget):
    """监控快照组件 - 用于显示和回放已保存的监控快照"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.snapshots = []  # 存储快照记录
        self.current_snapshot_index = 0
        self.monitor_history_dir = Path("monitor_history")
        self.monitor_history_dir.mkdir(exist_ok=True)
        # 添加detection_history目录支持
        self.detection_history_dir = Path("detection_history")
        self.detection_history_dir.mkdir(exist_ok=True)

        self.init_ui()
        self.load_snapshots()

    def init_ui(self):
        """初始化UI界面"""
        layout = QVBoxLayout(self)

        # 快照列表和播放区域
        content_layout = QHBoxLayout()

        # 左侧：快照列表
        left_panel = QVBoxLayout()

        list_group = QGroupBox("📋 快照历史")
        list_group.setMaximumHeight(780)
        list_layout = QVBoxLayout(list_group)

        self.snapshot_list = QListWidget()
        self.snapshot_list.itemClicked.connect(self.on_snapshot_selected)
        list_layout.addWidget(self.snapshot_list)

        # 快照操作按钮
        snapshot_btn_layout = QHBoxLayout()

        self.play_btn = QPushButton("▶️ 播放")
        self.play_btn.clicked.connect(self.play_selected_snapshot)
        self.play_btn.setEnabled(False)
        snapshot_btn_layout.addWidget(self.play_btn)

        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.clicked.connect(self.delete_selected_snapshot)
        self.delete_btn.setEnabled(False)
        snapshot_btn_layout.addWidget(self.delete_btn)

        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self.load_snapshots)
        snapshot_btn_layout.addWidget(self.refresh_btn)

        # 添加导出按钮到布局中
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.clicked.connect(self.export_selected_snapshot)
        self.export_btn.setEnabled(False)
        snapshot_btn_layout.addWidget(self.export_btn)

        list_layout.addLayout(snapshot_btn_layout)
        left_panel.addWidget(list_group)

        content_layout.addLayout(left_panel, 1)

        # 右侧：播放区域
        right_panel = QVBoxLayout()

        player_group = QGroupBox("🎥 快照播放器")
        # player_group.setMaximumHeight(780)  # 减少高度
        player_layout = QVBoxLayout(player_group)

        # 视频显示区域
        self.video_label = QLabel("选择快照进行播放")
        self.video_label.setMinimumSize(640, 390)
        self.video_label.setStyleSheet("""
            QLabel {
                border: 1px solid rgba(52, 152, 219, 0.3);
                font-size: 14px;
                border-radius: 10px;
            }
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setScaledContents(True)
        player_layout.addWidget(self.video_label)

        # 播放控制
        playback_layout = QHBoxLayout()

        self.playback_btn = QPushButton("▶️")
        self.playback_btn.clicked.connect(self.toggle_playback)
        self.playback_btn.setEnabled(False)
        playback_layout.addWidget(self.playback_btn)

        self.stop_btn = QPushButton("⏹️")
        self.stop_btn.clicked.connect(self.stop_playback)
        self.stop_btn.setEnabled(False)
        playback_layout.addWidget(self.stop_btn)

        # 进度条
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setEnabled(False)
        self.progress_slider.valueChanged.connect(self.on_progress_changed)
        playback_layout.addWidget(self.progress_slider)

        # 时间显示
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        playback_layout.addWidget(self.time_label)

        player_layout.addLayout(playback_layout, stretch=5)

        # 快照信息
        info_group = QGroupBox("📊 快照信息")
        info_group.setStyleSheet("""
                    QGroupBox {
                border: 1px solid rgba(52, 152, 219, 0.3);
                font-size: 14px;
                border-radius: 10px;
            }
        """
                                 )
        info_layout = QVBoxLayout(info_group)

        self.info_text = QTextEdit()
        self.info_text.setMinimumHeight(170)
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background: rgba(248, 249, 250, 0.8);
                border: 1px solid rgba(189, 195, 199, 0.3);
                border-radius: 5px;
                font-size: 11px;
                color: #2c3e50;
            }
        """)
        info_layout.addWidget(self.info_text)

        player_layout.addWidget(info_group, stretch=3)
        right_panel.addWidget(player_group)

        content_layout.addLayout(right_panel, 2)
        layout.addLayout(content_layout)

        # 初始化播放定时器
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.update_playback)
        self.current_frame_index = 0
        self.is_playing = False

    def toggle_recording(self):
        """切换录制状态"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """开始录制"""
        self.is_recording = True
        self.recording_frames.clear()
        self.recording_start_time = time.time()
        self.max_recording_duration = self.duration_spinbox.value()

        self.record_btn.setText("⏹️ 停止录制")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #95a5a6, stop:1 #7f8c8d);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7f8c8d, stop:1 #6c7b7d);
            }
        """)
        self.save_btn.setEnabled(False)
        self.clear_btn.setEnabled(True)
        self.recording_status.setText("状态: 录制中...")
        self.recording_status.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 12px;
                padding: 5px;
                background: rgba(231, 76, 60, 0.1);
                border-radius: 5px;
            }
        """)

    def stop_recording(self):
        """停止录制"""
        self.is_recording = False

        self.record_btn.setText("🔴 开始录制")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c0392b, stop:1 #a93226);
            }
        """)

        if len(self.recording_frames) > 0:
            self.save_btn.setEnabled(True)

        self.recording_status.setText(f"状态: 录制完成 ({len(self.recording_frames)} 帧)")
        self.recording_status.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 12px;
                padding: 5px;
                background: rgba(39, 174, 96, 0.1);
                border-radius: 5px;
            }
        """)

    def add_frame(self, frame, detection_info=None):
        """添加帧到录制中"""
        if not self.is_recording:
            return

        # 检查录制时长
        if time.time() - self.recording_start_time > self.max_recording_duration:
            self.stop_recording()
            return

        frame_data = {
            'frame': frame.copy(),
            'timestamp': time.time(),
            'detection_info': detection_info or {}
        }
        self.recording_frames.append(frame_data)

        # 更新状态
        elapsed = time.time() - self.recording_start_time
        self.recording_status.setText(f"状态: 录制中... ({len(self.recording_frames)} 帧, {elapsed:.1f}s)")

    def save_current_recording(self):
        """保存当前录制"""
        if not self.recording_frames:
            QMessageBox.warning(self, "警告", "没有可保存的录制内容")
            return

        # 生成快照ID
        snapshot_id = f"snapshot_{int(time.time())}"
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.json"

        # 保存帧数据
        snapshot_data = {
            'id': snapshot_id,
            'created_time': time.time(),
            'duration': self.max_recording_duration,
            'fps': self.fps_spinbox.value(),
            'frame_count': len(self.recording_frames),
            'frames': []
        }

        # 压缩保存帧数据
        for i, frame_data in enumerate(self.recording_frames):
            # 将帧转换为base64编码的字符串
            _, buffer = cv2.imencode('.jpg', frame_data['frame'], [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_str = buffer.tobytes().hex()

            snapshot_data['frames'].append({
                'index': i,
                'timestamp': frame_data['timestamp'],
                'frame_data': frame_str,
                'detection_info': frame_data['detection_info']
            })

        # 保存到文件
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, ensure_ascii=False, indent=2)

        # 添加到快照列表
        snapshot_info = {
            'id': snapshot_id,
            'path': str(snapshot_path),
            'created_time': snapshot_data['created_time'],
            'duration': snapshot_data['duration'],
            'frame_count': snapshot_data['frame_count'],
            'fps': snapshot_data['fps']
        }

        self.snapshots.append(snapshot_info)
        self.update_snapshot_list()

        QMessageBox.information(self, "成功", f"快照已保存: {snapshot_id}")

        # 清空当前录制
        self.clear_recording()

    def clear_recording(self):
        """清空当前录制"""
        self.recording_frames.clear()
        self.save_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.recording_status.setText("状态: 未录制")
        self.recording_status.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                padding: 5px;
                background: rgba(236, 240, 241, 0.5);
                border-radius: 5px;
            }
        """)

    def load_snapshots(self):
        """加载已保存的快照"""
        self.snapshots.clear()

        # 扫描monitor_history目录下的JSON文件
        for json_file in self.monitor_history_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 检查对应的MP4文件是否存在
                mp4_file = json_file.with_suffix('.mp4')
                if mp4_file.exists():
                    snapshot_info = {
                        'camera_name': data.get('camera_name', '未知摄像头'),
                        'start_time': data.get('start_time', 0),
                        'end_time': data.get('end_time', 0),
                        'file_size': self._get_file_size(mp4_file),
                        'detection_stats': data.get('detection_stats', {}),
                        'json_path': str(json_file),
                        'mp4_path': str(mp4_file),
                        'fps': data.get('fps', 20),
                        'total_detections': data.get('total_detections', 0),
                        'source': 'monitor'  # 标记来源为监控
                    }
                    self.snapshots.append(snapshot_info)
            except Exception as e:
                print(f"加载快照失败 {json_file}: {e}")

        # 扫描detection_history目录下的JSON文件
        for json_file in self.detection_history_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 检查对应的MP4文件是否存在
                mp4_file = json_file.with_suffix('.mp4')
                if mp4_file.exists():
                    snapshot_info = {
                        'camera_name': data.get('source_name', '未知源'),
                        'start_time': data.get('start_time', 0),
                        'end_time': data.get('end_time', 0),
                        'file_size': self._get_file_size(mp4_file),
                        'detection_stats': data.get('detection_stats', {}),
                        'json_path': str(json_file),
                        'mp4_path': str(mp4_file),
                        'fps': data.get('fps', 20),
                        'total_detections': data.get('total_detections', 0),
                        'source': 'detection'  # 标记来源为检测
                    }
                    self.snapshots.append(snapshot_info)
            except Exception as e:
                print(f"加载快照失败 {json_file}: {e}")

        self.update_snapshot_list()

    def _get_file_size(self, file_path):
        """获取文件大小"""
        try:
            size = file_path.stat().st_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"

    def update_snapshot_list(self):
        """更新快照列表显示"""
        self.snapshot_list.clear()

        # 按开始时间排序（最新的在前）
        self.snapshots.sort(key=lambda x: x['start_time'], reverse=True)

        for snapshot in self.snapshots:
            start_time = datetime.fromtimestamp(snapshot['start_time'])
            end_time = datetime.fromtimestamp(snapshot['end_time'])

            # 格式化检测统计信息
            stats_text = ""
            if snapshot['detection_stats']:
                stats_items = []
                for class_name, count in snapshot['detection_stats'].items():
                    stats_items.append(f"{class_name}:{count}")
                stats_text = " | ".join(stats_items)

            # 根据来源添加不同的前缀标识
            source_prefix = "🖥️" if snapshot['source'] == 'monitor' else "📹"
            item_text = f"{source_prefix} {snapshot['camera_name']}\n"
            item_text += f"时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            item_text += f"文件大小: {snapshot['file_size']} | 检测次数: {snapshot['total_detections']}\n"
            if stats_text:
                item_text += f"检测统计: {stats_text}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, snapshot)
            self.snapshot_list.addItem(item)

    def on_snapshot_selected(self, item):
        """快照被选中"""
        snapshot = item.data(Qt.UserRole)
        self.current_snapshot_index = self.snapshots.index(snapshot)
        self.play_btn.setEnabled(True)
        # self.playback_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

        # 显示快照信息
        self.show_snapshot_info(snapshot)

    def show_snapshot_info(self, snapshot):
        """显示快照信息"""
        start_time = datetime.fromtimestamp(snapshot['start_time'])
        end_time = datetime.fromtimestamp(snapshot['end_time'])
        duration = snapshot['end_time'] - snapshot['start_time']

        info_text = f"摄像头: {snapshot['camera_name']}\n"
        info_text += f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        info_text += f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        info_text += f"录制时长: {duration:.1f} 秒\n"
        info_text += f"文件大小: {snapshot['file_size']}\n"
        info_text += f"帧率: {snapshot['fps']} fps\n"
        info_text += f"检测次数: {snapshot['total_detections']}\n"

        if snapshot['detection_stats']:
            info_text += f"检测统计:\n"
            for class_name, count in snapshot['detection_stats'].items():
                info_text += f"  {class_name}: {count} 次\n"

        info_text += f"视频文件: {snapshot['mp4_path']}"

        self.info_text.setText(info_text)

    def play_selected_snapshot(self):
        """播放选中的快照"""
        if not self.snapshots or self.current_snapshot_index >= len(self.snapshots):
            return

        snapshot = self.snapshots[self.current_snapshot_index]

        try:
            # 使用OpenCV读取MP4文件
            cap = cv2.VideoCapture(snapshot['mp4_path'])
            if not cap.isOpened():
                QMessageBox.warning(self, "错误", "无法打开视频文件")
                return

            # 读取所有帧
            self.playback_frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                self.playback_frames.append(frame)

            cap.release()

            if not self.playback_frames:
                QMessageBox.warning(self, "错误", "视频文件为空")
                return

            # 设置播放参数
            self.current_frame_index = 0
            self.playback_fps = snapshot['fps']
            self.playback_interval = 1000 // self.playback_fps  # 毫秒

            # 设置进度条
            self.progress_slider.setRange(0, len(self.playback_frames) - 1)
            self.progress_slider.setValue(0)
            self.progress_slider.setEnabled(True)
            self.playback_btn.setEnabled(True)

            # 开始播放
            self.toggle_playback()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"播放快照失败: {str(e)}")

    def toggle_playback(self):
        """切换播放状态"""
        if not hasattr(self, 'playback_frames') or not self.playback_frames:
            return

        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()

    def start_playback(self):
        """开始播放"""
        self.is_playing = True
        self.playback_btn.setText("⏸️")
        self.stop_btn.setEnabled(True)

        self.playback_timer.start(self.playback_interval)

    def pause_playback(self):
        """暂停播放"""
        self.is_playing = False
        self.playback_btn.setText("▶️")

        self.playback_timer.stop()

    def stop_playback(self):
        """停止播放"""
        self.is_playing = False
        self.playback_btn.setText("▶️")
        self.stop_btn.setEnabled(False)

        self.playback_timer.stop()
        self.current_frame_index = 0
        self.progress_slider.setValue(0)

        # 显示第一帧
        if hasattr(self, 'playback_frames') and self.playback_frames:
            self.display_frame(self.playback_frames[0])

    def update_playback(self):
        """更新播放"""
        if not hasattr(self, 'playback_frames') or not self.playback_frames:
            return

        if self.current_frame_index >= len(self.playback_frames):
            self.stop_playback()
            return

        # 显示当前帧
        frame = self.playback_frames[self.current_frame_index]
        self.display_frame(frame)

        # 更新进度
        self.progress_slider.setValue(self.current_frame_index)

        # 更新时间显示
        current_time = self.current_frame_index / self.playback_fps
        total_time = len(self.playback_frames) / self.playback_fps
        self.time_label.setText(f"{current_time:.1f}s / {total_time:.1f}s")

        self.current_frame_index += 1

    def on_progress_changed(self, value):
        """进度条改变"""
        if hasattr(self, 'playback_frames') and self.playback_frames and not self.is_playing:
            self.current_frame_index = value
            frame = self.playback_frames[value]
            self.display_frame(frame)

            # 更新时间显示
            current_time = value / self.playback_fps
            total_time = len(self.playback_frames) / self.playback_fps
            self.time_label.setText(f"{current_time:.1f}s / {total_time:.1f}s")

    def display_frame(self, frame):
        """显示帧"""
        if frame is None:
            return

        # 转换颜色空间
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # 缩放适应显示区域
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    def delete_selected_snapshot(self):
        """删除选中的快照"""
        if not self.snapshots or self.current_snapshot_index >= len(self.snapshots):
            return

        snapshot = self.snapshots[self.current_snapshot_index]

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除摄像头 '{snapshot['camera_name']}' 的快照吗？\n此操作不可恢复。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # 删除MP4和JSON文件
                Path(snapshot['mp4_path']).unlink()
                Path(snapshot['json_path']).unlink()

                # 从列表中移除
                self.snapshots.pop(self.current_snapshot_index)
                self.update_snapshot_list()

                # 清空播放区域
                self.video_label.clear()
                self.video_label.setText("选择快照进行播放")
                self.info_text.clear()

                # 禁用按钮
                self.play_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self.export_btn.setEnabled(False)

                QMessageBox.information(self, "成功", "快照已删除")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除快照失败: {str(e)}")

    # 添加导出功能的实现
    def export_selected_snapshot(self):
        """导出选中的快照"""
        if not self.snapshots or self.current_snapshot_index >= len(self.snapshots):
            return

        snapshot = self.snapshots[self.current_snapshot_index]

        # 选择导出目录
        export_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not export_dir:
            return

        try:
            export_path = Path(export_dir)
            mp4_file = Path(snapshot['mp4_path'])
            json_file = Path(snapshot['json_path'])

            # 构造导出文件路径
            mp4_export_path = export_path / mp4_file.name
            json_export_path = export_path / json_file.name

            # 复制文件
            import shutil
            shutil.copy2(mp4_file, mp4_export_path)
            shutil.copy2(json_file, json_export_path)

            QMessageBox.information(self, "成功", f"快照已导出到:\n{export_path}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出快照失败: {str(e)}")


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

        self.slice_update_timer = QTimer()
        self.slice_update_timer.setSingleShot(True)
        self.slice_update_timer.timeout.connect(self.update_slice_preview)
        self.slice_range_changed = False

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("🚀 基于YOLO的脑部肿瘤检测系统 ")
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
        self.select_file_btn = QPushButton("📁 选择文件/文件夹")
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

        # 创建 NIfTI 格式转换标签页
        nifti_tab = self.create_nifti_conversion_tab()
        self.tab_widget.addTab(nifti_tab, " NIfTI 转换")

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

    def create_nifti_conversion_tab(self):
        """创建NIfTI格式转换标签页"""
        nifti_tab = QWidget()
        layout = QVBoxLayout(nifti_tab)

        # 文件选择区域
        file_group = QGroupBox("📁 文件选择")
        file_layout = QVBoxLayout(file_group)

        file_select_layout = QHBoxLayout()
        self.nii_file_edit = QLineEdit()
        self.nii_file_edit.setPlaceholderText("选择NIfTI文件或目录...")
        file_select_layout.addWidget(self.nii_file_edit)

        self.browse_nii_btn = QPushButton("浏览")
        self.browse_nii_btn.clicked.connect(self.browse_nii_file)
        file_select_layout.addWidget(self.browse_nii_btn)

        file_layout.addLayout(file_select_layout)

        # 输出目录设置
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("📤 输出目录:"))
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("自动设置为输入目录 + '_swift_normal'")
        output_layout.addWidget(self.output_dir_edit)

        self.browse_output_btn = QPushButton("浏览")
        self.browse_output_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.browse_output_btn)

        file_layout.addLayout(output_layout)

        layout.addWidget(file_group)

        # 切片设置和文件信息横向布局区域
        settings_layout = QHBoxLayout()
        # 切片设置区域
        slice_group = QGroupBox("🔪 切片设置")
        slice_layout = QVBoxLayout(slice_group)

        # 切片方向选择
        direction_layout = QHBoxLayout()
        direction_layout.addWidget(QLabel("🧭 切片方向:"))
        self.slice_direction_combo = QComboBox()
        self.slice_direction_combo.addItems(["冠状位 (Coronal)","水平位 (Axial)", "矢状位 (Sagittal)"])
        self.slice_direction_combo.setCurrentText("水平位 (Axial)")
        self.slice_direction_combo.currentTextChanged.connect(self.update_slice_info)
        direction_layout.addWidget(self.slice_direction_combo)
        direction_layout.addStretch()

        slice_layout.addLayout(direction_layout)

        # 切片范围设置
        range_layout = QHBoxLayout()
        # 在创建切片范围设置的部分，为 QSpinBox 添加信号连接
        range_layout.addWidget(QLabel("📏 切片范围:"))
        self.start_slice_spin = QSpinBox()
        self.start_slice_spin.setMinimum(0)
        self.start_slice_spin.setValue(60)
        self.start_slice_spin.valueChanged.connect(self.on_slice_range_changed)  # 添加这一行
        range_layout.addWidget(self.start_slice_spin)

        range_layout.addWidget(QLabel(" - "))

        self.end_slice_spin = QSpinBox()
        self.end_slice_spin.setMinimum(0)
        self.end_slice_spin.setMaximum(1000)
        self.end_slice_spin.setValue(150)
        self.end_slice_spin.valueChanged.connect(self.on_slice_range_changed)  # 添加这一行
        range_layout.addWidget(self.end_slice_spin)

        range_layout.addStretch()
        slice_layout.addLayout(range_layout)

        # 切片信息显示
        info_layout = QHBoxLayout()
        self.slice_info_label = QLabel("_slices: 0, 当前范围: 0-0")
        info_layout.addWidget(self.slice_info_label)
        info_layout.addStretch()
        slice_layout.addLayout(info_layout)

        # layout.addWidget(slice_group)

        # 文件信息显示区域
        info_group = QGroupBox("📊 文件信息")
        info_layout = QVBoxLayout(info_group)

        self.file_info_text = QTextEdit()
        self.file_info_text.setReadOnly(True)
        self.file_info_text.setMaximumHeight(100)
        info_layout.addWidget(self.file_info_text)

        # layout.addWidget(info_group)
        # 添加两个区域到水平布局
        settings_layout.addWidget(slice_group)
        settings_layout.addWidget(info_group)
        slice_group.setMaximumHeight(150)  # 限制切片设置区域高度
        info_group.setMaximumHeight(150)  # 限制文件信息区域高度
        # 设置两个区域等宽
        settings_layout.setStretch(0, 1)
        settings_layout.setStretch(1, 1)

        layout.addLayout(settings_layout)
        # 预览区域
        preview_group = QGroupBox("🖼️ 切片预览")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_widget = QWidget()
        self.preview_layout = QHBoxLayout(self.preview_widget)
        self.preview_scroll.setWidget(self.preview_widget)

        preview_layout.addWidget(self.preview_scroll)
        layout.addWidget(preview_group)

        # 控制按钮
        button_layout = QHBoxLayout()
        self.convert_btn = QPushButton("🔄 转换")
        self.convert_btn.clicked.connect(self.convert_nifti)
        self.convert_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        button_layout.addWidget(self.convert_btn)

        self.preview_btn = QPushButton("👀 预览")
        self.preview_btn.clicked.connect(self.generate_preview)
        button_layout.addWidget(self.preview_btn)

        layout.addLayout(button_layout)

        # 初始化状态
        self.current_nii_file = None
        self.nii_data = None

        return nifti_tab

    def on_slice_range_changed(self, value):
        """当切片范围改变时更新预览图"""
        # 设置标志位，表示切片范围已更改
        self.slice_range_changed = True

        # 重启定时器，延迟更新预览图
        self.slice_update_timer.start(100)  # 300毫秒延迟，避免频繁更新
    def browse_nii_file(self):
        """浏览NIfTI文件或目录"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择NIfTI文件",
            "",
            "NIfTI Files (*.nii *.nii.gz);;All Files (*)"
        )

        if file_path:
            self.nii_file_edit.setText(file_path)
            self.load_nifti_file(file_path)

    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir_edit.setText(dir_path)

    def load_nifti_file(self, file_path):
        """加载NIfTI文件并显示信息"""
        try:
            import nibabel as nib
            self.current_nii_file = file_path
            nii = nib.load(file_path)
            self.nii_data = nii.get_fdata()

            # 更新输出目录
            if not self.output_dir_edit.text():
                input_dir = Path(file_path).parent
                output_dir = input_dir / f"{Path(file_path).stem}_swift_normal"
                self.output_dir_edit.setText(str(output_dir))

            # 更新切片范围
            self.update_slice_range()

            # 显示文件信息
            self.display_file_info(nii)

            # 生成预览
            self.generate_preview()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载NIfTI文件失败: {str(e)}")

    def update_slice_range(self):
        """更新切片范围控件"""
        if self.nii_data is not None:
            # 根据切片方向确定最大切片数
            direction = self.slice_direction_combo.currentIndex()
            max_slices = self.nii_data.shape[direction] - 1

            self.start_slice_spin.setMaximum(max_slices)
            self.end_slice_spin.setMaximum(max_slices)
            # self.end_slice_spin.setValue(max_slices)

            self.update_slice_info()

    def update_slice_info(self):
        """更新切片信息显示"""
        if self.nii_data is not None:
            direction = self.slice_direction_combo.currentIndex()
            max_slices = self.nii_data.shape[direction]
            start = self.start_slice_spin.value()
            end = min(self.end_slice_spin.value(), max_slices - 1)

            self.slice_info_label.setText(f"_slices: {max_slices}, 当前范围: {start}-{end}")

    def display_file_info(self, nii):
        """显示NIfTI文件信息"""
        try:
            import os
            from datetime import datetime

            file_path = self.current_nii_file
            file_size = os.path.getsize(file_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))

            header = nii.header
            shape = nii.shape
            dtype = header.get_data_dtype()
            affine = nii.affine

            # 计算空间分辨率
            voxel_sizes = header.get_zooms()

            info_text = f"文件大小: {self.format_file_size(file_size)}\n"
            info_text += f"修改日期: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            info_text += f"图像维度: {shape}\n"
            info_text += f"数据类型: {dtype}\n"
            info_text += f"空间分辨率: {voxel_sizes[:3] if len(voxel_sizes) >= 3 else voxel_sizes}\n"

            self.file_info_text.setText(info_text)
        except Exception as e:
            self.file_info_text.setText(f"无法读取文件信息: {str(e)}")

    def format_file_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def generate_preview(self):
        """生成预览图像"""
        if self.nii_data is None:
            return

        # 清除现有预览
        for i in reversed(range(self.preview_layout.count())):
            widget = self.preview_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            import numpy as np

            direction = self.slice_direction_combo.currentIndex()
            max_slices = self.nii_data.shape[direction]
            start = self.start_slice_spin.value()
            end = min(self.end_slice_spin.value(), max_slices - 1)

            # 选择5个代表性切片
            indices = np.linspace(start, end, 5, dtype=int)

            for idx in indices:
                # 提取切片
                if direction == 0:  # Sagittal
                    slice_data = self.nii_data[idx, :, :]
                elif direction == 1:  # Coronal
                    slice_data = self.nii_data[:, idx, :]
                else:  # Axial
                    slice_data = self.nii_data[:, :, idx]

                # 创建图像
                fig = plt.Figure(figsize=(2, 2), dpi=100)
                ax = fig.add_subplot(111)
                ax.imshow(slice_data, cmap='gray')
                ax.set_title(f"Slice {idx}")
                ax.axis('off')

                canvas = FigureCanvas(fig)
                canvas.setToolTip(f"切片索引: {idx}")

                # 添加右键菜单功能
                canvas.setContextMenuPolicy(Qt.CustomContextMenu)
                canvas.customContextMenuRequested.connect(
                    lambda pos, c=canvas, index=idx, dir_=direction:
                    self.show_slice_context_menu(pos, c, index, dir_)
                )
                self.preview_layout.addWidget(canvas)

            plt.close('all')

        except Exception as e:
            error_label = QLabel(f"预览生成失败: {str(e)}")
            self.preview_layout.addWidget(error_label)

    def show_slice_context_menu(self, pos, canvas, slice_index, direction):
        """显示切片右键菜单"""
        context_menu = QMenu(self)

        # 添加放大操作
        zoom_action = QAction("🔍 放大查看", self)
        zoom_action.triggered.connect(
            lambda: self.show_slice_detail(slice_index, direction)
        )
        context_menu.addAction(zoom_action)

        context_menu.exec(canvas.mapToGlobal(pos))

    def show_slice_detail(self, slice_index, direction):
        """显示切片详细信息弹窗"""
        dialog = SliceDetailDialog(self.nii_data, slice_index, direction, self)
        dialog.exec()

    def update_slice_preview(self):
        """更新切片预览图"""
        if not self.slice_range_changed:
            return
        # 重置标志位
        self.slice_range_changed = False
        # 更新切片信息显示
        self.update_slice_info()
        # 重新生成预览图
        if hasattr(self, 'current_nii_file') and self.current_nii_file:
            self.generate_preview()
    def convert_nifti(self):
        """执行NIfTI转换"""
        if not self.current_nii_file:
            QMessageBox.warning(self, "警告", "请先选择NIfTI文件")
            return

        output_dir = self.output_dir_edit.text()
        if not output_dir:
            QMessageBox.warning(self, "警告", "请设置输出目录")
            return

        try:
            import nibabel as nib
            import numpy as np
            from PIL import Image
            import os

            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)

            # 加载NIfTI文件
            nii = nib.load(self.current_nii_file)
            data = nii.get_fdata()

            direction = self.slice_direction_combo.currentIndex()
            start = self.start_slice_spin.value()
            end = min(self.end_slice_spin.value(), data.shape[direction] - 1)

            # 转换切片
            progress = QProgressDialog("正在转换...", "取消", 0, end - start + 1, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            count = 0
            for i in range(start, end + 1):
                if progress.wasCanceled():
                    break

                # 提取切片
                if direction == 0:  # Sagittal
                    slice_data = data[i, :, :]
                elif direction == 1:  # Coronal
                    slice_data = data[:, i, :]
                else:  # Axial
                    slice_data = data[:, :, i]

                # 标准化到0-255
                slice_data = ((slice_data - slice_data.min()) /
                              (slice_data.max() - slice_data.min()) * 255).astype(np.uint8)

                # 保存为PNG
                img = Image.fromarray(slice_data)
                img.save(os.path.join(output_dir, f"slice_{i:04d}.png"))

                count += 1
                progress.setValue(count)

            progress.close()
            QMessageBox.information(self, "成功", f"转换完成！共保存 {count} 张切片到:\n{output_dir}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"转换失败: {str(e)}")

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
            # self.update_button_states()
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
            f.write("🎯 基于YOLO的脑部肿瘤检测系统 - 批量检测报告\n")
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

    def clear_display(self, lable):
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
        self.max_frames_per_file = fps * 60 * 60 * 24  # 24小时的视频

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
    app.setApplicationName("基于YOLO的脑部肿瘤检测系统")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("AI Vision Lab")

    # 设置高DPI缩放
    # app.setAttribute(Qt.AA_EnableHighDpiScaling)
    # app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # 创建主窗口
    window = EnhancedDetectionUI()
    window.show()

    # 启动消息
    window.log_message("🚀 基于YOLO的脑部肿瘤检测系统 已启动")
    window.log_message("✨ 新功能: 渐变UI、多摄像头支持、实时监控、增强日志等")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()