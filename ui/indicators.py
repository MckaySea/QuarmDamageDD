from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout
from config import Config


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
