#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图片转 PDF 工具  –  单文件 PySide6 实现
author : kimi
"""

import os
import sys
import img2pdf
from pathlib import Path
from typing import List

from PySide6.QtCore import (Qt, QThread, Signal, QMimeData, QPoint, QStandardPaths)
from PySide6.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent, QResizeEvent
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QGroupBox, QPushButton, QListWidget, QListWidgetItem, QLabel,
                               QFileDialog, QMessageBox, QProgressBar, QTextEdit, QDialog, QScrollArea, QFrame)
def resource_path(relative_path):
    """获取资源的绝对路径，支持开发和打包后两种模式"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller单文件模式下的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发模式下的相对路径
    return os.path.join(os.path.abspath("."), relative_path)
# -------------------- Style --------------------
class StyleManager:
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
            padding: 4px 6px;
            font-size: 11px;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            color: white;
            min-width: 45px;
            min-height: 32px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3498db, stop:1 #2980b9);
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5dade2, stop:1 #3498db);
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
            font-family: Consolas, Monaco, monospace;
            font-size: 11px;
            padding: 8px;
            selection-background-color: #3498db;
        }
        """

# -------------------- Model --------------------
class ImgListModel(QThread):
    """负责图片列表管理与 PDF 转换（Model）"""
    progress = Signal(int)
    finished = Signal(bool, str)

    def __init__(self):
        super().__init__()
        self.img_paths: List[str] = []
        self.output_path = ""
        self._running = True
        self.is_merge_mode = True  # 默认为合并模式
        self.mode = 'merge'  # 转换模式
        self.base_output_dir = ""  # 批量转换时的基础输出目录

    def add_images(self, paths: List[str]):
        for p in paths:
            if p not in self.img_paths:
                self.img_paths.append(p)

    def remove_index(self, index: int):
        if 0 <= index < len(self.img_paths):
            self.img_paths.pop(index)

    def clear(self):
        self.img_paths.clear()

    def move_up(self, index: int):
        if 0 < index < len(self.img_paths):
            self.img_paths[index], self.img_paths[index - 1] = self.img_paths[index - 1], self.img_paths[index]

    def move_down(self, index: int):
        if 0 <= index < len(self.img_paths) - 1:
            self.img_paths[index], self.img_paths[index + 1] = self.img_paths[index + 1], self.img_paths[index]

    def move_top(self, index: int):
        if 0 < index < len(self.img_paths):
            self.img_paths.insert(0, self.img_paths.pop(index))

    def move_bottom(self, index: int):
        if 0 <= index < len(self.img_paths) - 1:
            self.img_paths.append(self.img_paths.pop(index))

    def run(self):
        """线程执行：生成 PDF"""
        try:
            total = len(self.img_paths)
            if total == 0:
                self.finished.emit(False, "图片列表为空")
                return
                
            if self.mode == 'merge':
                # 合并转换模式：将所有图片合并为一个PDF
                if not self.output_path:
                    self.finished.emit(False, "未指定输出路径")
                    return
                    
                self.progress.emit(5)
                
                # 设置PDF页面选项以保持一致的页面尺寸
                a4_width = 595  # A4 width in points
                a4_height = 842 # A4 height in points
                
                layout_fun = img2pdf.get_layout_fun((a4_width, a4_height))
                
                with open(self.output_path, "wb") as f:
                    f.write(img2pdf.convert(self.img_paths, layout_fun=layout_fun))
                    
                self.progress.emit(100)
                self.finished.emit(True, self.output_path)
            elif self.mode == 'batch':
                # 批量单页转换模式：每张图片单独转换为一个PDF文件
                self.progress.emit(5)
                
                # 设置PDF页面选项以保持一致的页面尺寸
                a4_width = 595  # A4 width in points
                a4_height = 842 # A4 height in points
                
                layout_fun = img2pdf.get_layout_fun((a4_width, a4_height))
                
                success_count = 0
                for idx, img_path in enumerate(self.img_paths):
                    if not self._running:
                        self.finished.emit(False, "用户取消")
                        return
                    
                    # 为每张图片创建单独的PDF文件，使用原图片名
                    img_dir = os.path.dirname(img_path)
                    img_base_name = os.path.splitext(os.path.basename(img_path))[0]
                    output_pdf_path = os.path.join(img_dir, f"{img_base_name}.pdf")
                    
                    # 检查文件是否已存在，如果存在则添加数字后缀
                    counter = 0
                    original_output_path = output_pdf_path
                    while os.path.exists(output_pdf_path):
                        name_part = os.path.splitext(original_output_path)[0]
                        ext_part = os.path.splitext(original_output_path)[1]
                        output_pdf_path = f"{name_part}_{counter}{ext_part}"
                        counter += 1
                    
                    # 转换单张图片为PDF
                    with open(output_pdf_path, "wb") as f:
                        f.write(img2pdf.convert(img_path, layout_fun=layout_fun))
                    
                    success_count += 1
                    self.progress.emit(int((idx + 1) / total * 90))
                
                self.progress.emit(100)
                self.finished.emit(True, f"批量转换完成，共转换 {success_count} 个PDF文件")
        except Exception as e:
            self.finished.emit(False, str(e))

    def stop(self):
        self._running = False

# -------------------- View --------------------
class MainView(QMainWindow):
    """纯 UI 布局（View）"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片转 PDF 工具")
        self.resize(750, 650)
        self.setAcceptDrops(True)
        self._central = QWidget()
        self.setCentralWidget(self._central)
        self._setup_ui()
        self.setStyleSheet(StyleManager.get_main_stylesheet())

    def _setup_ui(self):
        main_lo = QHBoxLayout(self._central)

        # 左侧：图片列表
        left_gb = QGroupBox("图片列表")
        self.list_w = QListWidget()
        # 绑定双击事件
        self.list_w.itemDoubleClicked.connect(self._on_item_double_clicked)
        left_btn_lo = QHBoxLayout()
        self.add_btn = QPushButton("添加图片")
        self.del_btn = QPushButton("移除选中")
        self.clear_btn = QPushButton("清空列表")
        left_btn_lo.addWidget(self.add_btn)
        left_btn_lo.addWidget(self.del_btn)
        left_btn_lo.addWidget(self.clear_btn)
        left_lo = QVBoxLayout(left_gb)
        left_lo.addWidget(self.list_w)
        left_lo.addLayout(left_btn_lo)

        # 右侧：顺序调整 + 预览/状态
        right_gb = QGroupBox("操作与状态")
        order_lo = QHBoxLayout()
        self.up_btn = QPushButton("上移")
        self.down_btn = QPushButton("下移")
        self.top_btn = QPushButton("置顶")
        self.bottom_btn = QPushButton("置底")
        for btn in (self.up_btn, self.down_btn, self.top_btn, self.bottom_btn):
            order_lo.addWidget(btn)

        self.save_path_le = QTextEdit()
        self.save_path_le.setFixedHeight(60)
        self.save_path_le.setPlaceholderText("点击“选择保存路径”设置输出文件")
        self.choose_save_btn = QPushButton("选择保存路径")
        
        # 新增：两个转换按钮和操作详情标签
        self.merge_convert_btn = QPushButton("合并转换")
        self.batch_convert_btn = QPushButton("批量单页转换")
        
        # 操作详情标签
        self.operation_info_label = QLabel()
        self.operation_info_label.setWordWrap(True)
        self.operation_info_label.setStyleSheet("""
            QLabel {
                background-color: #f0f8ff;
                border: 1px solid #d0e0f0;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                color: #333;
            }
        """)
        self.operation_info_label.setText("请选择转换模式：\n• 合并转换：将所有图片合并为一个PDF文件，每张图片为一页\n• 批量单页转换：每张图片单独转换为一个PDF文件")
        
        self.open_dir_btn = QPushButton("打开目录")
        self.open_dir_btn.setEnabled(False)

        self.bar = QProgressBar()
        self.bar.setTextVisible(True)
        self.status_te = QTextEdit()
        self.status_te.setReadOnly(True)

        right_lo = QVBoxLayout(right_gb)
        right_lo.addLayout(order_lo)
        right_lo.addWidget(self.choose_save_btn)
        right_lo.addWidget(self.save_path_le)
        right_lo.addWidget(self.merge_convert_btn)
        right_lo.addWidget(self.batch_convert_btn)
        right_lo.addWidget(self.operation_info_label)
        right_lo.addWidget(self.open_dir_btn)
        right_lo.addWidget(self.bar)
        right_lo.addWidget(self.status_te)

        main_lo.addWidget(left_gb, 2)
        main_lo.addWidget(right_gb, 1)
    
    def _on_item_double_clicked(self, item):
        """处理列表项双击事件"""
        image_path = item.data(Qt.UserRole)
        if image_path and os.path.exists(image_path):
            preview_dialog = ImagePreviewDialog(image_path, self)
            preview_dialog.exec()

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e: QDropEvent):
        files = [u.toLocalFile() for u in e.mimeData().urls()]
        self.controller.handle_drop_files(files)

    def set_controller(self, c):
        self.controller = c

