from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QPoint, QSize
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QSpinBox,
    QDoubleSpinBox,
    QMessageBox,
    QGroupBox,
    QFormLayout
)
from .position_selector import PositionSelectorWindow
from config import Config


class ConfigurationWindow(QDialog):
    config_saved = pyqtSignal(Config)

    def __init__(self, config: Config):
        super().__init__()
        self.setWindowTitle("Configuration Settings")
        self.config = config
        self.categories = ['damage', 'crowd_control', 'healing']
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Log File Path
        log_layout = QHBoxLayout()
        log_label = QLabel("Log File Path:")
        self.log_input = QLineEdit(self.config.log_file_path)
        log_browse = QPushButton("Browse")
        log_browse.clicked.connect(self.browse_log_file)
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_input)
        log_layout.addWidget(log_browse)
        layout.addLayout(log_layout)

        # Animation Duration
        anim_layout = QHBoxLayout()
        anim_label = QLabel("Animation Duration (ms):")
        self.anim_input = QSpinBox()
        self.anim_input.setRange(1000, 10000)
        self.anim_input.setSingleStep(500)
        self.anim_input.setValue(self.config.animation_duration)
        anim_layout.addWidget(anim_label)
        anim_layout.addWidget(self.anim_input)
        layout.addLayout(anim_layout)

        # Float Distance
        float_layout = QHBoxLayout()
        float_label = QLabel("Float Distance (pixels):")
        self.float_input = QSpinBox()
        self.float_input.setRange(50, 500)
        self.float_input.setValue(self.config.float_distance)
        float_layout.addWidget(float_label)
        float_layout.addWidget(self.float_input)
        layout.addLayout(float_layout)

        # Set Positions for Each Category
        self.position_displays = {}
        for category in self.categories:
            pos_layout = QHBoxLayout()
            pos_label = QLabel(f"{category.replace('_', ' ').capitalize()} Position:")
            pos_display = QLabel(f"({self.config.start_positions[category][0]}, {self.config.start_positions[category][1]})")
            set_pos_button = QPushButton("Set Position (Press Enter To Confirm)")
            set_pos_button.clicked.connect(lambda checked, cat=category: self.set_position(cat))
            pos_layout.addWidget(pos_label)
            pos_layout.addWidget(pos_display)
            pos_layout.addWidget(set_pos_button)
            layout.addLayout(pos_layout)
            self.position_displays[category] = pos_display

        # Padding
        padding_layout = QHBoxLayout()
        padding_label = QLabel("Padding (pixels):")
        self.padding_input = QSpinBox()
        self.padding_input.setRange(0, 100)
        self.padding_input.setValue(self.config.padding)
        padding_layout.addWidget(padding_label)
        padding_layout.addWidget(self.padding_input)
        layout.addLayout(padding_layout)

        # Total Font Ratio
        total_font_layout = QHBoxLayout()
        total_font_label = QLabel("Total Damage Font Ratio:")
        self.total_font_input = QDoubleSpinBox()
        self.total_font_input.setRange(0.1, 2.0)
        self.total_font_input.setSingleStep(0.1)
        self.total_font_input.setValue(self.config.total_font_ratio)
        total_font_layout.addWidget(total_font_label)
        total_font_layout.addWidget(self.total_font_input)
        layout.addLayout(total_font_layout)

        # Total Color
        total_color_layout = QHBoxLayout()
        total_color_label = QLabel("Total Damage Color:")
        self.total_color_input = QLineEdit(self.config.total_color)
        total_color_layout.addWidget(total_color_label)
        total_color_layout.addWidget(self.total_color_input)
        layout.addLayout(total_color_layout)

        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("Opacity (0.1 to 1.0):")
        self.opacity_input = QDoubleSpinBox()
        self.opacity_input.setRange(0.1, 1.0)
        self.opacity_input.setSingleStep(0.1)
        self.opacity_input.setValue(self.config.opacity)
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_input)
        layout.addLayout(opacity_layout)

        # Per-category settings
        self.category_inputs = {}
        for category in self.categories:
            group_box = QGroupBox(f"{category.capitalize()} Settings")
            form_layout = QFormLayout()

            icon_width_input = QSpinBox()
            icon_width_input.setRange(16, 512)
            icon_width_input.setValue(self.config.spell_categories[category]['icon_width'])

            icon_height_input = QSpinBox()
            icon_height_input.setRange(16, 512)
            icon_height_input.setValue(self.config.spell_categories[category]['icon_height'])

            font_size_input = QSpinBox()
            font_size_input.setRange(8, 100)
            font_size_input.setValue(self.config.spell_categories[category]['font_size'])

            text_color_input = QLineEdit(self.config.spell_categories[category]['text_color'])

            monster_font_size_input = QSpinBox()
            monster_font_size_input.setRange(8, 100)
            monster_font_size_input.setValue(self.config.spell_categories[category].get('monster_name_font_size', 24))

            monster_text_color_input = QLineEdit(self.config.spell_categories[category].get('monster_name_text_color', 'white'))

            form_layout.addRow("Icon Width:", icon_width_input)
            form_layout.addRow("Icon Height:", icon_height_input)
            form_layout.addRow("Font Size:", font_size_input)
            form_layout.addRow("Text Color:", text_color_input)
            form_layout.addRow("Monster Name Font Size:", monster_font_size_input)
            form_layout.addRow("Monster Name Text Color:", monster_text_color_input)

            group_box.setLayout(form_layout)
            layout.addWidget(group_box)

            self.category_inputs[category] = {
                'icon_width': icon_width_input,
                'icon_height': icon_height_input,
                'font_size': font_size_input,
                'text_color': text_color_input,
                'monster_name_font_size': monster_font_size_input,
                'monster_name_text_color': monster_text_color_input
            }

        # Buttons
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def browse_log_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Log File",
            self.log_input.text(),
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.log_input.setText(file_path)

    def set_position(self, category):
        self.selector = PositionSelectorWindow(category, self.config.start_positions)
        self.selector.position_selected.connect(self.update_position)
        self.selector.exec_()

    @pyqtSlot(QPoint, str)
    def update_position(self, pos: QPoint, category: str):
        self.config.start_positions[category] = (pos.x(), pos.y())
        self.position_displays[category].setText(f"({pos.x()}, {pos.y()})")

    def save_config(self):
        self.config.log_file_path = self.log_input.text()
        self.config.animation_duration = self.anim_input.value()
        self.config.float_distance = self.float_input.value()
        self.config.padding = self.padding_input.value()
        self.config.total_font_ratio = self.total_font_input.value()
        self.config.total_color = self.total_color_input.text()
        self.config.opacity = self.opacity_input.value()

        for category in self.categories:
            self.config.spell_categories[category]['icon_width'] = self.category_inputs[category]['icon_width'].value()
            self.config.spell_categories[category]['icon_height'] = self.category_inputs[category]['icon_height'].value()
            self.config.spell_categories[category]['font_size'] = self.category_inputs[category]['font_size'].value()
            self.config.spell_categories[category]['text_color'] = self.category_inputs[category]['text_color'].text()
            self.config.spell_categories[category]['monster_name_font_size'] = self.category_inputs[category]['monster_name_font_size'].value()
            self.config.spell_categories[category]['monster_name_text_color'] = self.category_inputs[category]['monster_name_text_color'].text()

        self.config_saved.emit(self.config)
        self.accept()
