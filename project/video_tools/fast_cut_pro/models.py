from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class MarkPoint:
    time_seconds: float
    frame_index: int


@dataclass
class VideoItem:
    path: str
    pre_seconds: float = 1.5
    post_seconds: float = 1.5
    marks: List[MarkPoint] = field(default_factory=list)


