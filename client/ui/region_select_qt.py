# client/ui/region_select_qt.py
from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QKeyEvent
from PySide6.QtWidgets import QWidget


class RegionSelectOverlay(QWidget):
    """
    Fullscreen overlay on a chosen QScreen.
    Click-drag to select a rectangle.
    Dims the screen and highlights the selected area.
    """

    def __init__(
        self,
        screen,
        on_selected: Callable[[int, int, int, int], None],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._screen = screen
        self._on_selected = on_selected

        self._dragging = False
        self._start = QPoint()
        self._end = QPoint()
        self._rect = QRect()

        # Window flags / attributes for overlay behavior
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        # Put the overlay exactly on the selected monitor
        geo = self._screen.geometry()
        self.setGeometry(geo)

        self._help_text = "Drag to select area • ENTER to confirm • ESC to cancel"

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Dim entire screen
        painter.fillRect(self.rect(), QColor(0, 0, 0, 160))

        # If selecting, "cut out" the selected area (make it clear)
        if not self._rect.isNull() and self._rect.width() > 1 and self._rect.height() > 1:
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(self._rect, QColor(0, 0, 0, 0))
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

            # Draw white border
            pen = QPen(QColor(255, 255, 255, 230))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(self._rect)

        # Help text top-left
        painter.setPen(QPen(QColor(255, 255, 255, 220)))
        painter.drawText(16, 28, self._help_text)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._start = event.position().toPoint()
            self._end = self._start
            self._rect = QRect(self._start, self._end).normalized()
            self.update()

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            self._end = event.position().toPoint()
            self._rect = QRect(self._start, self._end).normalized()
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            self._end = event.position().toPoint()
            self._rect = QRect(self._start, self._end).normalized()
            self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # ESC cancels
        if event.key() == Qt.Key_Escape:
            self.close()
            return

        # ENTER confirms selection
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self._rect.isNull() or self._rect.width() < 5 or self._rect.height() < 5:
                return

            # Convert overlay-local coords → absolute screen coords
            screen_geo = self._screen.geometry()
            x = screen_geo.x() + self._rect.x()
            y = screen_geo.y() + self._rect.y()
            w = self._rect.width()
            h = self._rect.height()

            self._on_selected(int(x), int(y), int(w), int(h))
            self.close()
