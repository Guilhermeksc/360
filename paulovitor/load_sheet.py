from src.config.paths import STYLE_PATH

def load_stylesheet(app):
    with open(STYLE_PATH, "r") as f:
        app.setStyleSheet(f.read())