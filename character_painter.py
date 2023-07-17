from PySide2.QtCore import Qt


class CharacterPainter:

    def __init__(self, width, height, painter, offset):
        self.width = width
        self.height = height
        self.painter = painter
        self.offset = offset

    def character(self, y, character):
        self.painter.setPen(Qt.white)
        char_x = self.width-16
        char_y = self.height-(y*self.offset)-1
        self.painter.drawText(char_x, char_y, character)

    def dat(self, y, width):
        self.painter.setPen(Qt.blue)
        x = self.width-width
        y = self.height-(y*self.offset)
        self.painter.drawLine(x, y, self.width-1, y)

    def dit(self, y, width):
        self.painter.setPen(Qt.red)
        x = self.width-width
        y = self.height-(y*self.offset)
        self.painter.drawLine(x, y, self.width-1, y)

    def unrecognized(self, y, width):
        self.character(y, "#")
        self.painter.setPen(Qt.yellow)
        x = self.width-width-1
        y = self.height-(y*self.offset)
        self.painter.drawLine(x, y, self.width-1, y)