# -------------------- Controller --------------------
class Controller:
    """业务逻辑与信号绑定"""
    def __init__(self, view: MainView, model: ImgListModel):
        self.v = view
        self.m = model
        self._connect()
        self._working = False

    def _connect(self):
        self.v.add_btn.clicked.connect(self.add_images)
        self.v.del_btn.clicked.connect(self.remove_selected)
        self.v.clear_btn.clicked.connect(self.clear_list)
        self.v.up_btn.clicked.connect(lambda: self.move(-1))
        self.v.down_btn.clicked.connect(lambda: self.move(1))
        self.v.top_btn.clicked.connect(lambda: self.move_top())
        self.v.bottom_btn.clicked.connect(lambda: self.move_bottom())
        self.v.choose_save_btn.clicked.connect(self.choose_save)
        self.v.merge_convert_btn.clicked.connect(lambda: self.convert(mode='merge'))
        self.v.batch_convert_btn.clicked.connect(lambda: self.convert(mode='batch'))
        self.v.open_dir_btn.clicked.connect(self.open_dir)
        self.m.progress.connect(self.v.bar.setValue)
        self.m.finished.connect(self.on_finished)

    def handle_drop_files(self, files: List[str]):
        good = [f for f in files if self._is_img(f)]
        if good:
            self.m.add_images(good)
            self.refresh_list()
        else:
            QMessageBox.warning(self.v, "提示", "拖拽的文件中没有支持的图片格式")

    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self.v, "选择图片", "",
            "Images (*.jpg *.jpeg *.png *.bmp *.gif *.JPG *.JPEG *.PNG *.BMP *.GIF)")
        if files:
            self.m.add_images(files)
            self.refresh_list()

    def remove_selected(self):
        row = self.v.list_w.currentRow()
        if row >= 0:
            self.m.remove_index(row)
            self.refresh_list()

    def clear_list(self):
        self.m.clear()
        self.refresh_list()

    def move(self, direction: int):
        row = self.v.list_w.currentRow()
        if direction == -1:
            self.m.move_up(row)
        else:
            self.m.move_down(row)
        self.refresh_list()
        self.v.list_w.setCurrentRow(row + direction)

    def move_top(self):
        row = self.v.list_w.currentRow()
        self.m.move_top(row)
        self.refresh_list()
        self.v.list_w.setCurrentRow(0)

    def move_bottom(self):
        row = self.v.list_w.currentRow()
        self.m.move_bottom(row)
        self.refresh_list()
        self.v.list_w.setCurrentRow(len(self.m.img_paths) - 1)

    def choose_save(self):
        if self.m.img_paths:
            # 如果有图片，将默认保存位置设为第一张图片的目录
            first_img_dir = os.path.dirname(self.m.img_paths[0])
            default_path = os.path.join(first_img_dir, "output.pdf")
        else:
            # 如果没有图片，使用文档目录
            default_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) + "/output.pdf"
        
        path, _ = QFileDialog.getSaveFileName(
            self.v, "保存 PDF 文件", default_path, "PDF Files (*.pdf)")
        if path:
            self.m.output_path = path
            self.v.save_path_le.setText(path)

    def convert(self, mode='merge'):
        if not self.m.img_paths:
            QMessageBox.information(self.v, "提示", "请先添加图片")
            return
        
        if mode == 'merge':
            # 合并转换模式：将所有图片合并为一个PDF文件
            if not self.m.output_path:
                if self.m.img_paths:
                    # 获取第一张图片的目录
                    img_dir = os.path.dirname(self.m.img_paths[0])
                    
                    # 查找已存在的output_*文件，找到最大的编号
                    existing_outputs = []
                    for filename in os.listdir(img_dir):
                        if filename.startswith("output_") and filename.endswith(".pdf"):
                            try:
                                # 提取数字部分
                                name_part = filename[len("output_"):-len(".pdf")]  # 去掉前缀和后缀
                                if name_part.isdigit():  # 确保是数字
                                    existing_outputs.append(int(name_part))
                            except:
                                continue  # 忽略无法解析的文件名
                    
                    # 找到下一个可用编号
                    if existing_outputs:
                        next_counter = max(existing_outputs) + 1
                    else:
                        next_counter = 0
                    
                    # 生成新的文件名
                    filename = f"output_{next_counter}.pdf"
                    self.m.output_path = os.path.join(img_dir, filename)
                    
                    self.v.save_path_le.setText(self.m.output_path)
            else:
                # 检查用户是否编辑了路径框中的内容
                user_input_path = self.v.save_path_le.toPlainText().strip()
                if user_input_path and user_input_path != self.m.output_path:
                    # 用户编辑了路径，使用用户指定的路径
                    self.m.output_path = user_input_path
                else:
                    # 用户未编辑路径框，但已有输出路径，检查是否为output_*格式
                    output_filename = os.path.basename(self.m.output_path)
                    if output_filename.startswith("output_") and output_filename.endswith(".pdf"):
                        # 提取文件名中的数字部分
                        name_part = output_filename[len("output_"):-len(".pdf")]
                        if name_part.isdigit():
                            output_dir = os.path.dirname(self.m.output_path)
                            # 查找已存在的output_*文件，找到最大的编号
                            existing_outputs = []
                            for filename in os.listdir(output_dir):
                                if filename.startswith("output_") and filename.endswith(".pdf"):
                                    try:
                                        # 提取数字部分
                                        existing_name_part = filename[len("output_"):-len(".pdf")]  # 去掉前缀和后缀
                                        if existing_name_part.isdigit():  # 确保是数字
                                            existing_outputs.append(int(existing_name_part))
                                    except:
                                        continue  # 忽略无法解析的文件名
                            
                            # 找到下一个可用编号
                            if existing_outputs:
                                next_counter = max(existing_outputs) + 1
                            else:
                                next_counter = 0
                            
                            # 生成新的文件名
                            filename = f"output_{next_counter}.pdf"
                            self.m.output_path = os.path.join(output_dir, filename)
                            
                            self.v.save_path_le.setText(self.m.output_path)
            
            # 设置合并转换的标志
            self.m.is_merge_mode = True
            
        elif mode == 'batch':
            # 批量单页转换模式：每张图片单独转换为一个PDF文件
            # 在这种模式下，我们不需要设置全局的output_path，而是使用图片所在目录
            if self.m.img_paths:
                # 获取第一张图片的目录作为基础目录
                base_dir = os.path.dirname(self.m.img_paths[0])
                self.m.base_output_dir = base_dir
            self.m.is_merge_mode = False
            # 清空output_path，因为批量转换不需要全局输出路径
            self.m.output_path = ""
        
        self._set_widgets_enabled(False)
        self.v.bar.setValue(0)
        if mode == 'merge':
            self.v.status_te.append("开始合并转换...")
        else:
            self.v.status_te.append("开始批量单页转换...")
        self.m.mode = mode
        self.m.start()

    def on_finished(self, ok: bool, msg: str):
        self._set_widgets_enabled(True)
        self.v.bar.setValue(0)
        if ok:
            self.v.status_te.append(f"转换成功：{msg}")
            self.v.open_dir_btn.setEnabled(True)
            QMessageBox.information(self.v, "完成", "PDF 已生成！")
        else:
            self.v.status_te.append(f"转换失败：{msg}")
            QMessageBox.critical(self.v, "错误", msg)

    def open_dir(self):
        if self.m.output_path and os.path.exists(self.m.output_path):
            QApplication.platform().openUrl(self.m.output_path)

    def refresh_list(self):
        self.v.list_w.clear()
        for p in self.m.img_paths:
            item = QListWidgetItem(os.path.basename(p))
            item.setData(Qt.UserRole, p)
            self.v.list_w.addItem(item)

    def _set_widgets_enabled(self, enabled: bool):
        for w in (self.v.add_btn, self.v.del_btn, self.v.clear_btn,
                  self.v.up_btn, self.v.down_btn, self.v.top_btn, self.v.bottom_btn,
                  self.v.choose_save_btn, self.v.merge_convert_btn, self.v.batch_convert_btn):
            w.setEnabled(enabled)

    @staticmethod
    def _is_img(path: str) -> bool:
        return path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))

