from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QLabel
from config import Config
from .group_indicator import GroupIndicator

class OverlayWindow(QWidget):
    damage_received = pyqtSignal(list)

    def __init__(self, config: Config):
        super().__init__()
        self.groups = []
        self.config = config
        self.initUI()

        # Create a dictionary to track vertical offsets for each category
        # This ensures each new group is placed below the previous ones.
        self.category_offsets = {cat: 0 for cat in self.config.start_positions.keys()}

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

    @QtCore.pyqtSlot(list)
    def show_damage(self, damage_events):
        if not damage_events:
            return

        # Group by (category, monster_name)
        categorized_events = {}
        for event in damage_events:
            category = event['category']
            monster_name = event.get('monster_name', event.get('message', 'Unknown'))

            key = (category, monster_name)
            if key not in categorized_events:
                categorized_events[key] = []
            categorized_events[key].append(event)

        for (category, monster_name), events in categorized_events.items():
            # Instead of using group_index for vertical placement,
            # we rely on the stored offset in self.category_offsets.
            group = GroupIndicator(
                events,
                self,
                self.category_offsets[category],
                self.config,
                category,
                monster_name
            )
            self.groups.append(group)

            # After placing the group, increment the offset for this category
            # by the amount of space used by this group.
            self.category_offsets[category] += group.final_group_height() + self.config.padding

        self.cleanup_groups()

    def cleanup_groups(self):
        active_groups = [g for g in self.groups if g.is_active()]
        self.groups = active_groups
