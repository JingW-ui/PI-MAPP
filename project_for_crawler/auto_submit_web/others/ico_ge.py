from PyQt5.QtGui import (QPixmap, QPainter, QPainterPath, QLinearGradient,
                         QRadialGradient, QColor, QFont, QPen, QBrush, QIcon)
from PyQt5.QtCore import Qt, QPointF, QRectF
import sys
from PyQt5.QtWidgets import QApplication


class ABIcon:
    SIZE = 64
    _cache = {}

    @classmethod
    def pixmap(cls, size=SIZE) -> QPixmap:
        if size in cls._cache:
            return cls._cache[size]

        px = QPixmap(size, size)
        px.fill(Qt.transparent)

        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(0, 0, size, size)
        radius = size * 0.18
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        # 1. 三色线性渐变：深青 → 中绿 → 淡青（中间最浅）
        g = QLinearGradient(QPointF(0, 0), QPointF(size, size))
        g.setColorAt(0.0, QColor("#00897b"))   # 深青
        g.setColorAt(0.5, QColor("#4db6ac"))  # 中绿（中心最浅）
        g.setColorAt(1.0, QColor("#80cbc4"))  # 淡青
        p.fillPath(path, QBrush(g))

        # 2. 径向毛玻璃：中心白雾 60 % 区域，不透明度 50 → 0
        radial = QRadialGradient(rect.center(), size * 0.6)
        radial.setColorAt(0.0, QColor(255, 255, 255, 80))
        radial.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.fillPath(path, radial)

        # 3. 文字
        font = QFont("Segoe UI", size * 0.25, QFont.Bold)
        p.setFont(font)
        p.setPen(QPen(Qt.white))
        p.drawText(rect, Qt.AlignCenter, "AB")

        p.end()
        cls._cache[size] = px
        return px

    @classmethod
    def icon(cls, size=SIZE) -> QIcon:
        return QIcon(cls.pixmap(size))

    @classmethod
    def save_as_png(cls, filename="AutoTool_AB_Icon.png", size=SIZE):
        pixmap = cls.pixmap(size)
        pixmap.save(filename, "PNG")
        print(f"图标已保存为：{filename}（尺寸：{size}×{size}像素）")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ABIcon.save_as_png()          # 64 默认
    ABIcon.save_as_png("AutoTool_AB_Icon_128.png", 128)
    sys.exit(0)