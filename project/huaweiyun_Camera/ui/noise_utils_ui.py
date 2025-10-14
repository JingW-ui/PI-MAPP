import sys
import os
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageFilter
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QLineEdit,
                               QComboBox, QGroupBox, QSpinBox, QDoubleSpinBox,
                               QFileDialog, QProgressBar, QTextEdit, QCheckBox,
                               QTabWidget, QGridLayout, QMessageBox, QListWidget)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QPixmap, QFont


class ImageProcessorThread(QThread):
    """图像处理线程"""
    progress_updated = Signal(int)
    log_message = Signal(str)
    processing_finished = Signal()

    def __init__(self, input_folder, output_folder, operations):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.operations = operations
        self.is_running = True

    def run(self):
        """执行批量处理"""
        try:
            # 获取所有图像文件
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
            image_files = []
            for ext in image_extensions:
                image_files.extend(Path(self.input_folder).glob(ext))
                image_files.extend(Path(self.input_folder).glob(ext.upper()))

            total_files = len(image_files)
            self.log_message.emit(f"找到 {total_files} 个图像文件")

            if total_files == 0:
                self.log_message.emit("错误: 在输入文件夹中未找到图像文件!")
                return

            # 创建输出文件夹
            Path(self.output_folder).mkdir(parents=True, exist_ok=True)

            # 处理每个文件
            for i, image_path in enumerate(image_files):
                if not self.is_running:
                    break

                try:
                    self.log_message.emit(f"处理文件: {image_path.name}")

                    # 读取图像
                    image = cv2.imread(str(image_path))
                    if image is None:
                        self.log_message.emit(f"警告: 无法读取文件 {image_path.name}")
                        continue

                    processed_image = image.copy()

                    # 应用所有选定的操作
                    for operation in self.operations:
                        if not self.is_running:
                            break
                        processed_image = self.apply_operation(processed_image, operation)

                    # 保存处理后的图像
                    output_path = Path(self.output_folder) / image_path.name
                    success = cv2.imwrite(str(output_path), processed_image)

                    if success:
                        self.log_message.emit(f"✓ 成功保存: {output_path.name}")
                    else:
                        self.log_message.emit(f"✗ 保存失败: {output_path.name}")

                    # 更新进度
                    progress = int((i + 1) / total_files * 100)
                    self.progress_updated.emit(progress)

                except Exception as e:
                    self.log_message.emit(f"✗ 处理 {image_path.name} 时出错: {str(e)}")
                    continue

            self.log_message.emit("批量处理完成!")

        except Exception as e:
            self.log_message.emit(f"✗ 处理过程中发生错误: {str(e)}")

        finally:
            self.processing_finished.emit()

    def apply_operation(self, image, operation):
        """应用单个操作到图像"""
        op_type = operation['type']
        params = operation['params']

        if op_type == 'gaussian_noise':
            return self.add_gaussian_noise(image, **params)
        elif op_type == 'salt_pepper_noise':
            return self.add_salt_pepper_noise(image, **params)
        elif op_type == 'poisson_noise':
            return self.add_poisson_noise(image)
        elif op_type == 'uniform_noise':
            return self.add_uniform_noise(image, **params)
        elif op_type == 'gaussian_blur':
            return self.gaussian_blur(image, **params)
        elif op_type == 'median_blur':
            return self.median_blur(image, **params)
        elif op_type == 'motion_blur':
            return self.motion_blur(image, **params)
        elif op_type == 'bokeh_blur':
            return self.bokeh_blur(image, **params)
        else:
            return image

    def add_gaussian_noise(self, image, mean=0, sigma=25):
        """添加高斯噪声"""
        row, col, ch = image.shape
        gauss = np.random.normal(mean, sigma, (row, col, ch))
        noisy = image + gauss
        return np.clip(noisy, 0, 255).astype(np.uint8)

    def add_salt_pepper_noise(self, image, salt_prob=0.01, pepper_prob=0.01):
        """添加椒盐噪声"""
        noisy = np.copy(image)
        # 盐噪声 (白点)
        salt_mask = np.random.random(image.shape[:2]) < salt_prob
        noisy[salt_mask] = 255
        # 椒噪声 (黑点)
        pepper_mask = np.random.random(image.shape[:2]) < pepper_prob
        noisy[pepper_mask] = 0
        return noisy

    def add_poisson_noise(self, image):
        """添加泊松噪声"""
        vals = len(np.unique(image))
        vals = 2 ** np.ceil(np.log2(vals))
        noisy = np.random.poisson(image * vals) / float(vals)
        return np.clip(noisy, 0, 255).astype(np.uint8)

    def add_uniform_noise(self, image, low=-10, high=10):
        """添加均匀噪声"""
        uniform_noise = np.random.uniform(low, high, image.shape)
        noisy = image + uniform_noise
        return np.clip(noisy, 0, 255).astype(np.uint8)

    def gaussian_blur(self, image, kernel_size=5, sigma_x=0):
        """高斯模糊"""
        # 确保核大小为奇数
        if kernel_size % 2 == 0:
            kernel_size += 1
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma_x)

    def median_blur(self, image, kernel_size=5):
        """中值模糊"""
        # 确保核大小为奇数
        if kernel_size % 2 == 0:
            kernel_size += 1
        return cv2.medianBlur(image, kernel_size)

    def motion_blur(self, image, kernel_size=15, angle=0):
        """运动模糊"""
        # 创建运动模糊核
        kernel = np.zeros((kernel_size, kernel_size))
        center = (kernel_size - 1) // 2

        if angle == 0:  # 水平
            kernel[center, :] = 1
        elif angle == 90:  # 垂直
            kernel[:, center] = 1
        else:  # 对角线
            for i in range(kernel_size):
                j = int((i - center) * np.tan(np.radians(angle)) + center)
                if 0 <= j < kernel_size:
                    kernel[j, i] = 1

        kernel = kernel / kernel.sum() if kernel.sum() > 0 else kernel
        return cv2.filter2D(image, -1, kernel)

    def bokeh_blur(self, image, radius=5):
        """散景模糊"""
        # 使用PIL进行高斯模糊来模拟散景效果
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        blurred_pil = pil_image.filter(ImageFilter.GaussianBlur(radius=radius))
        blurred_array = np.array(blurred_pil)
        return cv2.cvtColor(blurred_array, cv2.COLOR_RGB2BGR)

    def stop(self):
        """停止处理"""
        self.is_running = False


