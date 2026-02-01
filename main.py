"""Entry point for Image Merger GUI application."""
import os
import sys

# macOS: Qt가 cocoa 플랫폼 플러그인을 찾을 수 있도록 경로 설정 (venv 등에서 실행 시)
if sys.platform == "darwin":
    import importlib.util
    spec = importlib.util.find_spec("PyQt5")
    if spec is not None and spec.origin is not None:
        platforms_path = os.path.join(
            os.path.dirname(spec.origin), "Qt5", "plugins", "platforms"
        )
        if os.path.isdir(platforms_path):
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = platforms_path

from PyQt5.QtWidgets import QApplication
from src.main_window import MainWindow
from src.styles import APP_STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Image Merger")
    app.setStyleSheet(APP_STYLESHEET)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
