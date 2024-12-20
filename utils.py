import sys
import os
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QMessageBox, QApplication


def load_custom_fonts(config):
    font_path = os.path.join(config.script_dir, config.font_file)
    if not os.path.exists(font_path):
        print(f"Font file not found at '{font_path}'. Please ensure the font file is correct.")
        sys.exit(1)
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print("Failed to load the custom font.")
        sys.exit(1)
    loaded_fonts = QFontDatabase.applicationFontFamilies(font_id)
    if not loaded_fonts:
        print("No font families loaded.")
        sys.exit(1)
    config.font_family = loaded_fonts[0]
    return loaded_fonts[0]


def show_error_message(title, message):
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()


def signal_handler(sig, frame):
    QApplication.quit()
