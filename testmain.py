import sys
import re
import os
import signal
import json  # For configuration persistence
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QPoint, QSize
from PyQt5.QtGui import QFontDatabase, QFont, QPainter, QColor, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QSpinBox,
    QDoubleSpinBox,
    QMessageBox,
    QDialog,
    QGroupBox,
    QFormLayout
)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Any

# ------------------------ Configuration Dataclass ------------------------

@dataclass
class Config:
    # Path to your log file (absolute path)
    log_file_path: str = 'log.txt'  # Default value

    # List of spells with their configurations
    spells: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            'spell_name': 'Dooming Darkness',
            'icon_path': 'icons/doom_darkness.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Dooming Darkness\.',
            'message_template': None,
            'category': 'damage'
        },
        {
            'spell_name': 'Cascading Darkness',
            'icon_path': 'icons/cascading_darkness.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Cascading Darkness\.',
            'message_template': None,
            'category': 'damage'
        },
        {
            'spell_name': 'Spirit of Wolf',
            'icon_path': 'icons/spirit_wolf.png',
            'regex_pattern': r'You feel the spirit of wolf enter you.',
            'message_template': 'Spirit of the wolf',
            'category': 'healing'
        },
        {
            'spell_name': 'Vampiric Curse',
            'icon_path': 'icons/vamp_curse.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Vampiric Curse\.',
            'message_template': None,
            'category': 'damage'
        },
        {
            'spell_name': 'Invoke Fear',
            'icon_path': 'icons/invoke_fear.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Invoke Fear\.',
            'message_template': None,
            'category': 'crowd_control'
        },
        {
            'spell_name': 'Envenomed Bolt',
            'icon_path': 'icons/Envenomed_Bolt.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Envenomed Bolt\.',
            'message_template': None,
            'category': 'damage'
        },
        {
            'spell_name': 'Bond of Death',
            'icon_path': 'icons/bond_of_death.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Bond of Death\.',
            'message_template': None,
            'category': 'damage'
        },
        {
            'spell_name': 'Screaming Terror',
            'icon_path': 'icons/screaming_terror.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) begins to scream\.\s*',
            'message_template': '{monster_name} was mezzed!',
            'category': 'crowd_control'
        }
    ])

    # Start positions for each category
    start_positions: Dict[str, Tuple[int, int]] = field(default_factory=lambda: {
        'damage': (960, 100),
        'crowd_control': (960, 300),
        'healing': (960, 500),
    })

    # Per-category appearance settings
    spell_categories: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'damage': {
            'icon_width': 64,
            'icon_height': 64,
            'font_size': 20,
            'text_color': 'blue',
            'monster_name_font_size': 24,
            'monster_name_text_color': 'white'
        },
        'crowd_control': {
            'icon_width': 64,
            'icon_height': 64,
            'font_size': 20,
            'text_color': 'green',
            'monster_name_font_size': 24,
            'monster_name_text_color': 'white'
        },
        'healing': {
            'icon_width': 64,
            'icon_height': 64,
            'font_size': 20,
            'text_color': 'yellow',
            'monster_name_font_size': 24,
            'monster_name_text_color': 'white'
        }
    })

    animation_duration: int = 4000    # Duration in milliseconds (4 seconds)
    float_distance: int = 150         # Distance in pixels the indicator moves downwards

    padding: int = 10                 # Padding between stacked indicators/groups

    # Total Damage Label Appearance Settings
    total_font_ratio: float = 0.50    # Total damage font size as a ratio of FONT_SIZE
    total_color: str = 'red'          # Color for total damage text

    # Opacity Settings
    opacity: float = 1.0              # Overall opacity (0.1 to 1.0)

    # Font settings
    font_file: str = 'fonts/PressStart2P-Regular.ttf'
    font_family: str = ''  # To be set after loading

    # Configuration file path
    config_file: str = field(init=False)

    # Log file path absolute
    script_dir: str = field(init=False)

    def __post_init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_file_path = os.path.join(self.script_dir, self.log_file_path)
        for spell in self.spells:
            spell['icon_path'] = os.path.join(self.script_dir, spell['icon_path'])
        self.config_file = os.path.join(self.script_dir, 'config.json')

    def to_dict(self):
        return {
            'log_file_path': self.log_file_path,
            'spells': self.spells,
            'start_positions': self.start_positions,
            'spell_categories': self.spell_categories,
            'animation_duration': self.animation_duration,
            'float_distance': self.float_distance,
            'padding': self.padding,
            'total_font_ratio': self.total_font_ratio,
            'total_color': self.total_color,
            'opacity': self.opacity,
            'font_file': self.font_file
        }

    def save_to_file(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Failed to save configuration: {e}")

    def load_from_file(self):
        if not os.path.exists(self.config_file):
            print("Configuration file not found. Using default settings.")
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for field_name in self.__dataclass_fields__:
                if field_name in data and field_name not in ('script_dir', 'config_file'):
                    setattr(self, field_name, data[field_name])

            # Ensure that spell_icons paths are absolute
            for spell in self.spells:
                spell['icon_path'] = os.path.join(self.script_dir, os.path.relpath(spell['icon_path'], self.script_dir))

            print(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            print("Using default settings.")


# ------------------------ Position Selector Window ------------------------

class PositionSelectorWindow(QDialog):
    position_selected = pyqtSignal(QPoint, str)  # Emit position and category

    def __init__(self, category_name, start_positions):
        super().__init__()
        self.category_name = category_name
        self.start_positions = start_positions  # Dictionary of category -> (x, y)

        self.setWindowTitle(f"Select {self.category_name.capitalize()} Position")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        self.box_size = QSize(100, 100)
        self.box_pos = QPoint(
            (self.width() - self.box_size.width()) // 2,
            (self.height() - self.box_size.height()) // 2
        )
        self.dragging = False

        # Instructions label
        self.instructions = QLabel(
            f"Drag the {self.category_name} box to set its position.\n"
            f"Press ENTER to confirm position.\nPress ESC to cancel.",
            self
        )
        self.instructions.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 128); padding: 10px;")
        self.instructions.adjustSize()
        # Place instructions near the top center
        self.instructions.move(
            (self.width() - self.instructions.width()) // 2, 
            20
        )
        self.instructions.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        # Draw previously set boxes for other categories
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 0, 0, 70))
        for cat, pos in self.start_positions.items():
            if cat == self.category_name:
                continue
            rect = QtCore.QRect(QPoint(pos[0] - self.box_size.width()//2, pos[1] - self.box_size.height()//2), self.box_size)
            painter.drawRect(rect)

        # Draw the draggable box for the current category
        painter.setPen(QPen(QColor(255, 0, 0), 3))
        painter.setBrush(QColor(255, 0, 0, 100))
        painter.drawRect(QtCore.QRect(self.box_pos, self.box_size))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            box_rect = QtCore.QRect(self.box_pos, self.box_size)
            if box_rect.contains(event.pos()):
                self.dragging = True
                self.drag_offset = event.pos() - self.box_pos
                event.accept()
            else:
                event.ignore()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.pos() - self.drag_offset
            new_x = max(0, min(new_pos.x(), self.width() - self.box_size.width()))
            new_y = max(0, min(new_pos.y(), self.height() - self.box_size.height()))
            self.box_pos = QPoint(new_x, new_y)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            center_pos = self.box_pos + QPoint(
                self.box_size.width() // 2,
                self.box_size.height() // 2
            )
            self.position_selected.emit(center_pos, self.category_name)
            self.accept()
        elif event.key() == Qt.Key_Escape:
            self.reject()



# ------------------------ Configuration Window ------------------------

class ConfigurationWindow(QtWidgets.QDialog):
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


# ------------------------ Damage Indicator Widget ------------------------

class DamageIndicator(QtWidgets.QWidget):
    def __init__(self, damage, spell_icon, x, y, font_family, config: Config, category: str, parent=None):
        super().__init__(parent)
        self.damage = int(damage)
        self.spell_icon = spell_icon
        self.font_family = font_family
        self.config = config
        self.category = category

        cat_conf = self.config.spell_categories[self.category]

        self.icon_width = cat_conf['icon_width']
        self.icon_height = cat_conf['icon_height']
        self.font_size = cat_conf['font_size']
        self.text_color = cat_conf['text_color']

        self.initUI()

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.adjustSize()
        self.move(x - self.width() // 2, y)

        self.animation = QtCore.QPropertyAnimation(self, b'pos')
        self.animation.setDuration(self.config.animation_duration)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QtCore.QPoint(self.x(), self.y() + self.config.float_distance))
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.animation.start()

        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QtCore.QPropertyAnimation(self.opacity_effect, b'opacity')
        self.fade_animation.setDuration(self.config.animation_duration)
        self.fade_animation.setStartValue(self.config.opacity)
        self.fade_animation.setEndValue(0)
        self.fade_animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.fade_animation.start()
        self.fade_animation.finished.connect(self.close)

    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        icon_label = QLabel()
        pixmap = QtGui.QPixmap(self.spell_icon)
        if pixmap.isNull():
            print(f"Failed to load icon: {self.spell_icon}")
        pixmap = pixmap.scaled(
            self.icon_width, self.icon_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)

        damage_label = QLabel(str(self.damage))
        damage_label.setStyleSheet(f"color: {self.text_color};")
        damage_label.setFont(QFont(self.font_family, self.font_size))
        layout.addWidget(damage_label)

        self.setLayout(layout)
        self.adjustSize()


# ------------------------ Special Indicator Widget ------------------------

class SpecialIndicator(QtWidgets.QWidget):
    def __init__(self, message, spell_icon, x, y, font_family, config: Config, category: str, parent=None):
        super().__init__(parent)
        self.message = message
        self.spell_icon = spell_icon
        self.font_family = font_family
        self.config = config
        self.category = category

        cat_conf = self.config.spell_categories[self.category]

        self.icon_width = cat_conf['icon_width']
        self.icon_height = cat_conf['icon_height']
        self.font_size = cat_conf['font_size']
        self.text_color = cat_conf['text_color']

        self.initUI()

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.adjustSize()
        self.move(x - self.width() // 2, y)

        self.animation = QtCore.QPropertyAnimation(self, b'pos')
        self.animation.setDuration(self.config.animation_duration)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QtCore.QPoint(self.x(), self.y() + self.config.float_distance))
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.animation.start()

        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QtCore.QPropertyAnimation(self.opacity_effect, b'opacity')
        self.fade_animation.setDuration(self.config.animation_duration)
        self.fade_animation.setStartValue(self.config.opacity)
        self.fade_animation.setEndValue(0)
        self.fade_animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.fade_animation.start()
        self.fade_animation.finished.connect(self.close)

    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        icon_label = QLabel()
        pixmap = QtGui.QPixmap(self.spell_icon)
        if pixmap.isNull():
            print(f"Failed to load icon: {self.spell_icon}")
        pixmap = pixmap.scaled(
            self.icon_width, self.icon_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)

        message_label = QLabel(self.message)
        message_label.setStyleSheet(f"color: {self.text_color};")
        message_label.setFont(QFont(self.font_family, self.font_size))
        layout.addWidget(message_label)

        self.setLayout(layout)
        self.adjustSize()


# ------------------------ Total Damage Label Widget ------------------------

class TotalDamageLabel(QtWidgets.QWidget):
    def __init__(self, total_damage, x, y, font_family, config: Config, category: str, parent=None, monster_name=None):
        super().__init__(parent)
        self.total_damage = total_damage
        self.font_family = font_family
        self.config = config
        self.category = category
        self.monster_name = monster_name

        # Use the category's font size as base, then apply ratio
        base_font_size = self.config.spell_categories[self.category]['font_size']
        self.calculated_total_font_size = int(base_font_size * self.config.total_font_ratio)
        self.text_color = self.config.total_color

        self.initUI()

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.adjustSize()
        self.move(x - self.width() // 2, y)

        self.animation = QtCore.QPropertyAnimation(self, b'pos')
        self.animation.setDuration(self.config.animation_duration)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QtCore.QPoint(self.x(), self.y() + self.config.float_distance))
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.animation.start()

        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QtCore.QPropertyAnimation(self.opacity_effect, b'opacity')
        self.fade_animation.setDuration(self.config.animation_duration)
        self.fade_animation.setStartValue(self.config.opacity)
        self.fade_animation.setEndValue(0)
        self.fade_animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.fade_animation.start()
        self.fade_animation.finished.connect(self.close)

    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        if self.monster_name:
            total_label = QLabel(f"{self.monster_name} - Total Damage: {self.total_damage}")
        else:
            total_label = QLabel(f"Total Damage: {self.total_damage}")
        total_label.setStyleSheet(f"color: {self.text_color};")
        total_label.setFont(QFont(self.font_family, self.calculated_total_font_size))
        layout.addWidget(total_label)

        self.setLayout(layout)
        self.adjustSize()


# ------------------------ Monster Name Label Widget ------------------------

class MonsterNameLabel(QtWidgets.QWidget):
    def __init__(self, monster_name, x, y, font_family, config: Config, category: str, parent=None):
        super().__init__(parent)
        self.monster_name = monster_name
        self.font_family = font_family
        self.config = config
        self.category = category

        cat_conf = self.config.spell_categories[self.category]
        self.font_size = cat_conf['monster_name_font_size']
        self.text_color = cat_conf['monster_name_text_color']

        self.initUI()

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.adjustSize()
        self.move(x - self.width() // 2, y)

        self.animation = QtCore.QPropertyAnimation(self, b'pos')
        self.animation.setDuration(self.config.animation_duration)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QtCore.QPoint(self.x(), self.y() + self.config.float_distance))
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.animation.start()

        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QtCore.QPropertyAnimation(self.opacity_effect, b'opacity')
        self.fade_animation.setDuration(self.config.animation_duration)
        self.fade_animation.setStartValue(self.config.opacity)
        self.fade_animation.setEndValue(0)
        self.fade_animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.fade_animation.start()
        self.fade_animation.finished.connect(self.close)

    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        name_label = QLabel(self.monster_name)
        name_label.setStyleSheet(f"color: {self.text_color};")
        name_label.setFont(QFont(self.font_family, self.font_size))
        layout.addWidget(name_label)

        self.setLayout(layout)
        self.adjustSize()


# ------------------------ Group Indicator Class ------------------------

class GroupIndicator:
    def __init__(self, damage_events, overlay, group_index, config: Config, category: str, monster_name: str):
        self.damage_events = damage_events
        self.overlay = overlay
        self.group_index = group_index
        self.config = config
        self.font_family = config.font_family
        self.category = category
        self.monster_name = monster_name
        self.indicators = []
        self.total_label = None
        self.monster_label = None
        self.init_group()

    def init_group(self):
        start_x, start_y = self.config.start_positions.get(self.category, (960, 100))

        cat_conf = self.config.spell_categories[self.category]
        icon_height = cat_conf['icon_height']
        monster_name_font_size = cat_conf['monster_name_font_size']

        # Calculate vertical offset for groups
        group_y_offset = self.group_index * (
            icon_height + self.config.padding +
            int(self.config.spell_categories[self.category]['font_size'] * self.config.total_font_ratio) +
            monster_name_font_size + (self.config.padding * 2)
        )

        # Place monster name label at the top
        monster_label_y = start_y + group_y_offset
        self.monster_label = MonsterNameLabel(self.monster_name, start_x, monster_label_y, self.font_family, self.config, self.category)
        self.monster_label.show()

        current_y = monster_label_y + self.monster_label.height() + self.config.padding

        for event in self.damage_events:
            if event['type'] == 'damage':
                damage = event['damage']
                spell_name = event['spell_name']
                icon_path = self.config.spells_dict.get(spell_name, {}).get('icon_path', None)
                if not icon_path or not os.path.exists(icon_path):
                    continue

                indicator = DamageIndicator(damage, icon_path, start_x, current_y, self.font_family, self.config, self.category)
                indicator.show()
                self.indicators.append({'widget': indicator, 'category': self.category})
                current_y += indicator.height() + self.config.padding

            elif event['type'] == 'special':
                message = event['message']
                spell_name = event['spell_name']
                icon_path = self.config.spells_dict.get(spell_name, {}).get('icon_path', None)
                if not icon_path or not os.path.exists(icon_path):
                    continue

                indicator = SpecialIndicator(message, icon_path, start_x, current_y, self.font_family, self.config, self.category)
                indicator.show()
                self.indicators.append({'widget': indicator, 'category': self.category})
                current_y += indicator.height() + self.config.padding

        category_damage = 0
        for event in self.damage_events:
            if event['type'] == 'damage':
                category_damage += event['damage']

        damage_event_count = len([event for event in self.damage_events if event['type'] == 'damage'])
        if damage_event_count >= 2:
            # Place total damage label below all indicators
            self.total_label = TotalDamageLabel(category_damage, start_x, current_y, self.font_family, self.config, self.category, monster_name=self.monster_name)
            self.total_label.show()

    def is_active(self):
        active = True
        if self.monster_label and not self.monster_label.isVisible():
            active = False
        for ind in self.indicators:
            if not ind['widget'].isVisible():
                active = False
        if self.total_label and not self.total_label.isVisible():
            active = False
        return active


# ------------------------ Overlay Window ------------------------

class OverlayWindow(QtWidgets.QWidget):
    damage_received = pyqtSignal(list)

    def __init__(self, config: Config):
        super().__init__()
        self.groups = []
        self.config = config
        self.initUI()

        self.config.spells_dict = {spell['spell_name']: spell for spell in self.config.spells}
        self.damage_received.connect(self.show_damage)

    def initUI(self):
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.setGeometry(self.screen)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.category_boxes = {}
        for category in self.config.start_positions.keys():
            box = QLabel(self)
            box.setText(category.replace('_', ' ').capitalize())
            box.setStyleSheet("color: white; background-color: rgba(255, 0, 0, 150); padding: 5px;")
            box.adjustSize()
            x, y = self.config.start_positions[category]
            box.move(x - box.width() // 2, y - box.height() // 2)
            box.show()
            self.category_boxes[category] = box

    @pyqtSlot(list)
    def show_damage(self, damage_events):
        if not damage_events:
            return

        # Group by (category, monster_name)
        # monster_name might not exist for special events that don't have damage - handle gracefully
        categorized_events = {}
        for event in damage_events:
            category = event['category']
            monster_name = event.get('monster_name', event.get('message', 'Unknown'))
            if event['type'] == 'damage':
                # For damage, we have monster_name from regex group 1
                monster_name = event.get('monster_name', 'Unknown')
            else:
                # For special events that have monster_name in message template or not
                # If message_template sets {monster_name}, we extracted it. Otherwise fallback
                monster_name = event.get('monster_name', 'Unknown')

            key = (category, monster_name)
            if key not in categorized_events:
                categorized_events[key] = []
            categorized_events[key].append(event)

        for (category, monster_name), events in categorized_events.items():
            # Determine group_index for this (category, monster_name) combo
            existing_groups = [g for g in self.groups if g.category == category and g.monster_name == monster_name]
            group_index = len(existing_groups)
            group = GroupIndicator(events, self, group_index, self.config, category, monster_name)
            self.groups.append(group)

        self.cleanup_groups()

    def cleanup_groups(self):
        active_groups = []
        for group in self.groups:
            if group.is_active():
                active_groups.append(group)
        self.groups = active_groups


# ------------------------ Log File Handler ------------------------

class LogHandler(FileSystemEventHandler):
    def __init__(self, callback, config: Config):
        super().__init__()
        self.callback = callback
        self.config = config
        try:
            self._file = open(self.config.log_file_path, 'r', encoding='utf-8')
        except FileNotFoundError:
            print(f"Log file '{self.config.log_file_path}' not found.")
            sys.exit(1)
        self._file.seek(0, os.SEEK_END)
        self.spell_patterns = []
        for spell in self.config.spells:
            try:
                compiled_regex = re.compile(spell['regex_pattern'], re.IGNORECASE)
                self.spell_patterns.append({
                    'spell_name': spell['spell_name'],
                    'regex': compiled_regex,
                    'message_template': spell.get('message_template', None),
                    'category': spell.get('category', 'damage')
                })
            except re.error as e:
                print(f"Invalid regex pattern for spell '{spell['spell_name']}': {e}")

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == os.path.abspath(self.config.log_file_path):
            lines = self._file.readlines()
            events = []
            for line in lines:
                line = line.strip()
                for pattern in self.spell_patterns:
                    match = pattern['regex'].search(line)
                    if match:
                        if pattern['message_template']:
                            # Special event
                            monster_name = match.group(1)
                            message = pattern['message_template'].format(monster_name=monster_name)
                            events.append({
                                'type': 'special',
                                'spell_name': pattern['spell_name'],
                                'message': message,
                                'category': pattern['category'],
                                'monster_name': monster_name
                            })
                        else:
                            # Damage event
                            monster_name = match.group(1)
                            damage = int(match.group(2))
                            spell_name = pattern['spell_name']
                            category = pattern['category']
                            events.append({
                                'type': 'damage',
                                'spell_name': spell_name,
                                'damage': damage,
                                'category': category,
                                'monster_name': monster_name
                            })
            if events:
                self.callback(events)


# ------------------------ Font Loader ------------------------

def load_custom_fonts(config: Config):
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


# ------------------------ Damage Overlay Application ------------------------

class DamageOverlayApp(QtWidgets.QApplication):
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


# ------------------------ Signal Handler ------------------------

def signal_handler(sig, frame):
    QtWidgets.QApplication.quit()


# ------------------------ Entry Point ------------------------

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
            QMessageBox.critical(None, "Missing Icons", msg)
            sys.exit(1)

        font_dir = os.path.dirname(updated_config.font_file)
        if not os.path.isdir(font_dir):
            msg = "The directory for fonts does not exist. Please ensure the font file path is correct."
            QMessageBox.critical(None, "Missing Fonts Directory", msg)
            sys.exit(1)
        font_file_path = updated_config.font_file
        if not os.path.exists(font_file_path):
            msg = f"The font file '{font_file_path}' is missing."
            QMessageBox.critical(None, "Missing Font File", msg)
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
