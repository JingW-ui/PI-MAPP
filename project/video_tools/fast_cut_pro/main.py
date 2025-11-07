import sys
import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def _resource_path(*relative: str) -> str:
    base_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_dir, *relative)


def main() -> None:
    app = QApplication(sys.argv)
    icon_path = _resource_path("ico", "app_128px.ico")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    window = MainWindow()
    # 兼容某些平台需显式给窗口设置图标
    window.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