# -------------------- Image Preview Dialog --------------------
class ImagePreviewDialog(QDialog):
    """图片预览对话框"""
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle(f"图片预览 - {os.path.basename(image_path)}")
        self.resize(900, 700)
        
        # 初始化缩放级别
        self.scale_factor = 1.0
        
        # 创建滚动区域以支持大图片
        self.scroll_area = QScrollArea()
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setWidgetResizable(True)
        
        # 启用鼠标追踪以支持缩放
        self.label.setMouseTracking(True)
        
        # 加载并显示图片
        self.original_pixmap = QPixmap(image_path)
        
        # 根据图片大小和窗口大小计算初始缩放比例，确保整个图片可见
        self._calculate_initial_scale()
        
        self.current_pixmap = self.original_pixmap.scaled(
            self._get_scaled_size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.label.setPixmap(self.current_pixmap)
        
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)
        
    def _calculate_initial_scale(self):
        """根据图片大小和窗口大小计算初始缩放比例"""
        if self.original_pixmap.isNull():
            return
        
        # 获取滚动区域的大小（可视区域）
        scroll_size = self.scroll_area.viewport().size()
        
        # 为边距留出一些空间
        available_width = scroll_size.width() - 10
        available_height = scroll_size.height() - 10
        
        # 计算缩放比例，确保图片完全适应窗口
        pixmap_size = self.original_pixmap.size()
        
        if pixmap_size.width() > available_width or pixmap_size.height() > available_height:
            # 需要缩小
            width_ratio = available_width / pixmap_size.width()
            height_ratio = available_height / pixmap_size.height()
            self.scale_factor = min(width_ratio, height_ratio)
        else:
            # 图片小于窗口，可以按原尺寸显示
            self.scale_factor = 1.0
    
    def _get_scaled_size(self):
        """获取当前缩放后的图片尺寸"""
        return self.original_pixmap.size() * self.scale_factor
        
    def wheelEvent(self, event):
        # 检测是否按下Ctrl键来进行缩放
        if event.modifiers() & Qt.ControlModifier:
            # 计算缩放因子
            if event.angleDelta().y() > 0:
                # 向上滚动，放大 (每次放大20%)
                self.scale_factor *= 1.2
            else:
                # 向下滚动，缩小 (每次缩小20%)
                self.scale_factor /= 1.2
            
            # 限制缩放范围
            self.scale_factor = max(0.1, min(self.scale_factor, 10.0))
            
            # 重新缩放图片
            self._update_image()
        else:
            # 如果没有按Ctrl，执行正常的滚动事件
            super().wheelEvent(event)
    
    def _update_image(self):
        """更新图片显示"""
        new_size = self._get_scaled_size()
        self.current_pixmap = self.original_pixmap.scaled(
            new_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.label.setPixmap(self.current_pixmap)
        
    def keyPressEvent(self, event):
        # 支持按键快捷操作
        if event.key() == Qt.Key_Control:
            self.setCursor(Qt.OpenHandCursor)
        super().keyPressEvent(event)
        
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.unsetCursor()
        super().keyReleaseEvent(event)
        
    def resizeEvent(self, event):
        """窗口大小改变时重新计算缩放"""
        super().resizeEvent(event)
        # 重新计算缩放比例
        self._calculate_initial_scale()
        # 更新图片显示
        self._update_image()

# -------------------- main --------------------
def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon.fromTheme("image-x-generic"))
    view = MainView()
    view.setWindowIcon(QIcon(resource_path("app.ico")))
    model = ImgListModel()
    ctrl = Controller(view, model)
    view.set_controller(ctrl)
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()