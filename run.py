import sys
from PyQt6.QtWidgets import QApplication
from src.main import MainWindow
from paulovitor.load_sheet import load_stylesheet

def run():
    app = QApplication(sys.argv)
    load_stylesheet(app)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
