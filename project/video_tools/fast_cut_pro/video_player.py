from __future__ import annotations

import cv2
import numpy as np
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal, QObject, QUrl
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class VideoPlayer(QObject):
    position_changed = Signal(float)  # current seconds
    duration_changed = Signal(float)  # duration seconds

    def __init__(self) -> None:
        super().__init__()
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet("""
            background-color: black;
            border-radius: 3px;
        """)
        # 添加以下代码来限制标签大小行为
        self._label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._label.setMinimumSize(320, 240)  # 设置最小尺寸
        self._label.setMaximumSize(1920, 1080)  # 设置最大尺寸，防止过度放大
        self._cap: Optional[cv2.VideoCapture] = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._playing = False

        # 音频播放（与视频同步）
        self._audio_output = QAudioOutput()
        self._media = QMediaPlayer()
        self._media.setAudioOutput(self._audio_output)

        self.current_time_seconds: float = 0.0
        self.current_frame_index: int = 0
        self.duration_seconds: float = 0.0
        self.fps: float = 0.0
        self.total_frames: int = 0
        self._sync_counter = 0

    def widget(self) -> QLabel:
        return self._label

    def load(self, path: str) -> None:
        self.unload()
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise RuntimeError(f"无法打开视频: {path}")
        self._cap = cap
        self.fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        self.duration_seconds = self.total_frames / self.fps if self.fps > 0 else 0.0
        self.duration_changed.emit(self.duration_seconds)
        # 配置音频源
        self._media.setSource(QUrl.fromLocalFile(path))
        self.seek_ratio(0.0)
        self.play()

    def unload(self) -> None:
        self.pause()
        if self._cap is not None:
            self._cap.release()
        self._cap = None
        # 停止音频
        self._media.stop()
        self.current_time_seconds = 0.0
        self.current_frame_index = 0
        self.duration_seconds = 0.0
        self._label.setText("添加视频后开始预览")

    def play(self) -> None:
        if self._cap is None:
            return
        if not self._playing:
            # 更精确地计算播放间隔
            interval_ms = int(1000.0 / (self.fps or 30.0))
            # 使用更精确的定时器
            self._timer.setTimerType(Qt.PreciseTimer)
            self._timer.start(max(1, interval_ms))  # 最小间隔设为1ms
            self._playing = True
            self._media.play()

    def pause(self) -> None:
        if self._playing:
            self._timer.stop()
            self._playing = False
            self._media.pause()

    def toggle_play(self) -> None:
        if self._playing:
            self.pause()
        else:
            self.play()

    def seek_ratio(self, ratio: float) -> None:
        if self._cap is None or self.total_frames <= 0:
            return
        ratio = min(max(ratio, 0.0), 1.0)
        frame_idx = int(ratio * (self.total_frames - 1))

        # 先暂停媒体播放以避免同步问题
        was_playing = self._playing
        if was_playing:
            self._media.pause()

        self._seek_frame(frame_idx)

        # 同步音频位置（毫秒）
        if self.duration_seconds > 0:
            ms = int(ratio * self.duration_seconds * 1000)
            self._media.setPosition(ms)

            # 如果之前在播放，则重新开始播放
            if was_playing:
                self._media.play()


    def _seek_frame(self, frame_idx: int) -> None:
        if self._cap is None:
            return
        frame_idx = int(np.clip(frame_idx, 0, max(0, self.total_frames - 1)))
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = self._cap.read()
        if not ok:
            return
        self.current_frame_index = frame_idx
        self.current_time_seconds = frame_idx / (self.fps or 25.0)
        self._show_frame(frame)
        self.position_changed.emit(self.current_time_seconds)

    def _on_tick(self) -> None:
        if self._cap is None:
            return
        ok, frame = self._cap.read()
        if not ok:
            # 到尾部后停住
            self.pause()
            return
        self.current_frame_index = int(self._cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.current_time_seconds = self.current_frame_index / (self.fps or 25.0)
        self._show_frame(frame)
        self.position_changed.emit(self.current_time_seconds)

        # 同步音频位置，确保音画同步
        self._sync_counter += 1
        if self._sync_counter % 10 == 0 and self.duration_seconds > 0:
            expected_ms = int(self.current_time_seconds * 1000)
            actual_ms = self._media.position()
            if abs(actual_ms - expected_ms) > 5000 and self._playing:
                self._media.setPosition(expected_ms)
        if self._sync_counter >= 100:  # 重置计数器
            self._sync_counter = 0

    def _show_frame(self, frame: np.ndarray) -> None:
        h, w = frame.shape[:2]
        # 转换颜色格式
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 创建 QImage
        bytes_per_line = 3 * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg)

        # 总是根据标签大小进行缩放，保持宽高比
        label_size = self._label.size()
        scaled = pix.scaled(label_size, Qt.KeepAspectRatio, Qt.FastTransformation)
        self._label.setPixmap(scaled)






