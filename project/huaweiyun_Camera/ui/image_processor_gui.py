import sys
import os
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QGridLayout, QLabel, QLineEdit, QPushButton, QGroupBox,
                               QSpinBox, QProgressBar, QTextEdit, QFileDialog, QTabWidget,
                               QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
                               QCheckBox, QListWidget, QSizePolicy, QSlider)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QRect
from PySide6.QtGui import QFont, QPixmap, QPainter


class ImageComparisonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gt_pixmap = None  # 真值图
        self.pred_pixmap = None  # 处理图
        self.split_ratio = 0.5  # 分割比例，默认在中间
        self.setMinimumSize(400, 300)

    def set_images(self, gt_image_path, pred_image_path):
        """设置要对比的两张图片"""
        if gt_image_path:
            self.gt_pixmap = QPixmap(gt_image_path)
        if pred_image_path:
            self.pred_pixmap = QPixmap(pred_image_path)
        self.update()

    def set_split_ratio(self, ratio):
        """设置分割比例 (0.0 - 1.0)"""
        self.split_ratio = max(0.0, min(1.0, ratio))
        self.update()

    def paintEvent(self, event):
        """绘制图像对比效果"""
        if not self.gt_pixmap or not self.pred_pixmap:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 获取控件尺寸
        widget_width = self.width()
        widget_height = self.height()

        # 计算分割点
        split_x = int(widget_width * self.split_ratio)

        # 缩放图像以适应控件大小
        gt_scaled = self.gt_pixmap.scaled(widget_width, widget_height,
                                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pred_scaled = self.pred_pixmap.scaled(widget_width, widget_height,
                                              Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 计算居中位置
        gt_x = (widget_width - gt_scaled.width()) // 2
        gt_y = (widget_height - gt_scaled.height()) // 2

        # 绘制真值图(左侧)
        if split_x > gt_x:
            source_rect = QRect(0, 0,
                                min(split_x - gt_x, gt_scaled.width()),
                                gt_scaled.height())
            target_rect = QRect(gt_x, gt_y,
                                min(split_x - gt_x, gt_scaled.width()),
                                gt_scaled.height())
            painter.drawPixmap(target_rect, gt_scaled, source_rect)

        # 绘制处理图(右侧)
        pred_start_x = max(split_x, gt_x)
        pred_width = min(gt_scaled.width() - (pred_start_x - gt_x),
                         gt_scaled.width())
        if pred_width > 0:
            source_rect = QRect(pred_start_x - gt_x, 0,
                                pred_width, gt_scaled.height())
            target_rect = QRect(pred_start_x, gt_y,
                                pred_width, gt_scaled.height())
            painter.drawPixmap(target_rect, pred_scaled, source_rect)

        # 绘制分割线
        painter.setPen(Qt.red)
        painter.drawLine(split_x, 0, split_x, widget_height)

        # 绘制分割线手柄（圆形）
        painter.setBrush(Qt.red)
        painter.drawEllipse(split_x - 5, widget_height // 2 - 10, 10, 20)

# ======================
# StyleManager
# ======================
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
                padding: 3px 7px;
                font-size: 8px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                color: white;
                min-width: 40px;
                min-height: 20px;
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

            QSpinBox {
                padding: 6px 10px;
                border: 2px solid rgba(189, 195, 199, 0.5);
                border-radius: 6px;
                background: white;
                min-width: 80px;
                font-size: 12px;
            }

            QProgressBar {
                border: 2px solid rgba(189, 195, 199, 0.5);
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 11px;
                max-height: 15px;
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
                font-size: 10px;
                padding: 6px;
                selection-background-color: #3498db;
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
                padding: 8px 15px;
                margin-right: 3px;
                font-weight: bold;
                font-size: 10px;
                color: #2c3e50;
            }

            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border-color: rgba(52, 152, 219, 0.7);
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


# ======================
# 图像处理核心类
# ======================

def validate_block_size(img_h: int, img_w: int, block_h: int, block_w: int) -> bool:
    return img_h % block_h == 0 and img_w % block_w == 0


def split_image(image: np.ndarray, block_h: int, block_w: int) -> List[np.ndarray]:
    h, w = image.shape[:2]
    blocks = []
    for y in range(0, h, block_h):
        for x in range(0, w, block_w):
            block = image[y:y + block_h, x:x + block_w]
            blocks.append((y // block_h, x // block_w, block))
    return blocks


def save_blocks(blocks: List[Tuple[int, int, np.ndarray]], output_dir: str, base_name: str):
    os.makedirs(output_dir, exist_ok=True)
    for idx_y, idx_x, block in blocks:
        fname = f"{base_name}_{idx_y:02d}_{idx_x:02d}.jpg"
        path = os.path.join(output_dir, fname)
        cv2.imwrite(path, block)


def load_blocks(block_dir: str, base_name: str) -> Dict[Tuple[int, int], np.ndarray]:
    blocks = {}
    import glob
    
    # 查找所有可能匹配的文件
    image_extensions = [".png", ".jpg", ".jpeg", ".bmp"]
    for ext in image_extensions:
        # 查找所有匹配的文件
        pattern = os.path.join(block_dir, f"*{ext}")
        for f in glob.glob(pattern):
            fname = os.path.basename(f)
            parts = fname.split('_')
            
            if len(parts) >= 3:
                try:
                    # 特殊处理 0_00_00_upscayl_1x_high-fidelity-4x.jpg 格式
                    if len(parts) >= 3:
                        # 检查是否符合 数字_数字_数字... 模式
                        int(parts[0])  # 第一部分
                        int(parts[1])  # 第二部分
                        int(parts[2].split('.')[0])  # 第三部分
                        
                        # 如果基础名称匹配
                        if parts[0] == base_name:
                            idx_y = int(parts[1])
                            idx_x = int(parts[2].split('.')[0])
                            block = cv2.imread(f)
                            if block is not None:
                                blocks[(idx_y, idx_x)] = block
                                continue  # 处理完就跳过下面的逻辑
                    
                    # 处理其他命名模式
                    # 检查是否符合 base_y_x 或 base_y_x_suffix 模式
                    int(parts[-3])  # yy
                    int(parts[-2].split('.')[0])  # xx（可能带有扩展名）
                    
                    # 检查base_name是否匹配
                    base_from_file = '_'.join(parts[:-3]) if len(parts) > 3 else parts[0]
                    if base_from_file == base_name:
                        idx_y = int(parts[-3])
                        idx_x = int(parts[-2].split('.')[0])
                        block = cv2.imread(f)
                        if block is not None:
                            blocks[(idx_y, idx_x)] = block
                except (ValueError, IndexError):
                    # 无法解析为有效的索引格式，跳过
                    continue
    return blocks


def merge_blocks(blocks: Dict[Tuple[int, int], np.ndarray], block_h: int, block_w: int) -> np.ndarray:
    if not blocks:
        return None
    idx_ys = sorted({k[0] for k in blocks.keys()})
    idx_xs = sorted({k[1] for k in blocks.keys()})
    num_y = len(idx_ys)
    num_x = len(idx_xs)
    h = num_y * block_h
    w = num_x * block_w
    merged = np.zeros((h, w, 3), dtype=np.uint8)
    for idx_y in idx_ys:
        for idx_x in idx_xs:
            block = blocks.get((idx_y, idx_x), np.zeros((block_h, block_w, 3), dtype=np.uint8))
            y_start = idx_y * block_h
            x_start = idx_x * block_w
            merged[y_start:y_start + block_h, x_start:x_start + block_w] = block
    return merged


def evaluate_images(pred_path: str, gt_path: str) -> Optional[Dict[str, float]]:
    if not os.path.exists(pred_path) or not os.path.exists(gt_path):
        return None
    pred = cv2.imread(pred_path)
    gt = cv2.imread(gt_path)
    if pred is None or gt is None:
        return None
    if pred.shape != gt.shape:
        return None
    pred_gray = cv2.cvtColor(pred, cv2.COLOR_BGR2GRAY)
    gt_gray = cv2.cvtColor(gt, cv2.COLOR_BGR2GRAY)
    p = psnr(gt, pred)
    s = ssim(gt_gray, pred_gray)
    return {"PSNR": p, "SSIM": s}


# ======================
# 后台任务线程
# ======================

class WorkerThread(QThread):
    progress_updated = Signal(int)
    log_updated = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, task_type: str, **kwargs):
        super().__init__()
        self.task_type = task_type
        self.kwargs = kwargs

    def run(self):
        try:
            if self.task_type == "split":
                self._run_split()
            elif self.task_type == "merge":
                self._run_merge()
            elif self.task_type == "evaluate":
                self._run_evaluate()
            self.finished_signal.emit(True, "操作成功完成！")
        except Exception as e:
            self.finished_signal.emit(False, f"操作失败：{str(e)}")

    def _run_split(self):
        input_dir = self.kwargs.get("input_dir")
        output_dir = self.kwargs.get("output_dir")
        block_h = self.kwargs.get("block_h", 1024)
        block_w = self.kwargs.get("block_w", 1024)

        os.makedirs(output_dir, exist_ok=True)
        image_extensions = [".png", ".jpg", ".jpeg", ".bmp"]
        image_files = []
        for ext in image_extensions:
            image_files.extend(Path(input_dir).glob(f"*{ext}"))
        image_files = sorted([f for f in image_files if f.is_file()])

        total = len(image_files)
        for i, img_path in enumerate(image_files):
            img_path = str(img_path)
            self.log_updated.emit(f"正在处理: {os.path.basename(img_path)}")
            image = cv2.imread(img_path)
            if image is None:
                self.log_updated.emit(f"警告：无法读取图像 {img_path}，跳过。")
                continue
            h, w = image.shape[:2]
            if not validate_block_size(h, w, block_h, block_w):
                self.log_updated.emit(f"错误：图像 {img_path} 尺寸 ({h},{w}) 不能被分块尺寸 ({block_h},{block_w}) 整除，跳过。")
                continue
            base_name = Path(img_path).stem
            blocks = split_image(image, block_h, block_w)
            save_blocks(blocks, output_dir, base_name)
            self.progress_updated.emit(int((i + 1) / total * 100))

        self.log_updated.emit("分块完成！")

    def _run_merge(self):
        block_dir = self.kwargs.get("block_dir")
        output_dir = self.kwargs.get("output_dir")
        block_h = self.kwargs.get("block_h", 1024)
        block_w = self.kwargs.get("block_w", 1024)

        os.makedirs(output_dir, exist_ok=True)
        image_extensions = [".png", ".jpg", ".jpeg", ".bmp"]
        base_names = set()
        all_files = []
        
        # 收集所有图像文件
        for ext in image_extensions:
            for f in Path(block_dir).glob(f"*{ext}"):
                all_files.append(f.name)
                
        # 从文件名中提取基础名称
        for fname in all_files:
            parts = fname.split('_')
            if len(parts) >= 3:
                try:
                    # 检查是否符合 0_00_00_upscayl_1x_high-fidelity-4x.jpg 模式
                    # 前三个部分应该是 数字_数字_数字...
                    int(parts[0])  # 第一部分
                    int(parts[1])  # 第二部分
                    int(parts[2].split('.')[0])  # 第三部分（可能带扩展名）
                    
                    # 对于这种模式，基础名称就是第一个数字
                    base_names.add(parts[0])
                except ValueError:
                    # 不是这种模式，尝试其他方式
                    try:
                        # 尝试解析倒数第三和第二部分为数字（索引）
                        int(parts[-3])  # yy
                        int(parts[-2].split('.')[0])  # xx（可能带有扩展名）
                        # 如果成功，base_name应该是前面的部分
                        if len(parts) > 3:
                            base = '_'.join(parts[:-3])
                        else:
                            # 最简单的情况，如 0_00_00.jpg
                            base = parts[0]
                        base_names.add(base)
                    except (ValueError, IndexError):
                        continue

        total = len(base_names)
        for i, base in enumerate(sorted(base_names)):
            self.log_updated.emit(f"正在合并: {base}")
            blocks = load_blocks(block_dir, base)
            if not blocks:
                self.log_updated.emit(f"警告：未找到 {base} 的任何分块，跳过。")
                continue
            merged = merge_blocks(blocks, block_h, block_w)
            if merged is not None:
                out_path = os.path.join(output_dir, f"{base}.jpg")
                cv2.imwrite(out_path, merged)
            self.progress_updated.emit(int((i + 1) / total * 100))

        self.log_updated.emit("整合完成！")

    def _run_evaluate(self):
        pred_dir = self.kwargs.get("pred_dir")
        gt_dir = self.kwargs.get("gt_dir")
        output_csv = self.kwargs.get("output_csv", "evaluation_results.csv")

        image_extensions = [".png", ".jpg", ".jpeg", ".bmp"]
        pred_files = {f.stem: f for ext in image_extensions for f in Path(pred_dir).glob(f"*{ext}")}
        gt_files = {f.stem: f for ext in image_extensions for f in Path(gt_dir).glob(f"*{ext}")}

        common_names = set(pred_files.keys()) & set(gt_files.keys())
        results = []

        for name in sorted(common_names):
            pred_path = str(pred_files[name])
            gt_path = str(gt_files[name])
            eval_result = evaluate_images(pred_path, gt_path)
            if eval_result:
                eval_result["Image"] = name
                results.append(eval_result)
                self.log_updated.emit(f"{name}: PSNR={eval_result['PSNR']:.2f}, SSIM={eval_result['SSIM']:.4f}")
            else:
                self.log_updated.emit(f"{name}: 评估失败（图像不存在/尺寸不一致）")

        df = pd.DataFrame(results)
        df.to_csv(output_csv, index=False)
        self.log_updated.emit(f"评估完成，结果已保存至 {output_csv}")


# ======================
# 主窗口 GUI
# ======================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图像分块与整合工具 v1.0")
        self.setGeometry(20, 50, 750, 800)
        self.setStyleSheet(StyleManager.get_main_stylesheet())

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Tab
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: 分块
        self.tab_split = self._create_split_tab()
        self.tabs.addTab(self.tab_split, "图像分块")

        # Tab 2: 整合
        self.tab_merge = self._create_merge_tab()
        self.tabs.addTab(self.tab_merge, "图像整合")

        # Tab 3: 评估
        self.tab_eval = self._create_eval_tab()
        self.tabs.addTab(self.tab_eval, "对比评估")

        # Tab 4: 单图对比
        self.tab_single_eval = self._create_single_eval_tab()
        self.tabs.addTab(self.tab_single_eval, "单图对比")

        self.setCentralWidget(central_widget)

        # Thread
        self.worker_thread = None

    # 将其替换为：
    def _create_single_eval_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group_input = QGroupBox("图像选择")
        layout_input = QGridLayout(group_input)
        layout_input.addWidget(QLabel("处理图 (预测图):"), 0, 0)
        self.single_pred_path = QLineEdit()
        self.single_pred_browse = QPushButton("浏览...")
        self.single_pred_browse.clicked.connect(lambda: self._browse_file(self.single_pred_path))
        layout_input.addWidget(self.single_pred_path, 0, 1)
        layout_input.addWidget(self.single_pred_browse, 0, 2)

        layout_input.addWidget(QLabel("真值图 (GT图):"), 1, 0)
        self.single_gt_path = QLineEdit()
        self.single_gt_browse = QPushButton("浏览...")
        self.single_gt_browse.clicked.connect(lambda: self._browse_file(self.single_gt_path))
        layout_input.addWidget(self.single_gt_path, 1, 1)
        layout_input.addWidget(self.single_gt_browse, 1, 2)

        layout.addWidget(group_input)

        # 修改对比结果显示部分
        group_result = QGroupBox("对比结果")
        layout_result = QVBoxLayout(group_result)

        # 添加图像对比控件
        self.image_comparison = ImageComparisonWidget()
        layout_result.addWidget(self.image_comparison,stretch=5)

        # 添加滑动条来控制图像分割
        self.split_slider = QSlider(Qt.Horizontal)
        self.split_slider.setMinimum(0)
        self.split_slider.setMaximum(100)
        self.split_slider.setValue(50)  # 默认在中间
        self.split_slider.valueChanged.connect(self._on_split_slider_changed)
        layout_result.addWidget(self.split_slider)

        self.single_log = QTextEdit()
        self.single_log.setMaximumHeight(60)
        layout_result.addWidget(self.single_log)
        layout.addWidget(group_result)

        self.single_eval_button = QPushButton("开始对比")
        self.single_eval_button.setStyleSheet("""
                    QPushButton {
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                color: white;
                min-width: 40px;
                min-height: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
            }
                        """)
        self.single_eval_button.clicked.connect(self._on_single_eval_clicked)
        layout.addWidget(self.single_eval_button)

        return widget

    # 在MainWindow类中添加以下方法：
    def _on_split_slider_changed(self, value):
        """处理滑动条变化事件"""
        ratio = value / 100.0
        self.image_comparison.set_split_ratio(ratio)

    # 在MainWindow类中添加文件浏览方法
    def _browse_file(self, line_edit: QLineEdit):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图像文件",
            "",
            "图像文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            line_edit.setText(file_path)

    # 在MainWindow类中添加单图对比处理方法
    def _on_single_eval_clicked(self):
        pred_path = self.single_pred_path.text()
        gt_path = self.single_gt_path.text()

        if not pred_path or not gt_path:
            QMessageBox.warning(self, "警告", "请选择处理图和真值图！")
            return

        if not os.path.exists(pred_path):
            QMessageBox.warning(self, "警告", f"处理图不存在: {pred_path}")
            return

        if not os.path.exists(gt_path):
            QMessageBox.warning(self, "警告", f"真值图不存在: {gt_path}")
            return
        # 显示图像对比
        self.image_comparison.set_images(gt_path, pred_path)
        # 执行评估
        result = evaluate_images(pred_path, gt_path)
        if result:
            # 显示结果
            self.single_log.append(f"对比完成: {os.path.basename(pred_path)} vs {os.path.basename(gt_path)}")
            self.single_log.append(f"PSNR: {result['PSNR']:.2f}")
            self.single_log.append(f"SSIM: {result['SSIM']:.4f}")
        else:
            QMessageBox.warning(self, "错误", "图像对比失败，请检查图像文件是否有效且尺寸一致！")

    def _create_split_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group_input = QGroupBox("输入设置")
        layout_input = QGridLayout(group_input)
        layout_input.addWidget(QLabel("图片文件夹:"), 0, 0)
        self.split_input_dir = QLineEdit()
        self.split_input_browse = QPushButton("浏览...")
        self.split_input_browse.clicked.connect(lambda: self._browse_folder(self.split_input_dir))
        layout_input.addWidget(self.split_input_dir, 0, 1)
        layout_input.addWidget(self.split_input_browse, 0, 2)

        layout_input.addWidget(QLabel("输出分块文件夹:"), 1, 0)
        self.split_output_dir = QLineEdit()
        self.split_output_browse = QPushButton("浏览...")
        self.split_output_browse.clicked.connect(lambda: self._browse_folder(self.split_output_dir))
        layout_input.addWidget(self.split_output_dir, 1, 1)
        layout_input.addWidget(self.split_output_browse, 1, 2)

        layout_input.addWidget(QLabel("分块宽度:"), 2, 0)
        self.split_block_w = QSpinBox()
        self.split_block_w.setRange(64, 4096)
        self.split_block_w.setValue(1024)
        layout_input.addWidget(self.split_block_w, 2, 1)

        layout_input.addWidget(QLabel("分块高度:"), 3, 0)
        self.split_block_h = QSpinBox()
        self.split_block_h.setRange(64, 4096)
        self.split_block_h.setValue(1024)
        layout_input.addWidget(self.split_block_h, 3, 1)

        layout.addWidget(group_input)

        # Progress & Log
        group_progress = QGroupBox("执行状态")
        layout_progress = QVBoxLayout(group_progress)
        self.split_progress = QProgressBar()
        self.split_log = QTextEdit()
        # self.split_log.setMaximumHeight(300)
        layout_progress.addWidget(self.split_log,stretch=4)
        layout_progress.addWidget(self.split_progress,stretch=1)
        layout.addWidget(group_progress)

        # Button
        self.split_button = QPushButton("开始分块")
        self.split_button.setStyleSheet("""
                    QPushButton {
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                color: white;
                min-width: 40px;
                min-height: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
            }
                        """)
        self.split_button.clicked.connect(self._on_split_clicked)
        layout.addWidget(self.split_button)

        return widget

    def _create_merge_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group_input = QGroupBox("输入设置")
        layout_input = QGridLayout(group_input)
        layout_input.addWidget(QLabel("分块文件夹:"), 0, 0)
        self.merge_block_dir = QLineEdit()
        self.merge_block_browse = QPushButton("浏览...")
        self.merge_block_browse.clicked.connect(lambda: self._browse_folder(self.merge_block_dir))
        layout_input.addWidget(self.merge_block_dir, 0, 1)
        layout_input.addWidget(self.merge_block_browse, 0, 2)

        layout_input.addWidget(QLabel("输出整合文件夹:"), 1, 0)
        self.merge_output_dir = QLineEdit()
        self.merge_output_browse = QPushButton("浏览...")
        self.merge_output_browse.clicked.connect(lambda: self._browse_folder(self.merge_output_dir))
        layout_input.addWidget(self.merge_output_dir, 1, 1)
        layout_input.addWidget(self.merge_output_browse, 1, 2)

        layout_input.addWidget(QLabel("分块宽度:"), 2, 0)
        self.merge_block_w = QSpinBox()
        self.merge_block_w.setRange(64, 4096)
        self.merge_block_w.setValue(1024)
        layout_input.addWidget(self.merge_block_w, 2, 1)

        layout_input.addWidget(QLabel("分块高度:"), 3, 0)
        self.merge_block_h = QSpinBox()
        self.merge_block_h.setRange(64, 4096)
        self.merge_block_h.setValue(1024)
        layout_input.addWidget(self.merge_block_h, 3, 1)

        layout.addWidget(group_input)

        group_progress = QGroupBox("执行状态")
        layout_progress = QVBoxLayout(group_progress)
        self.merge_progress = QProgressBar()
        self.merge_log = QTextEdit()
        # self.merge_log.setMaximumHeight(200)
        layout_progress.addWidget(self.merge_log,stretch=4)
        layout_progress.addWidget(self.merge_progress,stretch=1)
        layout.addWidget(group_progress)

        self.merge_button = QPushButton("开始整合")
        self.merge_button.setStyleSheet("""
                    QPushButton {
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                color: white;
                min-width: 40px;
                min-height: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
            }
                        """)
        self.merge_button.clicked.connect(self._on_merge_clicked)
        layout.addWidget(self.merge_button)

        return widget

    def _create_eval_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group_input = QGroupBox("输入设置")
        layout_input = QGridLayout(group_input)
        layout_input.addWidget(QLabel("预测图文件夹 (增图):"), 0, 0)
        self.eval_pred_dir = QLineEdit()
        self.eval_pred_browse = QPushButton("浏览...")
        self.eval_pred_browse.clicked.connect(lambda: self._browse_folder(self.eval_pred_dir))
        layout_input.addWidget(self.eval_pred_dir, 0, 1)
        layout_input.addWidget(self.eval_pred_browse, 0, 2)

        layout_input.addWidget(QLabel("GT图文件夹 (真值图):"), 1, 0)
        self.eval_gt_dir = QLineEdit()
        self.eval_gt_browse = QPushButton("浏览...")
        self.eval_gt_browse.clicked.connect(lambda: self._browse_folder(self.eval_gt_dir))
        layout_input.addWidget(self.eval_gt_dir, 1, 1)
        layout_input.addWidget(self.eval_gt_browse, 1, 2)

        layout_input.addWidget(QLabel("评估结果CSV:"), 2, 0)
        self.eval_output_csv = QLineEdit()
        self.eval_output_csv.setText("evaluation_results.csv")
        layout_input.addWidget(self.eval_output_csv, 2, 1)

        layout.addWidget(group_input)

        group_progress = QGroupBox("执行状态")
        layout_progress = QVBoxLayout(group_progress)
        self.eval_progress = QProgressBar()
        self.eval_log = QTextEdit()
        # self.eval_log.setMaximumHeight(200)
        layout_progress.addWidget(self.eval_log,stretch=4)
        layout_progress.addWidget(self.eval_progress,stretch=1)
        layout.addWidget(group_progress)

        self.eval_button = QPushButton("开始评估")
        self.eval_button.setStyleSheet("""
                    QPushButton {
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                color: white;
                min-width: 40px;
                min-height: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
            }
                        """)
        self.eval_button.clicked.connect(self._on_eval_clicked)
        layout.addWidget(self.eval_button)

        return widget

    def _browse_folder(self, line_edit: QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            line_edit.setText(folder)

    def _on_split_clicked(self):
        if self._start_task("split"):
            self.split_button.setEnabled(False)

    def _on_merge_clicked(self):
        if self._start_task("merge"):
            self.merge_button.setEnabled(False)

    def _on_eval_clicked(self):
        if self._start_task("evaluate"):
            self.eval_button.setEnabled(False)

    def _start_task(self, task_type: str):
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "警告", "请等待当前任务完成！")
            return False

        self.worker_thread = WorkerThread(task_type, **self._get_task_kwargs(task_type))
        self.worker_thread.progress_updated.connect(self._update_progress)
        self.worker_thread.log_updated.connect(self._update_log)
        self.worker_thread.finished_signal.connect(self._on_task_finished)
        self.worker_thread.start()
        return True

    def _get_task_kwargs(self, task_type: str) -> dict:
        if task_type == "split":
            return {
                "input_dir": self.split_input_dir.text(),
                "output_dir": self.split_output_dir.text(),
                "block_h": self.split_block_h.value(),
                "block_w": self.split_block_w.value(),
            }
        elif task_type == "merge":
            return {
                "block_dir": self.merge_block_dir.text(),
                "output_dir": self.merge_output_dir.text(),
                "block_h": self.merge_block_h.value(),
                "block_w": self.merge_block_w.value(),
            }
        elif task_type == "evaluate":
            return {
                "pred_dir": self.eval_pred_dir.text(),
                "gt_dir": self.eval_gt_dir.text(),
                "output_csv": self.eval_output_csv.text(),
            }
        return {}

    def _update_progress(self, value: int):
        sender = self.sender()
        if isinstance(sender, WorkerThread):
            if hasattr(self, 'split_progress') and self.sender() == self.worker_thread:
                if 'split' in self._get_current_task():
                    self.split_progress.setValue(value)
                elif 'merge' in self._get_current_task():
                    self.merge_progress.setValue(value)
                elif 'eval' in self._get_current_task():
                    self.eval_progress.setValue(value)

    def _get_current_task(self) -> str:
        # 简单启发式判断当前任务类型
        if self.worker_thread:
            if self.split_input_dir.text() and self.worker_thread.task_type == "split":
                return "split"
            elif self.merge_block_dir.text() and self.worker_thread.task_type == "merge":
                return "merge"
            elif self.eval_pred_dir.text() and self.worker_thread.task_type == "evaluate":
                return "evaluate"
        return ""

    def _update_log(self, message: str):
        self.split_log.append(message) if hasattr(self, 'split_log') else None
        self.merge_log.append(message) if hasattr(self, 'merge_log') else None
        self.eval_log.append(message) if hasattr(self, 'eval_log') else None

    def _on_task_finished(self, success: bool, message: str):
        self.split_button.setEnabled(True)
        self.merge_button.setEnabled(True)
        self.eval_button.setEnabled(True)
        self.split_progress.setValue(0)
        self.merge_progress.setValue(0)
        self.eval_progress.setValue(0)
        QMessageBox.information(self, "任务完成", message)


# ======================
# 程序入口
# ======================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())