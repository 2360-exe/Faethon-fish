# client/ui/theme_qt.py

THEME_QSS = """
QWidget {
  background: #0b0b0b;
  color: #f2f2f2;
  font-size: 11pt;
}

QLabel#TitleLabel {
  font-size: 14pt;
  font-weight: 600;
}

QFrame#Panel {
  background: #101010;
  border: 1px solid #f2f2f2;
}

QPushButton {
  background: #0b0b0b;
  border: 1px solid #f2f2f2;
  padding: 8px 10px;
}

QPushButton:hover {
  background: #f2f2f2;
  color: #0b0b0b;
}

QPushButton:pressed {
  background: #d9d9d9;
  color: #0b0b0b;
}

QPushButton:disabled {
  color: #777777;
  border: 1px solid #444444;
}

QSlider::groove:horizontal {
  border: 1px solid #f2f2f2;
  height: 6px;
  background: #0b0b0b;
}

QSlider::handle:horizontal {
  background: #f2f2f2;
  width: 12px;
}
"""
