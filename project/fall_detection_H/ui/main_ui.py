import sys
import cv2
import numpy as np
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from datetime import datetime


class VideoWidget(QWidget):
    """自定义视频显示组件"""

    def __init__(self, camera_id=0, parent=None):
        super().__init__(parent)
        self.camera_id = camera_id
        self.current_frame = None
        self.detection_state = "NORMAL"  # NORMAL, FALL, WALKING
        self.confidence = 0.0
        self.setMinimumSize(400, 300)

    def update_frame(self, frame, state="NORMAL", confidence=0.0):
        self.current_frame = frame
        self.detection_state = state
        self.confidence = confidence
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()

        # 绘制背景
        if self.detection_state == "FALL":
            # 跌倒状态 - 红色渐变背景
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor("#DC2626"))
            gradient.setColorAt(1, QColor("#B91C1C"))
            painter.fillRect(rect, gradient)
        elif self.detection_state == "WALKING":
            # 行走状态 - 蓝色渐变背景
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor("#3B82F6"))
            gradient.setColorAt(1, QColor("#2563EB"))
            painter.fillRect(rect, gradient)
        else:
            # 正常状态 - 绿色渐变背景
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor("#10B981"))
            gradient.setColorAt(1, QColor("#059669"))
            painter.fillRect(rect, gradient)

        # 绘制视频帧
        if self.current_frame is not None:
            # 转换OpenCV图像到QImage
            frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # 缩放图像适应控件大小
            scaled_pixmap = QPixmap.fromImage(q_img).scaled(
                self.width() - 4, self.height() - 4,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            # 居中绘制
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)

        # 绘制状态覆盖层
        if self.detection_state != "NORMAL":
            overlay = QRect(0, 0, self.width(), self.height())
            painter.setPen(QPen(Qt.white, 3))
            painter.setBrush(Qt.NoBrush)

            # 绘制状态文字背景
            text_rect = QRect(10, 10, self.width() - 20, 60)
            state_gradient = QLinearGradient(text_rect.topLeft(), text_rect.bottomRight())

            if self.detection_state == "FALL":
                state_gradient.setColorAt(0, QColor("#DC2626"))
                state_gradient.setColorAt(1, QColor("#B91C1C"))
                status_text = f"⚠️ 检测到跌倒事件"
                emoji_text = "🚨"
            elif self.detection_state == "WALKING":
                state_gradient.setColorAt(0, QColor("#3B82F6"))
                state_gradient.setColorAt(1, QColor("#2563EB"))
                status_text = f"🚶 患者行走中"
                emoji_text = "✅"
            else:
                state_gradient.setColorAt(0, QColor("#10B981"))
                state_gradient.setColorAt(1, QColor("#059669"))
                status_text = f"🪑 患者坐着"
                emoji_text = "🟢"

            painter.fillRect(text_rect, state_gradient)

            # 绘制状态文字
            font = QFont("Arial", 14, QFont.Bold)
            painter.setFont(font)
            painter.setPen(Qt.white)

            # 绘制Emoji
            emoji_font = QFont("Segoe UI Emoji", 16)
            painter.setFont(emoji_font)
            painter.drawText(text_rect.x() + 10, text_rect.y() + 25, emoji_text)

            # 绘制状态信息
            painter.setFont(font)
            painter.drawText(text_rect.x() + 40, text_rect.y() + 20, status_text)
            painter.drawText(text_rect.x() + 40, text_rect.y() + 45,
                             f"置信度: {self.confidence:.2f} | 摄像头: {self.camera_id}")

        # 绘制边框装饰
        if self.detection_state == "FALL":
            painter.setPen(QPen(QColor("#DC2626"), 4, Qt.DashLine))
            painter.drawRect(5, 5, self.width() - 10, self.height() - 10)


