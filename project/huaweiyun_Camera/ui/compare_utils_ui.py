import sys
import os
from pathlib import Path
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFileDialog,
                               QFrame, QGridLayout, QGroupBox, QFormLayout, QLineEdit)
from PySide6.QtCore import Qt, QRect, QPoint, QSize
from PySide6.QtGui import QPixmap, QPainter, QPen, QFont, QImage


class ImageCompareWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(1289, 515)  # 1280+9, 512+3
        self.setStyleSheet("background-color: white; border: 1px solid gray;")

        # 存储图像数据
        self.images = {
            'input': None,
            'baseline': None,
            'ours': None,
            'gt': None
        }

        # 放大区域坐标 (x, y, width, height)
        self.zoom_rect1 = QRect(100, 100, 128, 128)  # 第一行放大区域
        self.zoom_rect2 = QRect(300, 300, 128, 128)  # 第二行放大区域

    def load_images(self, image_paths):
        """加载图像"""
        for key, path in image_paths.items():
            if path and os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self.images[key] = pixmap.scaled(512, 512,
                                                     Qt.KeepAspectRatio,
                                                     Qt.SmoothTransformation)
                else:
                    self.images[key] = None
            else:
                self.images[key] = None

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制主图像区域 (512x512)
        if self.images['input'] is not None:
            # 绘制input图像
            painter.drawPixmap(0, 0, self.images['input'])

            # 绘制红色矩形框标注放大区域
            pen = QPen(Qt.red, 3)
            painter.setPen(pen)
            painter.drawRect(self.zoom_rect1)

            pen = QPen(Qt.red, 3)
            painter.setPen(pen)
            painter.drawRect(self.zoom_rect2)

        # 计算右侧面板位置 (考虑到间距)
        right_panel_x = 512 + 3

        # 右侧两行，每行三张局部放大图
        # 第一行位置 (baseline, ours, gt)
        row1_y = 0
        # 第二行位置 (baseline, ours, gt)
        row2_y = 256 + 3

        # 每张放大图的宽度
        zoom_width = 256
        zoom_height = 256

        # 第一行坐标 (baseline, ours, gt)
        zoom_positions_row1 = [
            (right_panel_x, row1_y),  # baseline
            (right_panel_x + zoom_width + 3, row1_y),  # ours
            (right_panel_x + 2 * (zoom_width + 3), row1_y)  # gt
        ]

        # 第二行坐标 (baseline, ours, gt)
        zoom_positions_row2 = [
            (right_panel_x, row2_y),  # baseline
            (right_panel_x + zoom_width + 3, row2_y),  # ours
            (right_panel_x + 2 * (zoom_width + 3), row2_y)  # gt
        ]

        # 绘制第一行局部放大图 (使用第一个放大区域)
        zoom_keys = ['baseline', 'ours', 'gt']
        for i, (key, pos) in enumerate(zip(zoom_keys, zoom_positions_row1)):
            if self.images[key] is not None:
                # 提取局部区域并放大
                scaled_pixmap = self.get_zoomed_pixmap(self.images[key], self.zoom_rect1)
                painter.drawPixmap(pos[0], pos[1], zoom_width, zoom_height, scaled_pixmap)

                # 绘制边框
                pen = QPen(Qt.black, 1)
                painter.setPen(pen)
                painter.drawRect(pos[0], pos[1], zoom_width, zoom_height)

                # 绘制标签 (左上方)
                font = QFont()
                font.setPointSize(16)
                font.setBold(True)
                painter.setFont(font)
                painter.setPen(Qt.white)
                label = key.capitalize()
                painter.drawText(pos[0] + 5, pos[1] + 26, label)

        # 绘制第二行局部放大图 (使用第二个放大区域)
        for i, (key, pos) in enumerate(zip(zoom_keys, zoom_positions_row2)):
            if self.images[key] is not None:
                # 提取局部区域并放大
                scaled_pixmap = self.get_zoomed_pixmap(self.images[key], self.zoom_rect2)
                painter.drawPixmap(pos[0], pos[1], zoom_width, zoom_height, scaled_pixmap)

                # 绘制边框
                pen = QPen(Qt.black, 1)
                painter.setPen(pen)
                painter.drawRect(pos[0], pos[1], zoom_width, zoom_height)

                # 绘制标签 (左上方)
                font = QFont()
                font.setPointSize(16)
                font.setBold(True)
                painter.setFont(font)
                painter.setPen(Qt.white)
                label = key.capitalize()
                painter.drawText(pos[0] + 5, pos[1] + 26, label)

        # 绘制左侧大图标签
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(Qt.white)
        painter.drawText(10, 30, "Input")

    def get_zoomed_pixmap(self, original_pixmap, rect):
        """获取放大的局部图像"""
        if original_pixmap is None:
            return QPixmap(256, 256)

        # 从原图中裁剪区域
        cropped = original_pixmap.copy(rect)
        # 放大到256x256
        return cropped.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def set_zoom_rects(self, rect1, rect2):
        """设置两个放大区域"""
        self.zoom_rect1 = rect1
        self.zoom_rect2 = rect2
        self.update()