class ImageProcessorApp(QMainWindow):
    """主应用程序窗口"""

    def __init__(self):
        super().__init__()
        self.processor_thread = None
        self.operations = []  # 存储选定的操作
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("图像噪声与模糊处理工具")
        self.setGeometry(100, 100, 900, 700)

        # 中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # 文件设置标签页
        file_tab = QWidget()
        self.setup_file_tab(file_tab)
        tab_widget.addTab(file_tab, "文件设置")

        # 噪声处理标签页
        noise_tab = QWidget()
        self.setup_noise_tab(noise_tab)
        tab_widget.addTab(noise_tab, "噪声处理")

        # 模糊处理标签页
        blur_tab = QWidget()
        self.setup_blur_tab(blur_tab)
        tab_widget.addTab(blur_tab, "模糊处理")

        # 操作列表标签页
        operations_tab = QWidget()
        self.setup_operations_tab(operations_tab)
        tab_widget.addTab(operations_tab, "操作列表")

        # 进度和日志区域
        self.setup_progress_log_area(main_layout)

        # 处理按钮
        button_layout = QHBoxLayout()
        self.process_btn = QPushButton("开始批量处理")
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-size: 14px; padding: 10px; }")

        self.stop_btn = QPushButton("停止处理")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; font-size: 14px; padding: 10px; }")

        button_layout.addWidget(self.process_btn)
        button_layout.addWidget(self.stop_btn)
        main_layout.addLayout(button_layout)

    def setup_file_tab(self, tab):
        """设置文件标签页"""
        layout = QVBoxLayout(tab)

        # 输入文件夹
        input_group = QGroupBox("输入文件夹")
        input_layout = QHBoxLayout(input_group)
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("选择输入文件夹...")
        input_browse_btn = QPushButton("浏览")
        input_browse_btn.clicked.connect(self.browse_input_folder)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(input_browse_btn)
        layout.addWidget(input_group)

        # 输出文件夹
        output_group = QGroupBox("输出文件夹")
        output_layout = QHBoxLayout(output_group)
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("选择输出文件夹...")
        output_browse_btn = QPushButton("浏览")
        output_browse_btn.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_browse_btn)
        layout.addWidget(output_group)

        layout.addStretch()

    def setup_noise_tab(self, tab):
        """设置噪声处理标签页"""
        layout = QVBoxLayout(tab)

        # 噪声类型选择
        noise_type_group = QGroupBox("选择噪声类型")
        noise_type_layout = QVBoxLayout(noise_type_group)

        self.noise_type_combo = QComboBox()
        self.noise_type_combo.addItems([
            "高斯噪声",
            "椒盐噪声",
            "泊松噪声",
            "均匀噪声"
        ])
        noise_type_layout.addWidget(QLabel("噪声类型:"))
        noise_type_layout.addWidget(self.noise_type_combo)

        # 参数区域
        self.noise_params_widget = QWidget()
        self.noise_params_layout = QGridLayout(self.noise_params_widget)
        noise_type_layout.addWidget(self.noise_params_widget)

        # 更新参数区域当噪声类型改变时
        self.noise_type_combo.currentTextChanged.connect(self.update_noise_params)
        self.update_noise_params()

        layout.addWidget(noise_type_group)

        # 添加噪声按钮
        add_noise_btn = QPushButton("添加到操作列表")
        add_noise_btn.clicked.connect(self.add_noise_operation)
        add_noise_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px; }")
        layout.addWidget(add_noise_btn)

        layout.addStretch()

    def setup_blur_tab(self, tab):
        """设置模糊处理标签页"""
        layout = QVBoxLayout(tab)

        # 模糊类型选择
        blur_type_group = QGroupBox("选择模糊类型")
        blur_type_layout = QVBoxLayout(blur_type_group)

        self.blur_type_combo = QComboBox()
        self.blur_type_combo.addItems([
            "高斯模糊",
            "中值模糊",
            "运动模糊",
            "散景模糊"
        ])
        blur_type_layout.addWidget(QLabel("模糊类型:"))
        blur_type_layout.addWidget(self.blur_type_combo)

        # 参数区域
        self.blur_params_widget = QWidget()
        self.blur_params_layout = QGridLayout(self.blur_params_widget)
        blur_type_layout.addWidget(self.blur_params_widget)

        # 更新参数区域当模糊类型改变时
        self.blur_type_combo.currentTextChanged.connect(self.update_blur_params)
        self.update_blur_params()

        layout.addWidget(blur_type_group)

        # 添加模糊按钮
        add_blur_btn = QPushButton("添加到操作列表")
        add_blur_btn.clicked.connect(self.add_blur_operation)
        add_blur_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px; }")
        layout.addWidget(add_blur_btn)

        layout.addStretch()

    def setup_operations_tab(self, tab):
        """设置操作列表标签页"""
        layout = QVBoxLayout(tab)

        # 操作列表
        operations_group = QGroupBox("当前操作列表 (按顺序执行)")
        operations_layout = QVBoxLayout(operations_group)

        self.operations_list = QListWidget()
        operations_layout.addWidget(self.operations_list)

        # 操作控制按钮
        op_buttons_layout = QHBoxLayout()
        self.clear_ops_btn = QPushButton("清空列表")
        self.clear_ops_btn.clicked.connect(self.clear_operations)
        self.remove_op_btn = QPushButton("移除选中")
        self.remove_op_btn.clicked.connect(self.remove_operation)

        op_buttons_layout.addWidget(self.clear_ops_btn)
        op_buttons_layout.addWidget(self.remove_op_btn)
        op_buttons_layout.addStretch()

        operations_layout.addLayout(op_buttons_layout)
        layout.addWidget(operations_group)

        layout.addStretch()

    def setup_progress_log_area(self, main_layout):
        """设置进度和日志区域"""
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 日志区域
        log_group = QGroupBox("处理日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        main_layout.addWidget(log_group)

    def update_noise_params(self):
        """更新噪声参数界面"""
        # 清除现有参数控件
        for i in reversed(range(self.noise_params_layout.count())):
            self.noise_params_layout.itemAt(i).widget().setParent(None)

        noise_type = self.noise_type_combo.currentText()
        row = 0

        if noise_type == "高斯噪声":
            self.noise_params_layout.addWidget(QLabel("均值:"), row, 0)
            self.gauss_mean_spin = QDoubleSpinBox()
            self.gauss_mean_spin.setRange(-100, 100)
            self.gauss_mean_spin.setValue(0)
            self.noise_params_layout.addWidget(self.gauss_mean_spin, row, 1)

            row += 1
            self.noise_params_layout.addWidget(QLabel("标准差:"), row, 0)
            self.gauss_sigma_spin = QDoubleSpinBox()
            self.gauss_sigma_spin.setRange(0, 100)
            self.gauss_sigma_spin.setValue(25)
            self.noise_params_layout.addWidget(self.gauss_sigma_spin, row, 1)

        elif noise_type == "椒盐噪声":
            self.noise_params_layout.addWidget(QLabel("盐噪声概率:"), row, 0)
            self.salt_prob_spin = QDoubleSpinBox()
            self.salt_prob_spin.setRange(0, 1)
            self.salt_prob_spin.setSingleStep(0.01)
            self.salt_prob_spin.setValue(0.01)
            self.noise_params_layout.addWidget(self.salt_prob_spin, row, 1)

            row += 1
            self.noise_params_layout.addWidget(QLabel("椒噪声概率:"), row, 0)
            self.pepper_prob_spin = QDoubleSpinBox()
            self.pepper_prob_spin.setRange(0, 1)
            self.pepper_prob_spin.setSingleStep(0.01)
            self.pepper_prob_spin.setValue(0.01)
            self.noise_params_layout.addWidget(self.pepper_prob_spin, row, 1)

        elif noise_type == "均匀噪声":
            self.noise_params_layout.addWidget(QLabel("下限:"), row, 0)
            self.uniform_low_spin = QDoubleSpinBox()
            self.uniform_low_spin.setRange(-50, 0)
            self.uniform_low_spin.setValue(-10)
            self.noise_params_layout.addWidget(self.uniform_low_spin, row, 1)

            row += 1
            self.noise_params_layout.addWidget(QLabel("上限:"), row, 0)
            self.uniform_high_spin = QDoubleSpinBox()
            self.uniform_high_spin.setRange(0, 50)
            self.uniform_high_spin.setValue(10)
            self.noise_params_layout.addWidget(self.uniform_high_spin, row, 1)

        # 泊松噪声没有参数

    def update_blur_params(self):
        """更新模糊参数界面"""
        # 清除现有参数控件
        for i in reversed(range(self.blur_params_layout.count())):
            self.blur_params_layout.itemAt(i).widget().setParent(None)

        blur_type = self.blur_type_combo.currentText()
        row = 0

        if blur_type == "高斯模糊":
            self.blur_params_layout.addWidget(QLabel("核大小:"), row, 0)
            self.gauss_kernel_spin = QSpinBox()
            self.gauss_kernel_spin.setRange(1, 51)
            self.gauss_kernel_spin.setValue(5)
            self.gauss_kernel_spin.setSingleStep(2)
            self.blur_params_layout.addWidget(self.gauss_kernel_spin, row, 1)

            row += 1
            self.blur_params_layout.addWidget(QLabel("Sigma X:"), row, 0)
            self.gauss_sigma_spin = QDoubleSpinBox()
            self.gauss_sigma_spin.setRange(0, 50)
            self.gauss_sigma_spin.setValue(0)
            self.blur_params_layout.addWidget(self.gauss_sigma_spin, row, 1)

        elif blur_type == "中值模糊":
            self.blur_params_layout.addWidget(QLabel("核大小:"), row, 0)
            self.median_kernel_spin = QSpinBox()
            self.median_kernel_spin.setRange(1, 51)
            self.median_kernel_spin.setValue(5)
            self.median_kernel_spin.setSingleStep(2)
            self.blur_params_layout.addWidget(self.median_kernel_spin, row, 1)

        elif blur_type == "运动模糊":
            self.blur_params_layout.addWidget(QLabel("核大小:"), row, 0)
            self.motion_kernel_spin = QSpinBox()
            self.motion_kernel_spin.setRange(3, 51)
            self.motion_kernel_spin.setValue(15)
            self.motion_kernel_spin.setSingleStep(2)
            self.blur_params_layout.addWidget(self.motion_kernel_spin, row, 1)

            row += 1
            self.blur_params_layout.addWidget(QLabel("角度:"), row, 0)
            self.motion_angle_spin = QSpinBox()
            self.motion_angle_spin.setRange(0, 180)
            self.motion_angle_spin.setValue(0)
            self.blur_params_layout.addWidget(self.motion_angle_spin, row, 1)

        elif blur_type == "散景模糊":
            self.blur_params_layout.addWidget(QLabel("半径:"), row, 0)
            self.bokeh_radius_spin = QDoubleSpinBox()
            self.bokeh_radius_spin.setRange(0.1, 50)
            self.bokeh_radius_spin.setValue(5)
            self.blur_params_layout.addWidget(self.bokeh_radius_spin, row, 1)

    def add_noise_operation(self):
        """添加噪声操作到列表"""
        noise_type = self.noise_type_combo.currentText()
        params = {}

        if noise_type == "高斯噪声":
            op_type = 'gaussian_noise'
            params = {
                'mean': self.gauss_mean_spin.value(),
                'sigma': self.gauss_sigma_spin.value()
            }
            display_text = f"高斯噪声 (均值: {params['mean']}, 标准差: {params['sigma']})"

        elif noise_type == "椒盐噪声":
            op_type = 'salt_pepper_noise'
            params = {
                'salt_prob': self.salt_prob_spin.value(),
                'pepper_prob': self.pepper_prob_spin.value()
            }
            display_text = f"椒盐噪声 (盐: {params['salt_prob']:.3f}, 椒: {params['pepper_prob']:.3f})"

        elif noise_type == "泊松噪声":
            op_type = 'poisson_noise'
            display_text = "泊松噪声"

        elif noise_type == "均匀噪声":
            op_type = 'uniform_noise'
            params = {
                'low': self.uniform_low_spin.value(),
                'high': self.uniform_high_spin.value()
            }
            display_text = f"均匀噪声 (范围: [{params['low']}, {params['high']}])"

        operation = {
            'type': op_type,
            'params': params,
            'display': display_text
        }

        self.operations.append(operation)
        self.update_operations_list()
        self.log_text.append(f"✓ 添加操作: {display_text}")

    def add_blur_operation(self):
        """添加模糊操作到列表"""
        blur_type = self.blur_type_combo.currentText()
        params = {}

        if blur_type == "高斯模糊":
            op_type = 'gaussian_blur'
            params = {
                'kernel_size': self.gauss_kernel_spin.value(),
                'sigma_x': self.gauss_sigma_spin.value()
            }
            display_text = f"高斯模糊 (核大小: {params['kernel_size']}, Sigma: {params['sigma_x']})"

        elif blur_type == "中值模糊":
            op_type = 'median_blur'
            params = {
                'kernel_size': self.median_kernel_spin.value()
            }
            display_text = f"中值模糊 (核大小: {params['kernel_size']})"

        elif blur_type == "运动模糊":
            op_type = 'motion_blur'
            params = {
                'kernel_size': self.motion_kernel_spin.value(),
                'angle': self.motion_angle_spin.value()
            }
            display_text = f"运动模糊 (核大小: {params['kernel_size']}, 角度: {params['angle']}°)"

        elif blur_type == "散景模糊":
            op_type = 'bokeh_blur'
            params = {
                'radius': self.bokeh_radius_spin.value()
            }
            display_text = f"散景模糊 (半径: {params['radius']})"

        operation = {
            'type': op_type,
            'params': params,
            'display': display_text
        }

        self.operations.append(operation)
        self.update_operations_list()
        self.log_text.append(f"✓ 添加操作: {display_text}")

    def update_operations_list(self):
        """更新操作列表显示"""
        self.operations_list.clear()
        for i, op in enumerate(self.operations):
            self.operations_list.addItem(f"{i + 1}. {op['display']}")

    def clear_operations(self):
        """清空操作列表"""
        self.operations.clear()
        self.operations_list.clear()
        self.log_text.append("✓ 操作列表已清空")

    def remove_operation(self):
        """移除选中的操作"""
        current_row = self.operations_list.currentRow()
        if current_row >= 0:
            removed_op = self.operations.pop(current_row)
            self.update_operations_list()
            self.log_text.append(f"✓ 移除操作: {removed_op['display']}")

    def browse_input_folder(self):
        """浏览输入文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择输入文件夹")
        if folder:
            self.input_path.setText(folder)
            # 自动设置输出文件夹为输入文件夹下的_noise_output子文件夹
            default_output = folder+"_ours_output"
            self.output_path.setText(default_output)

    def browse_output_folder(self):
        """浏览输出文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder:
            self.output_path.setText(folder)

    def start_processing(self):
        """开始批量处理"""
        # 验证输入
        if not self.input_path.text() or not Path(self.input_path.text()).exists():
            QMessageBox.warning(self, "警告", "请选择有效的输入文件夹!")
            return

        if not self.output_path.text():
            QMessageBox.warning(self, "警告", "请选择输出文件夹!")
            return

        if len(self.operations) == 0:
            QMessageBox.warning(self, "警告", "请至少添加一个处理操作!")
            return

        # 禁用按钮，显示进度条
        self.process_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # 清空日志
        self.log_text.clear()
        self.log_text.append("开始批量处理...")

        # 启动处理线程
        self.processor_thread = ImageProcessorThread(
            self.input_path.text(),
            self.output_path.text(),
            self.operations
        )
        self.processor_thread.progress_updated.connect(self.progress_bar.setValue)
        self.processor_thread.log_message.connect(self.log_text.append)
        self.processor_thread.processing_finished.connect(self.processing_finished)
        self.processor_thread.start()

    def stop_processing(self):
        """停止处理"""
        if self.processor_thread and self.processor_thread.isRunning():
            self.processor_thread.stop()
            self.log_text.append("正在停止处理...")
            self.stop_btn.setEnabled(False)

    def processing_finished(self):
        """处理完成"""
        self.process_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "完成", "批量处理完成!")


def main():
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle('Fusion')

    window = ImageProcessorApp()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()