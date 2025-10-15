import sys
import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QGridLayout, QLabel, QLineEdit, QPushButton, QGroupBox,
                               QTextEdit, QFileDialog, QMessageBox, QComboBox, QSpinBox,
                               QCheckBox, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal

os.environ['PYTHONIOENCODING'] = 'utf-8'


class TrainThread(QThread):
    log_updated = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path

    def run(self):
        try:
            # 构建训练命令
            cmd = [
                sys.executable,
                "realesrgan/train.py",
                "-opt", self.config_path,
                "--auto_resume"
            ]

            self.log_updated.emit(f"执行命令: {' '.join(cmd)}")

            # 执行训练过程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # 实时读取输出
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_updated.emit(output.strip())

            # 等待进程结束
            return_code = process.poll()

            if return_code == 0:
                self.finished_signal.emit(True, "训练完成!")
            else:
                self.finished_signal.emit(False, f"训练失败，返回码: {return_code}")

        except Exception as e:
            self.finished_signal.emit(False, f"训练出错: {str(e)}")


class RealESRGANTrainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.train_thread = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Real-ESRGAN 微调训练工具")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 配置文件设置组
        config_group = QGroupBox("配置文件设置")
        config_layout = QGridLayout(config_group)

        config_layout.addWidget(QLabel("YAML配置文件:"), 0, 0)
        self.config_line = QLineEdit("options/finetune_realesrgan_x4plus_pairdata.yml")
        self.config_browse_btn = QPushButton("浏览...")
        self.config_browse_btn.clicked.connect(self.browse_config)
        config_layout.addWidget(self.config_line, 0, 1)
        config_layout.addWidget(self.config_browse_btn, 0, 2)

        main_layout.addWidget(config_group)

        # 数据集设置组
        dataset_group = QGroupBox("数据集设置")
        dataset_layout = QGridLayout(dataset_group)

        dataset_layout.addWidget(QLabel("数据集名称:"), 0, 0)
        self.dataset_name_line = QLineEdit("DIV2K")
        dataset_layout.addWidget(self.dataset_name_line, 0, 1)

        dataset_layout.addWidget(QLabel("高质量图像根目录:"), 1, 0)
        self.gt_root_line = QLineEdit("datasets/DF2K")
        self.gt_root_browse_btn = QPushButton("浏览...")
        self.gt_root_browse_btn.clicked.connect(lambda: self.browse_folder(self.gt_root_line))
        dataset_layout.addWidget(self.gt_root_line, 1, 1)
        dataset_layout.addWidget(self.gt_root_browse_btn, 1, 2)

        dataset_layout.addWidget(QLabel("低质量图像根目录:"), 2, 0)
        self.lq_root_line = QLineEdit("datasets/DF2K")
        self.lq_root_browse_btn = QPushButton("浏览...")
        self.lq_root_browse_btn.clicked.connect(lambda: self.browse_folder(self.lq_root_line))
        dataset_layout.addWidget(self.lq_root_line, 2, 1)
        dataset_layout.addWidget(self.lq_root_browse_btn, 2, 2)

        dataset_layout.addWidget(QLabel("元信息文件路径:"), 3, 0)
        self.meta_info_line = QLineEdit("datasets/DF2K/meta_info/meta_info_DIV2K_sub_pair.txt")
        self.meta_info_browse_btn = QPushButton("浏览...")
        self.meta_info_browse_btn.clicked.connect(self.browse_meta_info)
        dataset_layout.addWidget(self.meta_info_line, 3, 1)
        dataset_layout.addWidget(self.meta_info_browse_btn, 3, 2)

        main_layout.addWidget(dataset_group)

        # 训练参数组
        train_params_group = QGroupBox("训练参数")
        train_params_layout = QGridLayout(train_params_group)

        train_params_layout.addWidget(QLabel("GPU设备:"), 0, 0)
        self.gpu_combo = QComboBox()
        self.gpu_combo.addItems(["0"])  # 默认单GPU
        train_params_layout.addWidget(self.gpu_combo, 0, 1)

        train_params_layout.addWidget(QLabel("自动恢复训练:"), 0, 2)
        self.auto_resume_check = QCheckBox()
        self.auto_resume_check.setChecked(True)
        train_params_layout.addWidget(self.auto_resume_check, 0, 3)

        main_layout.addWidget(train_params_group)

        # 日志组
        log_group = QGroupBox("训练日志")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(300)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        main_layout.addWidget(log_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.save_config_btn = QPushButton("保存配置")
        self.save_config_btn.clicked.connect(self.save_config)
        self.start_train_btn = QPushButton("开始训练")
        self.start_train_btn.clicked.connect(self.start_training)
        self.cancel_train_btn = QPushButton("取消训练")
        self.cancel_train_btn.clicked.connect(self.cancel_training)
        self.cancel_train_btn.setEnabled(False)

        button_layout.addWidget(self.save_config_btn)
        button_layout.addWidget(self.start_train_btn)
        button_layout.addWidget(self.cancel_train_btn)
        main_layout.addLayout(button_layout)

    def browse_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择配置文件", "", "YAML Files (*.yml *.yaml)")
        if file_path:
            self.config_line.setText(file_path)

    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            line_edit.setText(folder)

    def browse_meta_info(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择元信息文件", "", "Text Files (*.txt)")
        if file_path:
            self.meta_info_line.setText(file_path)

    def save_config(self):
        """保存配置到YAML文件"""
        try:
            config_path = self.config_line.text()
            if not config_path:
                QMessageBox.warning(self, "警告", "请指定配置文件路径!")
                return

            # 创建配置内容，匹配finetune_realesrgan_x4plus.yml格式
            config_content = f"""# general settings
    name: finetune_RealESRGANx4plus_PAIRDATA
    model_type: RealESRGANModel
    scale: 4
    num_gpu: 1
    manual_seed: 0

    # ----------------- options for synthesizing training data in RealESRGANModel ----------------- #
    # USM the ground-truth
    l1_gt_usm: True
    percep_gt_usm: True
    gan_gt_usm: False

    # the first degradation process
    resize_prob: [0.2, 0.7, 0.1]  # up, down, keep
    resize_range: [0.15, 1.5]
    gaussian_noise_prob: 0.5
    noise_range: [1, 30]
    poisson_scale_range: [0.05, 3]
    gray_noise_prob: 0.4
    jpeg_range: [30, 95]

    # the second degradation process
    second_blur_prob: 0.8
    resize_prob2: [0.3, 0.4, 0.3]  # up, down, keep
    resize_range2: [0.3, 1.2]
    gaussian_noise_prob2: 0.5
    noise_range2: [1, 25]
    poisson_scale_range2: [0.05, 2.5]
    gray_noise_prob2: 0.4
    jpeg_range2: [30, 95]

    gt_size: 256
    queue_size: 180

    # dataset and data loader settings
    datasets:
      train:
        name: {self.dataset_name_line.text()}
        type: RealESRGANPairedDataset
        dataroot_gt: {self.gt_root_line.text()}
        dataroot_lq: {self.lq_root_line.text()}
        meta_info: {self.meta_info_line.text()}
        io_backend:
          type: disk

        gt_size: 256
        use_hflip: True
        use_rot: False

        # data loader
        use_shuffle: true
        num_worker_per_gpu: 4
        batch_size_per_gpu: 4
        dataset_enlarge_ratio: 1
        prefetch_mode: ~

    # network structures
    network_g:
      type: RRDBNet
      num_in_ch: 3
      num_out_ch: 3
      num_feat: 64
      num_block: 23
      num_grow_ch: 32

    network_d:
      type: UNetDiscriminatorSN
      num_in_ch: 3
      num_feat: 64
      skip_connection: True

    # path
    path:
      # use the pre-trained Real-ESRNet model
      pretrain_network_g: H:\pycharm_project\PI-MAPP\project\huaweiyun_Camera\Real-ESRGAN\experiments\pretrained_models\RealESRGAN_x4plus.pth
      param_key_g: params_ema
      strict_load_g: true
      pretrain_network_d: H:\pycharm_project\PI-MAPP\project\huaweiyun_Camera\Real-ESRGAN\experiments\pretrained_models\RealESRGAN_x4plus_netD.pth
      param_key_d: params
      strict_load_d: true
      resume_state: ~

    # training settings
    train:
      ema_decay: 0.999
      optim_g:
        type: Adam
        lr: !!float 1e-4
        weight_decay: 0
        betas: [0.9, 0.99]
      optim_d:
        type: Adam
        lr: !!float 1e-4
        weight_decay: 0
        betas: [0.9, 0.99]

      scheduler:
        type: MultiStepLR
        milestones: [400000]
        gamma: 0.5

      total_iter: 400000
      warmup_iter: -1  # no warm up

      # losses
      pixel_opt:
        type: L1Loss
        loss_weight: 1.0
        reduction: mean
      # perceptual loss (content and style losses)
      perceptual_opt:
        type: PerceptualLoss
        layer_weights:
          # before relu
          'conv1_2': 0.1
          'conv2_2': 0.1
          'conv3_4': 1
          'conv4_4': 1
          'conv5_4': 1
        vgg_type: vgg19
        use_input_norm: true
        perceptual_weight: !!float 1.0
        style_weight: 0
        range_norm: false
        criterion: l1
      # gan loss
      gan_opt:
        type: GANLoss
        gan_type: vanilla
        real_label_val: 1.0
        fake_label_val: 0.0
        loss_weight: !!float 1e-1

      net_d_iters: 1
      net_d_init_iters: 0

    # logging settings
    logger:
      print_freq: 100
      save_checkpoint_freq: !!float 5e3
      use_tb_logger: true
      wandb:
        project: ~
        resume_id: ~

    # dist training settings
    dist_params:
      backend: nccl
      port: 29500
    """

            # 确保目录存在
            config_dir = os.path.dirname(config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)

            # 写入配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)

            QMessageBox.information(self, "成功", f"配置已保存到: {config_path}")
            self.log_text.append(f"配置已保存到: {config_path}")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存配置失败: {str(e)}")

    def start_training(self):
        config_path = self.config_line.text()
        if not config_path:
            QMessageBox.warning(self, "警告", "请指定配置文件路径!")
            return

        if not os.path.exists(config_path):
            reply = QMessageBox.question(self, "配置文件不存在",
                                         "配置文件不存在，是否要创建默认配置文件?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.save_config()
            else:
                return

        # 禁用按钮并显示进度条
        self.start_train_btn.setEnabled(False)
        self.cancel_train_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.log_text.clear()

        # 启动训练线程
        self.train_thread = TrainThread(config_path)
        self.train_thread.log_updated.connect(self.log_text.append)
        self.train_thread.finished_signal.connect(self.on_training_finished)
        self.train_thread.start()

    def cancel_training(self):
        if self.train_thread and self.train_thread.isRunning():
            self.train_thread.terminate()
            self.train_thread.wait()
            self.on_training_finished(False, "训练已取消")

    def on_training_finished(self, success, message):
        self.start_train_btn.setEnabled(True)
        self.cancel_train_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        if success:
            QMessageBox.information(self, "完成", message)
        else:
            QMessageBox.warning(self, "错误", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RealESRGANTrainUI()
    window.show()
    sys.exit(app.exec())
