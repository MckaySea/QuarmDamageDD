# main.py

import sys
import os
import signal
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog
from watchdog.observers import Observer
from config import Config
from handlers import LogHandler
from utils import load_custom_fonts, show_error_message, signal_handler
from ui.configuration_window import ConfigurationWindow
from ui.overlay_window import OverlayWindow


class DamageOverlayApp(QApplication):
    def __init__(self, sys_argv, config: Config):
        super().__init__(sys_argv)
        self.config = config
        load_custom_fonts(self.config)
        self.overlay = OverlayWindow(self.config)
        self.overlay.show()

        self.log_handler = LogHandler(self.process_log_lines, self.config)
        self.observer = Observer()
        log_dir = os.path.dirname(os.path.abspath(self.config.log_file_path))
        self.observer.schedule(self.log_handler, log_dir, recursive=False)
        self.observer.start()

    def process_log_lines(self, damage_events):
        if not damage_events:
            return
        self.overlay.damage_received.emit(damage_events)

    def __del__(self):
        self.observer.stop()
        self.observer.join()


def main():
    initial_config = Config()
    initial_config.load_from_file()

    app = QApplication(sys.argv)

    config_window = ConfigurationWindow(initial_config)
    config_window.setModal(True)
    config_window.config_saved.connect(lambda cfg: cfg.save_to_file())

    if config_window.exec_() == QDialog.Accepted:
        updated_config = config_window.config
        updated_config.save_to_file()

        missing_icons = [spell['spell_name'] for spell in updated_config.spells if not os.path.exists(spell['icon_path'])]
        if missing_icons:
            msg = "The following icon files are missing:\n" + "\n".join(
                f" - {spell['spell_name']}: {spell['icon_path']}" for spell in updated_config.spells if not os.path.exists(spell['icon_path'])
            )
            show_error_message("Missing Icons", msg)
            sys.exit(1)

        font_dir = os.path.dirname(updated_config.font_file)
        if not os.path.isdir(font_dir):
            msg = "The directory for fonts does not exist. Please ensure the font file path is correct."
            show_error_message("Missing Fonts Directory", msg)
            sys.exit(1)
        font_file_path = updated_config.font_file
        if not os.path.exists(font_file_path):
            msg = f"The font file '{font_file_path}' is missing."
            show_error_message("Missing Font File", msg)
            sys.exit(1)

        main_app = DamageOverlayApp(sys.argv, updated_config)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            sys.exit(main_app.exec_())
        except SystemExit:
            print("Exiting...")
    else:
        print("Configuration canceled. Exiting.")
        sys.exit(0)


if __name__ == '__main__':
    main()