class CameraControlPanel(QWidget):
    """摄像头控制面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("📹 摄像头监控管理")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 摄像头控制按钮区域
        button_layout = QHBoxLayout()

        self.add_camera_btn = QPushButton("➕ 添加摄像头")
        self.add_camera_btn.setObjectName("addButton")
        self.add_camera_btn.clicked.connect(self.add_camera)

        self.remove_camera_btn = QPushButton("➖ 移除摄像头")
        self.remove_camera_btn.setObjectName("removeButton")
        self.remove_camera_btn.clicked.connect(self.remove_camera)

        self.start_all_btn = QPushButton("▶️ 启动所有")
        self.start_all_btn.setObjectName("startButton")
        self.start_all_btn.clicked.connect(self.start_all_cameras)

        self.stop_all_btn = QPushButton("⏸️ 停止所有")
        self.stop_all_btn.setObjectName("stopButton")
        self.stop_all_btn.clicked.connect(self.stop_all_cameras)

        button_layout.addWidget(self.add_camera_btn)
        button_layout.addWidget(self.remove_camera_btn)
        button_layout.addWidget(self.start_all_btn)
        button_layout.addWidget(self.stop_all_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # 摄像头列表
        self.camera_list = QListWidget()
        self.camera_list.setObjectName("cameraList")
        self.camera_list.addItems([
            "📹 摄像头 1 - 病房A (在线)",
            "📹 摄像头 2 - 走廊B (在线)",
            "📹 摄像头 3 - 活动区 (离线)"
        ])
        layout.addWidget(self.camera_list)

        # 应用样式
        self.apply_styles()

    def apply_styles(self):
        style = """
        #titleLabel {
            font-size: 18px;
            font-weight: bold;
            color: #0F172A;
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #E8F5F0, stop:1 #D1E7DD);
            border-radius: 8px;
            margin: 5px;
        }

        #addButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #10B981, stop:1 #059669);
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: bold;
        }
        #addButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #059669, stop:1 #047857);
            transform: translateY(-1px);
        }

        #removeButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #EF4444, stop:1 #DC2626);
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: bold;
        }
        #removeButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #DC2626, stop:1 #B91C1C);
            transform: translateY(-1px);
        }

        #startButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #3B82F6, stop:1 #2563EB);
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: bold;
        }
        #startButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #2563EB, stop:1 #1D4ED8);
            transform: translateY(-1px);
        }

        #stopButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #F59E0B, stop:1 #D97706);
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: bold;
        }
        #stopButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #D97706, stop:1 #B45309);
            transform: translateY(-1px);
        }

        #cameraList {
            background: white;
            border: 2px solid #E2E8F0;
            border-radius: 8px;
            font-size: 14px;
            color: #0F172A;
        }

        #cameraList::item {
            padding: 8px;
            border-bottom: 1px solid #F1F5F9;
        }

        #cameraList::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #E0F2FE, stop:1 #B3E5FC);
        }
        """
        self.setStyleSheet(style)

    def add_camera(self):
        QMessageBox.information(self, "提示", "添加新摄像头功能")

    def remove_camera(self):
        QMessageBox.information(self, "提示", "移除摄像头功能")

    def start_all_cameras(self):
        QMessageBox.information(self, "提示", "启动所有摄像头")

    def stop_all_cameras(self):
        QMessageBox.information(self, "提示", "停止所有摄像头")


class StatusBar(QWidget):
    """状态栏"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # 系统时间
        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")
        layout.addWidget(self.time_label)

        layout.addStretch()

        # 检测统计
        self.stats_label = QLabel("📊 今日检测: 0次 | 跌倒事件: 0次 | 正常状态: 0次")
        self.stats_label.setObjectName("statsLabel")
        layout.addWidget(self.stats_label)

        # 系统状态
        self.system_label = QLabel("✅ 系统运行正常")
        self.system_label.setObjectName("systemLabel")
        layout.addWidget(self.system_label)

        self.apply_styles()

    def apply_styles(self):
        style = """
        #timeLabel {
            font-size: 14px;
            color: #0F172A;
            font-weight: bold;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #E8F5F0, stop:1 #D1E7DD);
            padding: 5px 10px;
            border-radius: 15px;
        }

        #statsLabel {
            font-size: 12px;
            color: #059669;
            background: rgba(16, 185, 129, 0.1);
            padding: 5px 10px;
            border-radius: 12px;
            border: 1px solid #10B981;
        }

        #systemLabel {
            font-size: 12px;
            color: #059669;
            background: rgba(16, 185, 129, 0.1);
            padding: 5px 10px;
            border-radius: 12px;
            border: 1px solid #10B981;
        }
        """
        self.setStyleSheet(style)
        self.update_time()

    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"🕒 系统时间: {current_time}")


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏥 医院摔倒实时检测系统 v2.0")
        self.setGeometry(100, 100, 1400, 900)
        self.setup_ui()
        self.apply_main_styles()

    def setup_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # 创建顶部状态栏
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)

        # 主内容区域
        content_splitter = QSplitter(Qt.Vertical)

        # 视频监控区域
        video_widget = self.create_video_monitoring_area()
        content_splitter.addWidget(video_widget)

        # 控制面板区域
        control_panel = self.create_control_panel()
        content_splitter.addWidget(control_panel)

        # 设置分割器比例
        content_splitter.setSizes([700, 200])
        main_layout.addWidget(content_splitter)

        self.setCentralWidget(central_widget)

    def create_video_monitoring_area(self):
        """创建视频监控区域"""
        video_widget = QWidget()
        layout = QVBoxLayout(video_widget)

        # 视频区域标题
        title_label = QLabel("🖥️ 实时视频监控 (4分屏)")
        title_label.setObjectName("mainTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #0F172A;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #E8F5F0, stop:1 #D1E7DD);
                border-radius: 8px;
                margin: 5px;
            }
        """)
        layout.addWidget(title_label)

        # 视频网格布局
        video_grid = QGridLayout()

        # 创建4个视频显示组件
        self.video_widgets = []
        for i in range(4):
            video_w = VideoWidget(camera_id=i + 1)
            self.video_widgets.append(video_w)

            # 设置初始状态和模拟数据
            state = "NORMAL"
            confidence = 0.0
            if i == 1:  # 模拟一个跌倒事件
                state = "FALL"
                confidence = 0.89
            elif i == 2:
                state = "WALKING"
                confidence = 0.75

            video_w.update_frame(self.create_demo_frame(), state, confidence)

            video_grid.addWidget(video_w, i // 2, i % 2)

        layout.addLayout(video_grid)
        layout.addStretch()

        return video_widget

    def create_demo_frame(self):
        """创建演示用的视频帧"""
        # 创建一个彩色渐变背景作为演示
        height, width = 480, 640
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # 创建渐变背景
        for y in range(height):
            ratio = y / height
            b = int(100 + ratio * 155)
            g = int(150 + ratio * 105)
            r = int(200 + ratio * 55)
            frame[y, :, 0] = b
            frame[y, :, 1] = g
            frame[y, :, 2] = r

        # 添加一些几何图形模拟人体
        center_x, center_y = width // 2, height // 2
        cv2.circle(frame, (center_x, center_y), 20, (255, 255, 255), -1)  # 头部

        return frame

    def create_control_panel(self):
        """创建控制面板"""
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)

        # 控制面板标题
        title_label = QLabel("⚙️ 系统控制中心")
        title_label.setObjectName("controlTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #0F172A;
                padding: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #E8F5F0, stop:1 #D1E7DD);
                border-radius: 6px;
                margin: 3px;
            }
        """)
        layout.addWidget(title_label)

        # 控制选项
        control_options = QFormLayout()

        # 置信度调节
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(30, 95)
        self.confidence_slider.setValue(70)
        self.confidence_slider.valueChanged.connect(self.on_confidence_changed)

        self.confidence_label = QLabel("置信度阈值: 70%")
        self.confidence_label.setObjectName("controlLabel")

        control_options.addRow("🎯 检测灵敏度:", self.confidence_slider)
        control_options.addRow(self.confidence_label)

        # 通知设置
        self.notification_checkbox = QCheckBox("🔔 启用跌倒事件通知")
        self.notification_checkbox.setChecked(True)
        self.notification_checkbox.stateChanged.connect(self.on_notification_changed)
        control_options.addRow("📱 通知设置:", self.notification_checkbox)

        # 主题选择
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["🌊 蓝绿渐变主题", "⚫ 深色主题", "⚪ 浅色主题"])
        self.theme_combo.setCurrentIndex(0)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        control_options.addRow("🎨 界面主题:", self.theme_combo)

        layout.addLayout(control_options)

        # 系统信息
        info_group = QGroupBox("📋 系统信息")
        info_layout = QVBoxLayout()

        self.event_count_label = QLabel("🚨 今日跌倒事件: 0 次")
        self.event_count_label.setObjectName("infoLabel")

        self.detection_count_label = QLabel("👁️ 总检测次数: 0 次")
        self.detection_count_label.setObjectName("infoLabel")

        self.camera_status_label = QLabel("📹 在线摄像头: 3 台")
        self.camera_status_label.setObjectName("infoLabel")

        info_layout.addWidget(self.event_count_label)
        info_layout.addWidget(self.detection_count_label)
        info_layout.addWidget(self.camera_status_label)
        info_group.setLayout(info_layout)

        layout.addWidget(info_group)
        layout.addStretch()

        return control_widget

    def apply_main_styles(self):
        main_style = """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                       stop:0 #E8F5F0, stop:1 #D1E7DD);
        }

        #mainTitle {
            font-size: 16px;
            font-weight: bold;
            color: #0F172A;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #E8F5F0, stop:1 #D1E7DD);
            padding: 10px;
            border-radius: 8px;
        }

        #controlTitle {
            font-size: 14px;
            font-weight: bold;
            color: #0F172A;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #E8F5F0, stop:1 #D1E7DD);
            padding: 8px;
            border-radius: 6px;
        }

        #confidenceLabel {
            font-size: 12px;
            color: #0F172A;
            font-weight: bold;
            background: rgba(16, 185, 129, 0.1);
            padding: 4px 8px;
            border-radius: 8px;
        }

        #infoLabel {
            font-size: 11px;
            color: #0F172A;
            background: rgba(59, 130, 246, 0.1);
            padding: 4px 8px;
            border-radius: 6px;
            margin: 2px;
        }

        QGroupBox {
            font-weight: bold;
            color: #0F172A;
            border: 2px solid #E2E8F0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #0F172A;
        }

        QSlider::groove:horizontal {
            border: 1px solid #E2E8F0;
            height: 8px;
            background: #F1F5F9;
            border-radius: 4px;
        }

        QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                       stop:0 #10B981, stop:1 #059669);
            border: 1px solid #047857;
            width: 16px;
            margin: -2px 0;
            border-radius: 8px;
        }

        QSlider::handle:horizontal:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                       stop:0 #059669, stop:1 #047857);
        }

        QCheckBox {
            spacing: 8px;
            font-size: 12px;
            color: #0F172A;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #10B981;
            border-radius: 4px;
            background: white;
        }

        QCheckBox::indicator:checked {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 #10B981, stop:1 #059669);
            border: 2px solid #047857;
        }

        QComboBox {
            padding: 5px;
            border: 2px solid #E2E8F0;
            border-radius: 6px;
            background: white;
            font-size: 12px;
            color: #0F172A;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #E2E8F0;
            border-left-style: solid;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        """
        self.setStyleSheet(main_style)

    def on_confidence_changed(self, value):
        self.confidence_label.setText(f"置信度阈值: {value}%")

    def on_notification_changed(self, state):
        if state == Qt.Checked:
            print("通知已启用")
        else:
            print("通知已禁用")

    def on_theme_changed(self, index):
        themes = ["蓝绿渐变", "深色主题", "浅色主题"]
        print(f"切换到主题: {themes[index]}")


def main():
    app = QApplication(sys.argv)

    # 设置应用程序属性
    app.setApplicationName("医院摔倒实时检测系统")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("医疗科技公司")

    # 创建主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()