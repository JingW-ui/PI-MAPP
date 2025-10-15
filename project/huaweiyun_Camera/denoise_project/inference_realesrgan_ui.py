import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QGridLayout, QLabel, QLineEdit, QPushButton, QGroupBox,
                               QSpinBox, QProgressBar, QTextEdit, QFileDialog, QComboBox,
                               QCheckBox, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal
import cv2
import glob
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

class InferenceThread(QThread):
    progress_updated = Signal(int)
    log_updated = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, args):
        super().__init__()
        self.args = args

    def run(self):
        try:
            # 初始化模型参数
            if self.args.model_name == 'RealESRGAN_x4plus':  # x4 RRDBNet model
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
                netscale = 4
            elif self.args.model_name == 'RealESRNet_x4plus':  # x4 RRDBNet model
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
                netscale = 4
            elif self.args.model_name == 'RealESRGAN_x4plus_anime_6B':  # x4 RRDBNet model with 6 blocks
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
                netscale = 4
            elif self.args.model_name == 'RealESRGAN_x2plus':  # x2 RRDBNet model
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
                netscale = 2
            elif self.args.model_name == 'realesr-animevideov3':  # x4 VGG-style model (XS size)
                model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=16, upscale=4,
                                        act_type='prelu')
                netscale = 4
            elif self.args.model_name == 'realesr-general-x4v3':  # x4 VGG-style model (S size)
                model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4,
                                        act_type='prelu')
                netscale = 4

            # 初始化upsampler
            upsampler = RealESRGANer(
                scale=netscale,
                model_path=self.args.model_path,
                model=model,
                tile=self.args.tile,
                tile_pad=self.args.tile_pad,
                pre_pad=self.args.pre_pad,
                half=not self.args.fp32)

            # 创建输出目录
            os.makedirs(self.args.output, exist_ok=True)

            # 获取图像路径
            if os.path.isfile(self.args.input):
                paths = [self.args.input]
            else:
                paths = sorted(glob.glob(os.path.join(self.args.input, '*')))

            total = len(paths)
            for idx, path in enumerate(paths):
                imgname, extension = os.path.splitext(os.path.basename(path))
                self.log_updated.emit(f'Processing {idx + 1}/{total}: {imgname}')

                img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if img is None:
                    self.log_updated.emit(f'Warning: Failed to read image {path}')
                    continue

                if len(img.shape) == 3 and img.shape[2] == 4:
                    img_mode = 'RGBA'
                else:
                    img_mode = None

                try:
                    output, _ = upsampler.enhance(img, outscale=self.args.outscale)
                except RuntimeError as error:
                    self.log_updated.emit(f'Error: {error}')
                    continue

                if self.args.ext == 'auto':
                    extension = extension[1:]
                else:
                    extension = self.args.ext
                if img_mode == 'RGBA':  # RGBA images should be saved in png format
                    extension = 'png'
                if self.args.suffix == '':
                    save_path = os.path.join(self.args.output, f'{imgname}.{extension}')
                else:
                    save_path = os.path.join(self.args.output, f'{imgname}_{self.args.suffix}.{extension}')

                cv2.imwrite(save_path, output)
                self.progress_updated.emit(int((idx + 1) / total * 100))

            self.finished_signal.emit(True, "Processing completed successfully!")
        except Exception as e:
            self.finished_signal.emit(False, f"Processing failed: {str(e)}")


class Args:
    def __init__(self):
        self.input = ""
        self.model_name = "RealESRGAN_x4plus"
        self.output = "results"
        self.denoise_strength = 0.5
        self.outscale = 4
        self.model_path = None
        self.suffix = "out"
        self.tile = 0
        self.tile_pad = 10
        self.pre_pad = 0
        self.face_enhance = False
        self.fp32 = False
        self.alpha_upsampler = "realesrgan"
        self.ext = "auto"
        self.gpu_id = None


class RealESRGANUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.args = Args()
        self.inference_thread = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Real-ESRGAN 图像超分辨率工具")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 输入设置组
        input_group = QGroupBox("输入设置")
        input_layout = QGridLayout(input_group)

        input_layout.addWidget(QLabel("输入图像或文件夹:"), 0, 0)
        self.input_line = QLineEdit()
        self.input_browse_btn = QPushButton("浏览...")
        self.input_browse_btn.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_line, 0, 1)
        input_layout.addWidget(self.input_browse_btn, 0, 2)

        input_layout.addWidget(QLabel("输出文件夹:"), 1, 0)
        self.output_line = QLineEdit()
        self.output_browse_btn = QPushButton("浏览...")
        self.output_browse_btn.clicked.connect(self.browse_output)
        input_layout.addWidget(self.output_line, 1, 1)
        input_layout.addWidget(self.output_browse_btn, 1, 2)

        main_layout.addWidget(input_group)

        # 模型设置组
        model_group = QGroupBox("模型设置")
        model_layout = QGridLayout(model_group)

        model_layout.addWidget(QLabel("模型名称:"), 0, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "RealESRGAN_x4plus",
            "RealESRNet_x4plus",
            "RealESRGAN_x4plus_anime_6B",
            "RealESRGAN_x2plus",
            "realesr-animevideov3",
            "realesr-general-x4v3"
        ])
        model_layout.addWidget(self.model_combo, 0, 1)

        model_layout.addWidget(QLabel("模型路径(可选):"), 1, 0)
        self.model_path_line = QLineEdit()
        self.model_path_browse_btn = QPushButton("浏览...")
        self.model_path_browse_btn.clicked.connect(self.browse_model)
        model_layout.addWidget(self.model_path_line, 1, 1)
        model_layout.addWidget(self.model_path_browse_btn, 1, 2)

        model_layout.addWidget(QLabel("放大倍数:"), 2, 0)
        self.outscale_spin = QSpinBox()
        self.outscale_spin.setRange(1, 8)
        self.outscale_spin.setValue(4)
        model_layout.addWidget(self.outscale_spin, 2, 1)

        model_layout.addWidget(QLabel("去噪强度(仅realesr-general-x4v3):"), 3, 0)
        self.denoise_spin = QSpinBox()
        self.denoise_spin.setRange(0, 100)
        self.denoise_spin.setValue(50)
        self.denoise_spin.setSuffix("%")
        model_layout.addWidget(self.denoise_spin, 3, 1)

        main_layout.addWidget(model_group)

        # 高级设置组
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QGridLayout(advanced_group)

        self.face_enhance_check = QCheckBox("使用GFPGAN增强人脸")
        advanced_layout.addWidget(self.face_enhance_check, 0, 0)

        self.fp32_check = QCheckBox("使用FP32精度(默认FP16)")
        advanced_layout.addWidget(self.fp32_check, 0, 1)

        advanced_layout.addWidget(QLabel("瓦片大小(0为无瓦片):"), 1, 0)
        self.tile_spin = QSpinBox()
        self.tile_spin.setRange(0, 2048)
        self.tile_spin.setValue(0)
        advanced_layout.addWidget(self.tile_spin, 1, 1)

        advanced_layout.addWidget(QLabel("瓦片填充:"), 2, 0)
        self.tile_pad_spin = QSpinBox()
        self.tile_pad_spin.setRange(0, 100)
        self.tile_pad_spin.setValue(10)
        advanced_layout.addWidget(self.tile_pad_spin, 2, 1)

        advanced_layout.addWidget(QLabel("预填充:"), 3, 0)
        self.pre_pad_spin = QSpinBox()
        self.pre_pad_spin.setRange(0, 100)
        self.pre_pad_spin.setValue(0)
        advanced_layout.addWidget(self.pre_pad_spin, 3, 1)

        advanced_layout.addWidget(QLabel("输出图像后缀:"), 4, 0)
        self.suffix_line = QLineEdit("out")
        advanced_layout.addWidget(self.suffix_line, 4, 1)

        advanced_layout.addWidget(QLabel("输出格式:"), 5, 0)
        self.ext_combo = QComboBox()
        self.ext_combo.addItems(["auto", "jpg", "png"])
        advanced_layout.addWidget(self.ext_combo, 5, 1)

        main_layout.addWidget(advanced_group)

        # 进度和日志组
        progress_group = QGroupBox("处理状态")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.log_text)

        main_layout.addWidget(progress_group)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始处理")
        self.start_btn.clicked.connect(self.start_processing)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(button_layout)

    def browse_input(self):
        path = QFileDialog.getExistingDirectory(self, "选择输入文件夹")
        if path:
            self.input_line.setText(path)

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if path:
            self.output_line.setText(path)

    def browse_model(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择模型文件", "", "Model Files (*.pth)")
        if file_path:
            self.model_path_line.setText(file_path)

    def update_args(self):
        self.args.input = self.input_line.text()
        self.args.model_name = self.model_combo.currentText()
        self.args.output = self.output_line.text()
        self.args.denoise_strength = self.denoise_spin.value() / 100.0
        self.args.outscale = self.outscale_spin.value()
        self.args.model_path = self.model_path_line.text() or None
        self.args.suffix = self.suffix_line.text()
        self.args.tile = self.tile_spin.value()
        self.args.tile_pad = self.tile_pad_spin.value()
        self.args.pre_pad = self.pre_pad_spin.value()
        self.args.face_enhance = self.face_enhance_check.isChecked()
        self.args.fp32 = self.fp32_check.isChecked()
        self.args.ext = self.ext_combo.currentText()

    def start_processing(self):
        if not self.input_line.text():
            QMessageBox.warning(self, "警告", "请选择输入图像或文件夹!")
            return

        if not os.path.exists(self.input_line.text()):
            QMessageBox.warning(self, "警告", "输入路径不存在!")
            return

        self.update_args()
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)

        self.inference_thread = InferenceThread(self.args)
        self.inference_thread.progress_updated.connect(self.progress_bar.setValue)
        self.inference_thread.log_updated.connect(self.log_text.append)
        self.inference_thread.finished_signal.connect(self.on_processing_finished)
        self.inference_thread.start()

    def cancel_processing(self):
        if self.inference_thread and self.inference_thread.isRunning():
            self.inference_thread.terminate()
            self.inference_thread.wait()
            self.on_processing_finished(False, "Processing cancelled by user.")

    def on_processing_finished(self, success, message):
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        if success:
            QMessageBox.information(self, "完成", message)
        else:
            QMessageBox.warning(self, "错误", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RealESRGANUI()
    window.show()
    sys.exit(app.exec())
