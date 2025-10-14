import sys, os, subprocess
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QFileDialog,
                               QLabel, QVBoxLayout, QHBoxLayout, QGroupBox)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import torch
from infer import load_model, inference_one, inference_folder
from PIL import Image
import numpy as np

class DenoiseUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Night Denoise - Classic CNN')
        self.resize(900, 600)
        self.model = None
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout(self)

        # 权重
        wbox = QHBoxLayout()
        self.wlabel = QLabel('权重：未加载')
        wbtn = QPushButton('选择权重')
        wbtn.clicked.connect(self.load_weight)
        wbox.addWidget(self.wlabel, 1)
        wbox.addWidget(wbtn)
        vbox.addLayout(wbox)

        # 输入
        gbox = QGroupBox('输入')
        gvb = QVBoxLayout(gbox)
        self.inlabel = QLabel('未选择')
        ibtn = QPushButton('单图')
        ibtn.clicked.connect(lambda: self.select_input(False))
        fbtn = QPushButton('文件夹')
        fbtn.clicked.connect(lambda: self.select_input(True))
        gvb.addWidget(self.inlabel)
        gvb.addWidget(ibtn)
        gvb.addWidget(fbtn)
        vbox.addWidget(gbox)

        # 运行
        runbtn = QPushButton('开始推理')
        runbtn.clicked.connect(self.infer)
        vbox.addWidget(runbtn)

        # 结果
        self.reslabel = QLabel('结果预览')
        self.reslabel.setAlignment(Qt.AlignCenter)
        self.reslabel.setMinimumSize(512,512)
        vbox.addWidget(self.reslabel, stretch=1)

    def load_weight(self):
        path, _ = QFileDialog.getOpenFileName(self, filter='*.pth')
        if path:
            self.model = load_model(path, torch.device('cuda' if torch.cuda.is_available() else 'cpu'))
            self.wlabel.setText(f'权重：{os.path.basename(path)}')

    def select_input(self, folder_mode):
        self.folder_mode = folder_mode
        if folder_mode:
            self.input_path = QFileDialog.getExistingDirectory(self)
            self.inlabel.setText(f'文件夹：{os.path.basename(self.input_path)}')
        else:
            self.input_path, _ = QFileDialog.getOpenFileName(self, filter='Images (*.png *.jpg *.bmp)')
            self.inlabel.setText(f'单图：{os.path.basename(self.input_path)}')

    def infer(self):
        if self.model is None:
            self.reslabel.setText('请先加载权重！')
            return
        if not hasattr(self, 'input_path'):
            self.reslabel.setText('请先选择输入！')
            return
        out_dir = 'result'
        os.makedirs(out_dir, exist_ok=True)
        if self.folder_mode:
            inference_folder(self.model, self.input_path, out_dir, self.model.device)
            self.reslabel.setText('文件夹推理完成，请在 result/ 查看')
        else:
            out_path = os.path.join(out_dir, os.path.basename(self.input_path))
            inference_one(self.model, self.input_path, out_path, self.model.device)
            # 显示
            qimg = QImage(out_path)
            self.reslabel.setPixmap(QPixmap.fromImage(qimg).scaled(
                self.reslabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = DenoiseUI()
    win.show()
    sys.exit(app.exec())