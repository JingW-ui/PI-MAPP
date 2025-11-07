from __future__ import annotations

import os
import shutil
import subprocess
from typing import Callable, List

from models import VideoItem


def _fmt_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def _run_ffmpeg_cut(src: str, start_sec: float, duration_sec: float, out_path: str) -> None:
    """Run ffmpeg to cut a clip with robust fallbacks.

    Order:
    1) Stream copy (fastest; keyframe aligned)
    2) mpeg4 video + copy audio (broad compatibility)
    3) mpeg4 video + aac audio (if audio copy不兼容)

    Never uses preset to avoid 'Unrecognized option preset' errors.
    """

    if shutil.which("ffmpeg") is None:
        raise RuntimeError("未找到 ffmpeg，请先安装并将其加入系统 PATH")

    start_ts = _fmt_time(start_sec)
    dur_ts = _fmt_time(duration_sec)

    base = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        start_ts,
        "-i",
        src,
        "-t",
        dur_ts,
    ]

    attempts = [
        # 2) mpeg4 + 音频copy（兼容性广，无 preset）
        base + ["-c:v", "mpeg4", "-q:v", "3", "-c:a", "copy", "-movflags", "+faststart", out_path],
        # 1) 纯拷贝（最快）
        base + ["-c", "copy", "-movflags", "+faststart", out_path],
        # 3) mpeg4 + aac（当音频流不支持copy时）
        base + ["-c:v", "mpeg4", "-q:v", "3", "-c:a", "aac", "-movflags", "+faststart", out_path],
    ]

    last_err: Exception | None = None
    for cmd in attempts:
        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except Exception as e:  # noqa: BLE001
            last_err = e
    if last_err is not None:
        raise last_err


def batch_extract(videos: List[VideoItem], output_dir: str, on_progress: Callable[[str], None] | None = None) -> None:
    os.makedirs(output_dir, exist_ok=True)
    for v in videos:
        if not v.marks:
            continue
        base = os.path.splitext(os.path.basename(v.path))[0]
        for idx, mk in enumerate(v.marks, start=1):
            start = max(0.0, mk.time_seconds - max(0.0, v.pre_seconds))
            duration = max(0.01, v.pre_seconds + v.post_seconds)
            filename = f"{base}_cut_{idx:03d}.mp4"
            out_path = os.path.join(output_dir, filename)
            _run_ffmpeg_cut(v.path, start, duration, out_path)
            if on_progress:
                on_progress(out_path)


