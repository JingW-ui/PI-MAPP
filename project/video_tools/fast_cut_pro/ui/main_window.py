from __future__ import annotations

import os
import datetime
from typing import Optional, List

import cv2
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QAction, QKeySequence, QFont
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QLabel,
    QPushButton,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QProgressBar,
    QLineEdit,
    QMessageBox,
)

from project.video_tools.fast_cut_pro.video_player import VideoPlayer
from project.video_tools.fast_cut_pro.models import VideoItem, MarkPoint

from project.video_tools.fast_cut_pro.extractor import batch_extract


class MainWindow(QMainWindow):
    marks_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Fast Cut")
        self.resize(1100, 480)

        self.video_items: List[VideoItem] = []
        self.current_video: Optional[VideoItem] = None

        self._init_actions()
        self._init_ui()
        self._connect_signals()

    def _init_actions(self) -> None:
        self.action_add_videos = QAction("添加视频", self)
        self.action_remove_video = QAction("移除视频", self)
        # 在 _init_actions 方法中添加
        self.action_add_mark = QAction("添加标记", self)
        self.action_add_mark.setShortcut(QKeySequence("M"))
        self.action_add_mark.triggered.connect(self._on_add_mark)
        self.addAction(self.action_add_mark)  # 将动作添加到主窗口

        self.action_remove_mark = QAction("删除标记", self)
        self.action_remove_mark.setShortcut(QKeySequence("D"))
        self.action_remove_mark.triggered.connect(self._on_remove_mark)
        self.addAction(self.action_remove_mark)  # 将动作添加到主窗口

    def _init_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # 左侧：视频列表 + 每视频时长设置
        left_box = QVBoxLayout()

        # 视频列表区域
        video_group = QGroupBox("视频列表")
        video_layout = QVBoxLayout(video_group)
        self.video_list = QListWidget()
        self.video_list.setSelectionMode(QAbstractItemView.SingleSelection)
        # 优化视频列表样式
        self.video_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
            }
            QListWidget::item {
                padding: 9px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        video_layout.addWidget(self.video_list)
        left_box.addWidget(video_group, 3)

        # 添加视频操作按钮到视频列表下方
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add")  # 简化为英文
        btn_remove = QPushButton("Remove")  # 简化为英文
        btn_batch_load = QPushButton("Batch")  # 新增批量加载按钮
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addWidget(btn_batch_load)
        left_box.addLayout(btn_layout)

        # 连接按钮信号
        btn_add.clicked.connect(self.action_add_videos.trigger)
        btn_remove.clicked.connect(self.action_remove_video.trigger)
        btn_batch_load.clicked.connect(self._on_batch_load_videos)
        # 视频信息面板
        info_group = QGroupBox("视频信息")
        info_layout = QFormLayout(info_group)
        self.lbl_device = QLabel("-")
        self.lbl_duration = QLabel("-")
        self.lbl_size = QLabel("-")
        self.lbl_date = QLabel("-")
        self.lbl_resolution = QLabel("-")  # 新增分辨率信息
        self.lbl_framerate = QLabel("-")  # 新增帧率信息
        info_layout.addRow("拍摄设备:", self.lbl_device)
        info_layout.addRow("时长:", self.lbl_duration)
        info_layout.addRow("大小:", self.lbl_size)
        info_layout.addRow("日期:", self.lbl_date)
        info_layout.addRow("分辨率:", self.lbl_resolution)  # 添加分辨率行
        info_layout.addRow("帧率:", self.lbl_framerate)  # 添加帧率行
        left_box.addWidget(info_group, 1)

        top_center_box = QVBoxLayout()
        self.player = VideoPlayer()
        top_center_box.addWidget(self.player.widget(),6)

        slider_row = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        # 设置滑块样式
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)
        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setMinimumWidth(80)  # 确保时间标签有足够宽度
        slider_row.addWidget(self.slider, 1)
        slider_row.addWidget(self.lbl_time)
        top_center_box.addLayout(slider_row)

        controls = QHBoxLayout()
        self.btn_play = QPushButton("播放/暂停")
        self.btn_add_mark = QPushButton("添加标记")
        self.btn_remove_mark = QPushButton("删除所选标记")

        # 增大按钮尺寸和字体
        button_font = QFont()
        button_font.setPointSize(10)
        self.btn_play.setFont(button_font)
        self.btn_play.setMinimumHeight(35)
        self.btn_add_mark.setFont(button_font)
        self.btn_add_mark.setMinimumHeight(35)
        self.btn_remove_mark.setFont(button_font)
        self.btn_remove_mark.setMinimumHeight(35)
        controls.addStretch(1)
        controls.addWidget(self.btn_play)
        controls.addWidget(self.btn_add_mark)
        controls.addWidget(self.btn_remove_mark)

        self.spin_pre = QDoubleSpinBox()
        self.spin_pre.setRange(0.0, 30.0)
        self.spin_pre.setSingleStep(0.1)
        self.spin_pre.setValue(1.5)
        self.spin_post = QDoubleSpinBox()
        self.spin_post.setRange(0.0, 30.0)
        self.spin_post.setSingleStep(0.1)
        self.spin_post.setValue(1.5)

        # 增大数值调节框尺寸和字体
        spin_font = QFont()
        spin_font.setPointSize(10)
        self.spin_pre.setFont(spin_font)
        self.spin_pre.setMinimumHeight(35)
        self.spin_pre.setMinimumWidth(70)
        self.spin_post.setFont(spin_font)
        self.spin_post.setMinimumHeight(35)
        self.spin_post.setMinimumWidth(70)

        label_font = QFont()
        label_font.setPointSize(10)
        pre_label = QLabel("前(秒)")
        post_label = QLabel("后(秒)")
        pre_label.setFont(label_font)
        post_label.setFont(label_font)

        controls.addWidget(pre_label)
        controls.addWidget(self.spin_pre)
        controls.addWidget(post_label)
        controls.addWidget(self.spin_post)
        controls.addStretch(1)
        top_center_box.addLayout(controls,2)

        top_center_widget = QWidget()
        top_center_widget.setLayout(top_center_box)


        center_splitter = QSplitter(Qt.Vertical)
        center_splitter.addWidget(top_center_widget)

        # 右侧：输出设置 + 批量截取
        right_box = QVBoxLayout()
        out_group = QGroupBox("输出设置")
        out_form = QFormLayout(out_group)
        self.edit_output_dir = QLineEdit()
        self.btn_choose_output = QPushButton("选择目录")
        out_row = QHBoxLayout()
        out_row.addWidget(self.edit_output_dir, 1)
        out_row.addWidget(self.btn_choose_output)
        out_form.addRow("输出目录", out_row)

        self.btn_extract = QPushButton("统一开始截取")
        # 优化进度条样式
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                background-color: #f0f0f0;
            }

            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)

        # 在 _init_ui 方法中找到表格初始化部分，修改选择模式
        self.table_marks = QTableWidget(0, 2)
        self.table_marks.setHorizontalHeaderLabels(["时间(s)", "帧索引"])
        # 修改为多选模式
        self.table_marks.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table_marks.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_marks.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_marks.verticalHeader().setVisible(False)

        # 简约化标记列表样式
        self.table_marks.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: #ffffff;
                selection-background-color: #e6f0ff;
                selection-color: #000000;
                gridline-color: #f0f0f0;
            }

            QTableWidget::item {
                padding: 4px 2px;
                border-bottom: 1px solid #fff5f5;
            }
            QHeaderView::section {
                background-color: #fafafa;
                padding: 8px 4px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                font-weight: normal;
                color: #666666;
            }
        """)

        right_box.addWidget(out_group)
        right_box.addWidget(self.btn_extract)
        right_box.addWidget(self.progress)
        marks_header_layout = QHBoxLayout()
        marks_header_layout.addWidget(QLabel("标记列表"))

        # 添加模式切换按钮
        self.btn_marks_mode = QPushButton("显示所有视频标记")
        self.btn_marks_mode.setCheckable(True)
        self.btn_marks_mode.setChecked(False)  # 默认显示单个视频标记
        self.btn_marks_mode.clicked.connect(self._on_marks_mode_changed)
        marks_header_layout.addWidget(self.btn_marks_mode)
        marks_header_layout.addStretch(1)

        right_box.addLayout(marks_header_layout)
        right_box.addWidget(self.table_marks)

        # 将三列放入可拖拽的水平分割条
        left_widget = QWidget()
        left_widget.setLayout(left_box)
        right_widget = QWidget()
        right_widget.setLayout(right_box)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(center_splitter)
        main_splitter.addWidget(right_widget)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 8)
        main_splitter.setStretchFactor(2, 2)

        layout.addWidget(main_splitter)

    def _connect_signals(self) -> None:
        self.action_add_videos.triggered.connect(self._on_add_videos)
        self.action_remove_video.triggered.connect(self._on_remove_selected_video)

        self.video_list.currentRowChanged.connect(self._on_video_selected)
        self.spin_pre.valueChanged.connect(self._on_duration_changed)
        self.spin_post.valueChanged.connect(self._on_duration_changed)

        self.btn_play.clicked.connect(self.player.toggle_play)
        self.btn_add_mark.clicked.connect(self._on_add_mark)
        self.btn_remove_mark.clicked.connect(self._on_remove_mark)

        self.slider.sliderMoved.connect(self._on_slider_moved)
        self.player.position_changed.connect(self._on_player_position_changed)
        self.player.duration_changed.connect(self._on_player_duration_changed)

        self.btn_choose_output.clicked.connect(self._on_choose_output_dir)
        self.btn_extract.clicked.connect(self._on_start_extract)

        self.btn_marks_mode.clicked.connect(self._on_marks_mode_changed)

    # 添加模式切换处理方法
    def _on_marks_mode_changed(self) -> None:
        """处理标记显示模式切换"""
        if self.btn_marks_mode.isChecked():
            self.btn_marks_mode.setText("显示单个视频标记")
        else:
            self.btn_marks_mode.setText("显示所有视频标记")
        self._refresh_marks_table()

    # 修改 _on_remove_mark 方法
    def _on_remove_mark(self) -> None:
        if not self.current_video:
            return

        # 获取所有选中的行
        selected_rows = set()
        for item in self.table_marks.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            return

        # 转换为排序后的列表（降序），以便从后往前删除
        sorted_rows = sorted(list(selected_rows), reverse=True)

        # 删除选中的标记
        for row in sorted_rows:
            if 0 <= row < len(self.current_video.marks):
                del self.current_video.marks[row]

        self._refresh_marks_table()

    # 文件与列表
    def _on_add_videos(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择视频文件", os.getcwd(), "视频文件 (*.mp4 *.mov *.mkv *.avi)"
        )
        if not files:
            return
        for path in files:
            item = VideoItem(path=path)
            self.video_items.append(item)
            self.video_list.addItem(QListWidgetItem(os.path.basename(path)))

        if self.video_list.count() > 0 and self.video_list.currentRow() < 0:
            self.video_list.setCurrentRow(0)

    def _on_remove_selected_video(self) -> None:
        row = self.video_list.currentRow()
        if row < 0:
            return
        self.video_list.takeItem(row)
        del self.video_items[row]
        self.current_video = None
        self.player.unload()
        self._refresh_marks_table()

    def _on_video_selected(self, row: int) -> None:
        if row < 0 or row >= len(self.video_items):
            # 清空信息显示
            self.lbl_device.setText("-")
            self.lbl_duration.setText("-")
            self.lbl_size.setText("-")
            self.lbl_date.setText("-")
            return

        self.current_video = self.video_items[row]
        self.spin_pre.setValue(self.current_video.pre_seconds)
        self.spin_post.setValue(self.current_video.post_seconds)
        self.player.load(self.current_video.path)
        self._refresh_marks_table()
        self._suggest_output_dir()

        # 更新视频信息显示
        self._update_video_info(self.current_video)

    def _on_batch_load_videos(self) -> None:
        """批量从文件夹加载视频"""
        directory = QFileDialog.getExistingDirectory(self, "选择视频文件夹", os.getcwd())
        if not directory:
            return

        # 支持的视频文件扩展名
        video_extensions = {'.mp4', '.mov', '.mkv', '.avi', '.wmv', '.flv', '.webm'}

        # 遍历文件夹中的所有视频文件
        video_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if os.path.splitext(file)[1].lower() in video_extensions:
                    video_files.append(os.path.join(root, file))

        if not video_files:
            QMessageBox.information(self, "提示", "该文件夹中没有找到视频文件。")
            return

        # 添加找到的视频文件
        for path in video_files:
            # 检查是否已存在
            if not any(item.path == path for item in self.video_items):
                item = VideoItem(path=path)
                self.video_items.append(item)
                self.video_list.addItem(QListWidgetItem(os.path.basename(path)))

        # 如果是第一次添加，选中第一个
        if self.video_list.count() > 0 and self.video_list.currentRow() < 0:
            self.video_list.setCurrentRow(0)

        QMessageBox.information(self, "完成", f"成功添加 {len(video_files)} 个视频文件。")

    def _update_video_info(self, video_item: VideoItem) -> None:
        """更新视频信息显示"""
        try:
            # 获取文件信息
            stat = os.stat(video_item.path)
            file_size = stat.st_size
            modified_time = datetime.datetime.fromtimestamp(stat.st_mtime)

            # 格式化文件大小
            size_str = self._format_file_size(file_size)

            # 获取视频信息（从player获取）
            duration = self.player.duration_seconds if self.player else 0
            fps = self.player.fps if self.player else 0
            total_frames = self.player.total_frames if self.player else 0

            # 获取视频分辨率
            resolution = "未知"
            if self.player and self.player._cap:
                width = int(self.player._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.player._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                if width > 0 and height > 0:
                    resolution = f"{width}×{height}"

            # 获取设备信息：首先尝试从文件名解析
            device_name = "未知"
            basename = os.path.basename(video_item.path)
            filename_without_ext = os.path.splitext(basename)[0]
            if '_' in filename_without_ext:
                device_name = filename_without_ext.split('_')[0]

            # 设置显示信息
            self.lbl_device.setText(device_name)
            self.lbl_duration.setText(self._fmt_time(duration))
            self.lbl_size.setText(size_str)
            self.lbl_date.setText(modified_time.strftime("%Y-%m-%d %H:%M:%S"))
            self.lbl_resolution.setText(resolution)  # 设置分辨率
            self.lbl_framerate.setText(f"{fps:.2f} fps")  # 设置帧率
        except Exception:
            # 出现错误时显示默认值
            self.lbl_device.setText("-")
            self.lbl_duration.setText("-")
            self.lbl_size.setText("-")
            self.lbl_date.setText("-")
            self.lbl_resolution.setText("-")
            self.lbl_framerate.setText("-")

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    # 播放器与进度
    def _on_slider_moved(self, value: int) -> None:
        self.player.seek_ratio(value / 1000.0)

    def _on_player_position_changed(self, current_sec: float) -> None:
        duration = self.player.duration_seconds or 0.0
        ratio = 0 if duration <= 0 else min(max(current_sec / duration, 0.0), 1.0)
        self.slider.blockSignals(True)
        self.slider.setValue(int(ratio * 1000))
        self.slider.blockSignals(False)
        self.lbl_time.setText(f"{self._fmt_time(current_sec)} / {self._fmt_time(duration)}")

    def _on_player_duration_changed(self, duration_sec: float) -> None:
        self.lbl_time.setText(f"00:00 / {self._fmt_time(duration_sec)}")

    # 标记
    def _on_add_mark(self) -> None:
        if not self.current_video:
            return
        t = self.player.current_time_seconds or 0.0
        frame_idx = self.player.current_frame_index or 0

        # 获取视频总帧数和帧率
        total_frames = self.player.total_frames if self.player else 0
        fps = self.player.fps if self.player else 25.0

        if total_frames > 0 and fps > 0:
            # 检查前后是否足够，不够则调整
            pre_seconds = self.current_video.pre_seconds
            post_seconds = self.current_video.post_seconds

            # 检查前面是否足够
            if t < pre_seconds:
                # 如果当前时间小于前导时间，则将标记时间设为前导时间
                t = pre_seconds
                frame_idx = int(t * fps)

            # 检查后面是否足够
            total_duration = total_frames / fps
            if t > (total_duration - post_seconds):
                # 如果剩余时间不足后导时间，则将标记时间调整为能保证后导时间的位置
                t = max(pre_seconds, total_duration - post_seconds)
                frame_idx = int(t * fps)

            # 确保帧索引在有效范围内
            frame_idx = max(0, min(frame_idx, total_frames - 1))

        self.current_video.marks.append(MarkPoint(time_seconds=t, frame_index=frame_idx))
        self._refresh_marks_table()

    def _on_remove_mark(self) -> None:
        if not self.current_video:
            return
        row = self.table_marks.currentRow()
        if row < 0 or row >= len(self.current_video.marks):
            return
        del self.current_video.marks[row]
        self._refresh_marks_table()

    # 修改 _refresh_marks_table 方法以支持两种模式
    def _refresh_marks_table(self) -> None:
        self.table_marks.setRowCount(0)

        # 显示所有视频标记模式
        if self.btn_marks_mode.isChecked():
            if not self.video_items:
                return

            # 创建三列表头
            self.table_marks.setColumnCount(3)
            self.table_marks.setHorizontalHeaderLabels(["时间(s)", "帧索引", "视频文件"])

            # 收集所有视频的标记
            all_marks = []
            for video_item in self.video_items:
                for mark in video_item.marks:
                    all_marks.append((mark, video_item))

            # 按时间排序
            all_marks.sort(key=lambda x: x[0].time_seconds)

            # 显示所有标记
            for mark, video_item in all_marks:
                r = self.table_marks.rowCount()
                self.table_marks.insertRow(r)
                self.table_marks.setItem(r, 0, QTableWidgetItem(f"{mark.time_seconds:.3f}"))
                self.table_marks.setItem(r, 1, QTableWidgetItem(str(mark.frame_index)))
                self.table_marks.setItem(r, 2, QTableWidgetItem(os.path.basename(video_item.path)))
        else:
            # 显示单个视频标记模式
            if not self.current_video:
                return

            # 恢复两列表头
            self.table_marks.setColumnCount(2)
            self.table_marks.setHorizontalHeaderLabels(["时间(s)", "帧索引"])

            # 显示当前视频的标记
            for mk in self.current_video.marks:
                r = self.table_marks.rowCount()
                self.table_marks.insertRow(r)
                self.table_marks.setItem(r, 0, QTableWidgetItem(f"{mk.time_seconds:.3f}"))
                self.table_marks.setItem(r, 1, QTableWidgetItem(str(mk.frame_index)))

    # 时长设置
    def _on_duration_changed(self) -> None:
        if not self.current_video:
            return
        self.current_video.pre_seconds = float(self.spin_pre.value())
        self.current_video.post_seconds = float(self.spin_post.value())

    # 输出与截取
    def _suggest_output_dir(self) -> None:
        if not self.current_video:
            return
        base_dir = os.path.dirname(self.current_video.path)
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        suggested = os.path.join(base_dir, date_str)
        self.edit_output_dir.setText(suggested)

    def _on_choose_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录", os.getcwd())
        if directory:
            self.edit_output_dir.setText(directory)

    def _on_start_extract(self) -> None:
        if not self.video_items:
            QMessageBox.warning(self, "提示", "请先添加视频并完成标记！")
            return
        output_dir = self.edit_output_dir.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "提示", "请选择输出目录！")
            return
        os.makedirs(output_dir, exist_ok=True)

        total_jobs = sum(len(v.marks) for v in self.video_items)
        if total_jobs == 0:
            QMessageBox.information(self, "提示", "没有标记，无需截取。")
            return

        self.progress.setValue(0)
        processed = 0

        def on_progress(_path: str) -> None:
            nonlocal processed, total_jobs
            processed += 1
            pct = int(processed / total_jobs * 100)
            self.progress.setValue(pct)

        try:
            batch_extract(self.video_items, output_dir, on_progress)
            QMessageBox.information(self, "完成", "批量截取完成！")
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "错误", f"截取失败：{e}")

    # utils
    @staticmethod
    def _fmt_time(sec: float) -> str:
        sec = max(0.0, float(sec))
        m = int(sec // 60)
        s = int(sec % 60)
        return f"{m:02d}:{s:02d}"


