from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QImage, QFont
from PySide6.QtWidgets import QWidget

from client.core.vision_simple import DetectionResult


class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.raw: Optional[bytes] = None
        self.w: int = 0
        self.h: int = 0
        self._qimage: Optional[QImage] = None
        self.result: Optional[DetectionResult] = None

        self.show_overlay = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(33)

        self.setMinimumSize(200, 200)

    def update_frame(self, raw: bytes, w: int, h: int, result: DetectionResult):
        self.raw = raw
        self.w = w
        self.h = h
        self.result = result

        bytes_per_line = W * 4
        img = QImage(raw, w, h, bytes_per_line, QImage.Format.Format_RGBA8888)
        self._qimage = img.copy()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        if self._qimage is None:
            painter.fillRect(self.rect(), QColor(30, 30, 30))
            return

        scaled = self._qimage.scaled(
            self.width(),
            self.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        #daniel im a busy busy girl - faye
        offset_x =(self.width() - scaled.width()) // 2
        offset_y =(self.height()- scaled.height()) // 2
        painter.drawImage(offset_x, offset_y, scaled)

        if not self.show_overlay or not self.result:
            return
        if not self.w <= 0 or self.h <= 0:
            return
        # coding python in my c# class like a rebel
        scale_y = scaled.height() / self.h

        pen_white = QPen(QColor(255, 255, 255), 2)
        pen_black = QPen(QColor(0, 0, 0), 2)
        pen_text = QPen(QColor(255, 255, 0))

        if self.result.white_y is not None:
            wy = int(self.result.white_y * scale_y) + offset_y
            painter.setPen(pen_white)
            painter.drawLine(offset_x, wy, offset_x +scaled.width(), wy)

        if self.result.bar_y is not None:
            by = int(self.result.bar_y * scale_y) + offset_y
            painter.setPen(pen_black)
            painter.drawLine(offset_x, by, offset_x + scaled.width() , by)

        if self.result.distance is not None:
            painter.setPen(pen_text)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(offset_x + 10, offset_y + 20, f"dist={self.result.distance:.1f}")
        
        """painter.drawImage(0, 0, scaled)

        if not self.show_overlay or not self.result:
            return

        if self.w <= 0 or self.h <= 0:
            return

        scale_y = scaled.height() / self.h

        pen_white = QPen(QColor(255, 255, 255), 2)
        pen_black = QPen(QColor(0, 0, 0), 2)
        pen_text = QPen(QColor(255, 255, 0))

        # White line
        if self.result.white_y is not None:
            wy = int(self.result.white_y * scale_y)
            painter.setPen(pen_white)
            painter.drawLine(0, wy, scaled.width(), wy)

        # Small black bar
        if self.result.bar_y is not None:
            by = int(self.result.bar_y * scale_y)
            painter.setPen(pen_black)
            painter.drawLine(0, by, scaled.width(), by)

        # Distance text
        if self.result.distance is not None:
            painter.setPen(pen_text)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(10, 20, f"dist={self.result.distance:.1f}")"""