class MainWindow(QMainWindow):
    # 在 MainWindow.__init__ 方法中添加按钮
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图像对比展示工具 - 人工路径设定版")
        self.setGeometry(100, 100, 1500, 800)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 图像显示区域
        self.image_compare_widget = ImageCompareWidget()
        main_layout.addWidget(self.image_compare_widget)

        # 路径输入区域
        path_group = QGroupBox("图像路径设置")
        path_layout = QFormLayout()

        self.input_path_edit = QLineEdit()
        self.input_path_edit.setText('H:/data/huaweiyun/one/latest/evaluation/input-fenkuai_mini/1_02_01.jpg')
        self.baseline_path_edit = QLineEdit()
        self.baseline_path_edit.setText('H:/data/huaweiyun/one/latest/evaluation/input-fenkuai_mini_4xHFA2k_output_resize/1_02_01.jpg')
        self.ours_path_edit = QLineEdit()
        self.ours_path_edit.setText('H:/data/huaweiyun/one/latest/evaluation/ours_output/1_02_01.jpg')
        self.gt_path_edit = QLineEdit()
        self.gt_path_edit.setText('H:/data/huaweiyun/one/latest/evaluation/gt_fenkuai_mini/1_02_01.jpg')

        # 浏览按钮
        input_browse_btn = QPushButton("浏览...")
        baseline_browse_btn = QPushButton("浏览...")
        ours_browse_btn = QPushButton("浏览...")
        gt_browse_btn = QPushButton("浏览...")

        input_browse_btn.clicked.connect(lambda: self.browse_image('input'))
        baseline_browse_btn.clicked.connect(lambda: self.browse_image('baseline'))
        ours_browse_btn.clicked.connect(lambda: self.browse_image('ours'))
        gt_browse_btn.clicked.connect(lambda: self.browse_image('gt'))

        # 路径输入行
        # 路径输入行
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_path_edit)
        input_layout.addWidget(input_browse_btn)
        prev_btn = QPushButton("上一张")
        next_btn = QPushButton("下一张")
        prev_btn.clicked.connect(lambda: self.switch_image('input', -1))
        next_btn.clicked.connect(lambda: self.switch_image('input', 1))
        input_layout.addWidget(prev_btn)
        input_layout.addWidget(next_btn)

        baseline_layout = QHBoxLayout()
        baseline_layout.addWidget(self.baseline_path_edit)
        baseline_layout.addWidget(baseline_browse_btn)
        prev_btn = QPushButton("上一张")
        next_btn = QPushButton("下一张")
        prev_btn.clicked.connect(lambda: self.switch_image('baseline', -1))
        next_btn.clicked.connect(lambda: self.switch_image('baseline', 1))
        baseline_layout.addWidget(prev_btn)
        baseline_layout.addWidget(next_btn)

        ours_layout = QHBoxLayout()
        ours_layout.addWidget(self.ours_path_edit)
        ours_layout.addWidget(ours_browse_btn)
        prev_btn = QPushButton("上一张")
        next_btn = QPushButton("下一张")
        prev_btn.clicked.connect(lambda: self.switch_image('ours', -1))
        next_btn.clicked.connect(lambda: self.switch_image('ours', 1))
        ours_layout.addWidget(prev_btn)
        ours_layout.addWidget(next_btn)

        gt_layout = QHBoxLayout()
        gt_layout.addWidget(self.gt_path_edit)
        gt_layout.addWidget(gt_browse_btn)
        prev_btn = QPushButton("上一张")
        next_btn = QPushButton("下一张")
        prev_btn.clicked.connect(lambda: self.switch_image('gt', -1))
        next_btn.clicked.connect(lambda: self.switch_image('gt', 1))
        gt_layout.addWidget(prev_btn)
        gt_layout.addWidget(next_btn)

        path_layout.addRow("Input图像:", input_layout)
        path_layout.addRow("Baseline图像:", baseline_layout)
        path_layout.addRow("Ours图像:", ours_layout)
        path_layout.addRow("GT图像:", gt_layout)

        path_group.setLayout(path_layout)
        main_layout.addWidget(path_group)

        # 控制按钮区域
        button_layout = QHBoxLayout()

        self.load_images_btn = QPushButton("加载图像")
        self.load_images_btn.clicked.connect(self.load_all_images)

        self.save_btn = QPushButton("保存当前视图")
        self.save_btn.clicked.connect(self.save_current_view)

        self.random_zoom_btn = QPushButton("随机放大区域")
        self.random_zoom_btn.clicked.connect(self.randomize_zoom_areas)

        self.clear_btn = QPushButton("清空路径")
        self.clear_btn.clicked.connect(self.clear_paths)

        self.prev_all_btn = QPushButton("全部上一张")
        self.next_all_btn = QPushButton("全部下一张")
        self.prev_all_btn.clicked.connect(lambda: self.switch_all_images(-1))
        self.next_all_btn.clicked.connect(lambda: self.switch_all_images(1))


        button_layout.addWidget(self.load_images_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.random_zoom_btn)
        button_layout.addWidget(self.prev_all_btn)
        button_layout.addWidget(self.next_all_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # 状态栏信息
        self.statusBar().showMessage("请手动设置图像路径后点击'加载图像'")

        # 新增：用于存储图像路径列表和当前索引
        self.image_paths_list = []
        self.current_index = 0

    # 在 MainWindow 类中新增方法
    def switch_image(self, image_type, direction):
        """
        切换指定类型的图像，基于当前路径的父目录实现

        Args:
            image_type: 图像类型 ('input', 'baseline', 'ours', 'gt')
            direction: 切换方向 (-1: 上一张, 1: 下一张)
        """
        # 获取当前路径编辑器
        path_edit = getattr(self, f"{image_type}_path_edit")
        current_path = path_edit.text()

        # 检查路径是否存在
        if not current_path or not os.path.exists(current_path):
            self.statusBar().showMessage(f"当前{image_type}图像路径不存在")
            return

        # 获取父目录
        parent_dir = os.path.dirname(current_path)

        # 获取支持的图像扩展名
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}

        # 获取目录下所有图像文件并排序
        image_files = []
        for filename in os.listdir(parent_dir):
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in image_extensions:
                image_files.append(filename)

        # 如果没有图像文件
        if not image_files:
            self.statusBar().showMessage(f"目录 {parent_dir} 中没有图像文件")
            return

        # 排序文件名以确保顺序一致
        image_files.sort()

        # 获取当前文件名
        current_filename = os.path.basename(current_path)

        # 找到当前文件在列表中的位置
        try:
            current_index = image_files.index(current_filename)
        except ValueError:
            self.statusBar().showMessage(f"未在目录中找到当前文件 {current_filename}")
            return

        # 计算新索引
        new_index = current_index + direction

        # 边界检查
        if new_index < 0:
            self.statusBar().showMessage("已经是第一张图像")
            return
        elif new_index >= len(image_files):
            self.statusBar().showMessage("已经是最后一张图像")
            return

        # 构建新路径
        new_filename = image_files[new_index]
        new_path = os.path.join(parent_dir, new_filename)

        # 更新路径
        path_edit.setText(new_path)

        # 重新加载所有图像
        image_paths = {
            'input': self.input_path_edit.text(),
            'baseline': self.baseline_path_edit.text(),
            'ours': self.ours_path_edit.text(),
            'gt': self.gt_path_edit.text()
        }

        self.image_compare_widget.load_images(image_paths)
        self.image_compare_widget.update()
        self.statusBar().showMessage(f"{image_type}图像已切换到 {new_filename} ({new_index + 1}/{len(image_files)})")

    def load_all_images(self):
        """加载所有图像"""
        image_paths = {
            'input': self.input_path_edit.text(),
            'baseline': self.baseline_path_edit.text(),
            'ours': self.ours_path_edit.text(),
            'gt': self.gt_path_edit.text()
        }

        self.image_compare_widget.load_images(image_paths)
        self.image_compare_widget.update()
        self.statusBar().showMessage("图像已加载")

    def save_current_view(self):
        """保存当前视图"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "保存图像", "",
            "Images (*.png *.jpg *.jpeg)")

        if file_name:
            # 获取widget的内容
            pixmap = QPixmap(self.image_compare_widget.size())
            self.image_compare_widget.render(pixmap)

            if pixmap.save(file_name):
                self.statusBar().showMessage(f"图像已保存: {file_name}")
            else:
                self.statusBar().showMessage("保存失败")

    def randomize_zoom_areas(self):
        """随机化两个不重叠的放大区域"""
        if self.image_compare_widget.images['input'] is not None:
            # 在input图像范围内生成两个不重叠的随机矩形
            # 第一个区域
            max_x1 = 512 - 128
            max_y1 = 512 - 128
            x1 = random.randint(0, max_x1)
            y1 = random.randint(0, max_y1)
            rect1 = QRect(x1, y1, 128, 128)

            # 第二个区域，确保不与第一个区域重叠
            attempt = 0
            max_attempts = 100
            rect2 = None

            while attempt < max_attempts:
                x2 = random.randint(0, max_x1)
                y2 = random.randint(0, max_y1)
                test_rect = QRect(x2, y2, 128, 128)

                # 检查是否与第一个区域重叠
                if not test_rect.intersects(rect1):
                    rect2 = test_rect
                    break

                attempt += 1

            # 如果无法找到不重叠的区域，则放置在固定位置
            if rect2 is None:
                # 简单地放在对角位置
                if x1 < 256:
                    x2 = max(x1 + 128, 300)  # 确保有一定距离
                else:
                    x2 = min(x1 - 128, 200)

                if y1 < 256:
                    y2 = max(y1 + 128, 300)
                else:
                    y2 = min(y1 - 128, 200)

                # 确保在有效范围内
                x2 = max(0, min(x2, max_x1))
                y2 = max(0, min(y2, max_y1))
                rect2 = QRect(x2, y2, 128, 128)

            self.image_compare_widget.set_zoom_rects(rect1, rect2)
            self.statusBar().showMessage("放大区域已更新")

    def clear_paths(self):
        """清空所有路径"""
        self.input_path_edit.clear()
        self.baseline_path_edit.clear()
        self.ours_path_edit.clear()
        self.gt_path_edit.clear()
        self.statusBar().showMessage("路径已清空")

    def switch_all_images(self, direction):
        """
        切换所有图像类型

        Args:
            direction: 切换方向 (-1: 上一张, 1: 下一张)
        """
        # 定义所有图像类型
        image_types = ['input', 'baseline', 'ours', 'gt']

        # 为每种图像类型执行切换
        for image_type in image_types:
            self.switch_image(image_type, direction)

        # 更新状态栏信息
        action = "上一张" if direction == -1 else "下一张"
        self.statusBar().showMessage(f"所有图像已切换到{action}")

    def browse_image(self, image_type):
        """浏览选择图像文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"选择{image_type.capitalize()}图像", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)")

        if file_path:
            if image_type == 'input':
                self.input_path_edit.setText(file_path)
            elif image_type == 'baseline':
                self.baseline_path_edit.setText(file_path)
            elif image_type == 'ours':
                self.ours_path_edit.setText(file_path)
            elif image_type == 'gt':
                self.gt_path_edit.setText(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
