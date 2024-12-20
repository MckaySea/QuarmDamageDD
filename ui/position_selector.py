from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QSize
from PyQt5.QtWidgets import QDialog, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen


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
