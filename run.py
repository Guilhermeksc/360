import sys
from PyQt6.QtWidgets import QApplication
from src.config.paths import STYLE_PATH
from src.main import MainWindow

def load_stylesheet(app):
    with open(STYLE_PATH, "r") as f:
        app.setStyleSheet(f.read())

def run():
    app = QApplication(sys.argv)
    load_stylesheet(app)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
