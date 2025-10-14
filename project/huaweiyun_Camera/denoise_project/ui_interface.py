import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QTextEdit,
                               QFileDialog, QProgressBar, QGroupBox, QMessageBox,
                               QTabWidget, QLineEdit, QSpinBox, QDoubleSpinBox,
                               QSplitter, QScrollArea)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QPixmap, QImage
import torch
from train import train_model
from test import Denoiser


class TrainingThread(QThread):
    update_signal = Signal(str)
    finished_signal = Signal(bool)

    def __init__(self, gt_dir, noise_dir, epochs, batch_size, lr):
        super().__init__()
        self.gt_dir = gt_dir
        self.noise_dir = noise_dir
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr

    def run(self):
        try:
            self.update_signal.emit("开始训练...")
            train_model(self.gt_dir, self.noise_dir, self.epochs, self.batch_size, self.lr)
            self.update_signal.emit("训练完成!")
            self.finished_signal.emit(True)
        except Exception as e:
            self.update_signal.emit(f"训练错误: {str(e)}")
            self.finished_signal.emit(False)


class DenoiseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.denoiser = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("夜景图像去噪系统")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)

        # 创建标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # 训练标签页
        train_tab = QWidget()
        self.setup_train_tab(train_tab)
        tab_widget.addTab(train_tab, "模型训练")

        # 测试标签页
        test_tab = QWidget()
        self.setup_test_tab(test_tab)
        tab_widget.addTab(test_tab, "图像去噪")

        # 状态栏
        self.statusBar().showMessage("就绪")

    def setup_train_tab(self, tab):
        layout = QVBoxLayout(tab)

        # 参数设置组
        params_group = QGroupBox("训练参数")
        params_layout = QVBoxLayout(params_group)

        # GT图像目录
        gt_layout = QHBoxLayout()
        gt_layout.addWidget(QLabel("GT图像目录:"))
        self.gt_dir_edit = QLineEdit()
        gt_layout.addWidget(self.gt_dir_edit)
        self.gt_dir_btn = QPushButton("浏览")
        self.gt_dir_btn.clicked.connect(self.browse_gt_dir)
        gt_layout.addWidget(self.gt_dir_btn)
        params_layout.addLayout(gt_layout)

        # 噪声图像目录
        noise_layout = QHBoxLayout()
        noise_layout.addWidget(QLabel("噪声图像目录:"))
        self.noise_dir_edit = QLineEdit()
        noise_layout.addWidget(self.noise_dir_edit)
        self.noise_dir_btn = QPushButton("浏览")
        self.noise_dir_btn.clicked.connect(self.browse_noise_dir)
        noise_layout.addWidget(self.noise_dir_btn)
        params_layout.addLayout(noise_layout)

        # 训练参数
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(QLabel("训练轮数:"))
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 1000)
        self.epochs_spin.setValue(100)
        h_layout1.addWidget(self.epochs_spin)

        h_layout1.addWidget(QLabel("批大小:"))
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 16)
        self.batch_size_spin.setValue(4)
        h_layout1.addWidget(self.batch_size_spin)
        params_layout.addLayout(h_layout1)

        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(QLabel("学习率:"))
        self.lr_spin = QDoubleSpinBox()
        self.lr_spin.setRange(0.00001, 0.01)
        self.lr_spin.setValue(0.0001)
        self.lr_spin.setDecimals(5)
        h_layout2.addWidget(self.lr_spin)
        params_layout.addLayout(h_layout2)

        layout.addWidget(params_group)

        # 训练控制
        train_control_layout = QHBoxLayout()
        self.train_btn = QPushButton("开始训练")
        self.train_btn.clicked.connect(self.start_training)
        train_control_layout.addWidget(self.train_btn)

        self.stop_btn = QPushButton("停止训练")
        self.stop_btn.clicked.connect(self.stop_training)
        self.stop_btn.setEnabled(False)
        train_control_layout.addWidget(self.stop_btn)
        layout.addLayout(train_control_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # 训练日志
        log_group = QGroupBox("训练日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)

    def setup_test_tab(self, tab):
        layout = QVBoxLayout(tab)

        # 模型加载
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型权重:"))
        self.model_path_edit = QLineEdit()
        model_layout.addWidget(self.model_path_edit)
        self.model_browse_btn = QPushButton("浏览")
        self.model_browse_btn.clicked.connect(self.browse_model_path)
        model_layout.addWidget(self.model_browse_btn)
        self.load_model_btn = QPushButton("加载模型")
        self.load_model_btn.clicked.connect(self.load_model)
        model_layout.addWidget(self.load_model_btn)
        layout.addLayout(model_layout)

        # 图像显示区域
        splitter = QSplitter(Qt.Horizontal)

        # 输入图像
        input_scroll = QScrollArea()
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.addWidget(QLabel("输入图像 (带噪声)"))
        self.input_image_label = QLabel()
        self.input_image_label.setAlignment(Qt.AlignCenter)
        self.input_image_label.setMinimumSize(400, 400)
        self.input_image_label.setStyleSheet("border: 1px solid gray;")
        input_layout.addWidget(self.input_image_label)
        input_scroll.setWidget(input_widget)

        # 输出图像
        output_scroll = QScrollArea()
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.addWidget(QLabel("输出图像 (去噪后)"))
        self.output_image_label = QLabel()
        self.output_image_label.setAlignment(Qt.AlignCenter)
        self.output_image_label.setMinimumSize(400, 400)
        self.output_image_label.setStyleSheet("border: 1px solid gray;")
        output_layout.addWidget(self.output_image_label)
        output_scroll.setWidget(output_widget)

        splitter.addWidget(input_scroll)
        splitter.addWidget(output_scroll)
        layout.addWidget(splitter)

        # 测试控制
        test_control_layout = QHBoxLayout()

        self.single_test_btn = QPushButton("测试单张图像")
        self.single_test_btn.clicked.connect(self.test_single_image)
        self.single_test_btn.setEnabled(False)
        test_control_layout.addWidget(self.single_test_btn)

        self.folder_test_btn = QPushButton("测试文件夹")
        self.folder_test_btn.clicked.connect(self.test_folder)
        self.folder_test_btn.setEnabled(False)
        test_control_layout.addWidget(self.folder_test_btn)

        self.save_result_btn = QPushButton("保存结果")
        self.save_result_btn.clicked.connect(self.save_result)
        self.save_result_btn.setEnabled(False)
        test_control_layout.addWidget(self.save_result_btn)

        layout.addLayout(test_control_layout)

        # 测试日志
        self.test_log = QTextEdit()
        self.test_log.setReadOnly(True)
        layout.addWidget(self.test_log)

    def browse_gt_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择GT图像目录")
        if directory:
            self.gt_dir_edit.setText(directory)

    def browse_noise_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择噪声图像目录")
        if directory:
            self.noise_dir_edit.setText(directory)

    def browse_model_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择模型权重文件", "", "PyTorch Files (*.pth)")
        if file_path:
            self.model_path_edit.setText(file_path)

    def start_training(self):
        gt_dir = self.gt_dir_edit.text()
        noise_dir = self.noise_dir_edit.text()

        if not gt_dir or not noise_dir:
            QMessageBox.warning(self, "警告", "请选择GT图像目录和噪声图像目录")
            return

        if not os.path.exists(gt_dir) or not os.path.exists(noise_dir):
            QMessageBox.warning(self, "警告", "指定的目录不存在")
            return

        self.train_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_text.clear()

        # 创建训练线程
        self.training_thread = TrainingThread(
            gt_dir,
            noise_dir,
            self.epochs_spin.value(),
            self.batch_size_spin.value(),
            self.lr_spin.value()
        )
        self.training_thread.update_signal.connect(self.update_training_log)
        self.training_thread.finished_signal.connect(self.training_finished)
        self.training_thread.start()

    def stop_training(self):
        if hasattr(self, 'training_thread') and self.training_thread.isRunning():
            self.training_thread.terminate()
            self.training_thread.wait()
            self.log_text.append("训练已停止")

        self.train_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def update_training_log(self, message):
        self.log_text.append(message)
        self.statusBar().showMessage(message)

    def training_finished(self, success):
        self.train_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if success:
            QMessageBox.information(self, "完成", "训练完成!")
        else:
            QMessageBox.warning(self, "错误", "训练过程中出现错误")

    def load_model(self):
        model_path = self.model_path_edit.text()
        if not model_path:
            QMessageBox.warning(self, "警告", "请选择模型权重文件")
            return

        if not os.path.exists(model_path):
            QMessageBox.warning(self, "警告", "模型权重文件不存在")
            return

        try:
            self.denoiser = Denoiser(model_path)
            self.single_test_btn.setEnabled(True)
            self.folder_test_btn.setEnabled(True)
            self.test_log.append("模型加载成功!")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"模型加载失败: {str(e)}")

    def test_single_image(self):
        if self.denoiser is None:
            QMessageBox.warning(self, "警告", "请先加载模型")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "选择测试图像", "", "Image Files (*.jpg *.jpeg *.png *.bmp)")
        if file_path:
            try:
                # 显示输入图像
                input_pixmap = QPixmap(file_path)
                scaled_pixmap = input_pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.input_image_label.setPixmap(scaled_pixmap)

                # 去噪处理
                self.test_log.append(f"处理图像: {os.path.basename(file_path)}")
                denoised_image = self.denoiser.denoise_single_image(file_path)

                # 显示输出图像
                denoised_image_q = denoised_image.toqpixmap()
                scaled_output = denoised_image_q.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.output_image_label.setPixmap(scaled_output)

                self.current_denoised_image = denoised_image
                self.save_result_btn.setEnabled(True)
                self.test_log.append("处理完成!")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"图像处理失败: {str(e)}")

    def test_folder(self):
        if self.denoiser is None:
            QMessageBox.warning(self, "警告", "请先加载模型")
            return

        input_folder = QFileDialog.getExistingDirectory(self, "选择输入文件夹")
        if input_folder:
            output_folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
            if output_folder:
                try:
                    self.test_log.append("开始批量处理文件夹...")
                    self.denoiser.denoise_folder(input_folder, output_folder)
                    self.test_log.append("批量处理完成!")
                    QMessageBox.information(self, "完成", f"所有图像处理完成! 结果保存在: {output_folder}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"批量处理失败: {str(e)}")

    def save_result(self):
        if hasattr(self, 'current_denoised_image'):
            file_path, _ = QFileDialog.getSaveFileName(self, "保存去噪图像", "", "Image Files (*.png *.jpg *.jpeg)")
            if file_path:
                try:
                    self.current_denoised_image.save(file_path)
                    self.test_log.append(f"结果已保存: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = DenoiseApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()