from datetime import datetime
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
import time


class TimeMarker:
    lastmarker = 0
    
    def __init__(self):
        self.timeFont = QFont("Arial", 10)

    def paint(self, width, height, painter):
        now = time.time()
        if now > self.lastmarker + 1:
            self.lastmarker = now
            painter.setPen(Qt.gray)
            painter.drawLine(width-2, 0, width-2, height-1)
            painter.setFont(self.timeFont)
            time_str = datetime.now().strftime("%H:%M:%S")
            painter.drawText(width-64, 16, time_str)
