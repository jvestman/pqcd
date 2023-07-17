from PySide2.QtCore import Slot, QRunnable
from PySide2.QtGui import QImage, QPixmap, QPainter, qRgb, QFont
from PySide2.QtCore import Qt
import pyfftw
import numpy as np
from morse import Morse
from time_marker import TimeMarker
from character_painter import CharacterPainter
from log import Log
import pyaudio
import time


class Worker(QRunnable):

    def __init__(self, window, audio):
        super(Worker, self).__init__()
        self.exiting = False
        self.window = window
        self.audio = audio
        self.chunk = int(self.window.chunksize.currentText())
        self.break_threshold = - self.window.break_threshold.value()
        self.dat_threshold = self.window.dat_threshold.value()
        self.morse = None
        self.frequency = 0
        self.log = None
        self.detect_threshold = 0

    @Slot(str)
    def set_chunk_size(self):
        self.chunk = int(self.window.chunksize.currentText())

    @Slot(str)
    def set_threshold(self):
        self.break_threshold = - self.window.break_threshold.value()
        self.dat_threshold = self.window.dat_threshold.value()
        self.morse.break_threshold = self.break_threshold
        self.morse.dat_threshold = self.dat_threshold

    @Slot(str)
    def set_detect_threshold(self):
        self.detect_threshold = 2 ** (self.window.detect_threshold.value()/3)
        self.morse.value_threshold = self.detect_threshold


    @Slot()
    def run(self):
        deviceIndex = self.window.device.currentIndex()
        sample_format = pyaudio.paUInt8  # 8 bits per sample
        channels = 1
        fs = int(self.window.framerate.currentText())

        stream = self.audio.open(format=sample_format,
                                 channels=channels,
                                 rate=fs,
                                 frames_per_buffer=64,
                                 input=True, input_device_index=deviceIndex)

        chunks = int(self.window.nochunks.currentText())
        width = self.window.label.frameGeometry().width() - 64
        height = self.window.label.frameGeometry().height()

        image = QImage(width+64, height, QImage.Format_RGB888)
        self.window.label.setPixmap(QPixmap(image))
        painter = QPainter(image)
        painter2 = QPainter(self.window.label.pixmap())

        self.paint_freqs(painter2, fs, height)

        self.maxs = 0.001

        bins = self.chunk * chunks / 2
        offset = 512/bins

        dit_threshold = 1

        loops_since_refresh = 0
        pyfftw.config.NUM_THREADS = 4
        pyfftw.config.PLANNER_EFFORT = 'FFTW_MEASURE'

        time_marker = TimeMarker()
        character_painter = CharacterPainter(width, height, painter, offset)

        self.morse = Morse(bins, self.detect_threshold, dit_threshold, self.dat_threshold, self.break_threshold)
        self.set_detect_threshold()
        self.morse.add_listener(character_painter)
        channel_bandwidth = fs/self.chunk
        self.log = Log(self.window.log, channel_bandwidth)
        self.morse.add_listener(self.log)
        last_freq = self.frequency
        while self.exiting is False:
            rescaled = self.fft(stream)

            self.scroll_waterfall(width, height, image, painter)

            for y, value in enumerate(rescaled):
                self.paint_sample(width, height, image, painter, offset, y, value)
                self.morse.decode_morse(y, value)

            time_marker.paint(width, height, painter)
            if last_freq != self.frequency:
                self.paint_freqs(painter2, fs, height)
                last_freq = self.frequency

            time.sleep(0.001)

            if loops_since_refresh > 3:
                painter2.drawImage(64, 0, image, 65, 0, width, height)
                self.window.label.update()
                loops_since_refresh = 0
            else:
                loops_since_refresh = loops_since_refresh + 1

        if painter:
            painter.end()
            painter2.end()
            del painter
        if image:
            del image

    def scroll_waterfall(self, width, height, image, painter):
        painter.drawImage(64, 0, image, 65, 0, width-64, height)
        painter.fillRect(width+1, 0, 63, height-1, Qt.black)
        x = width+self.detect_threshold/6+1
        painter.drawLine(x, 0, x, height)

    def fft(self, stream):
        buffer = bytearray(stream.read(self.chunk))
        signal = np.frombuffer(buffer, dtype=np.uint8)
        fourier = pyfftw.interfaces.numpy_fft.rfft(signal)
        fourier = np.delete(fourier, 0)
        absolutes = np.absolute(fourier)
        absolutes[0] = 0
        self.maxs = max([np.max(absolutes), self.maxs])
        rescaled = (255.0 / self.maxs * absolutes).astype(np.uint8)
        return rescaled

    def paint_sample(self, width, height, image, painter, offset, y, value):
        value_y = height-(y*offset)-1
        image.setPixel(width-1, value_y, qRgb(value, value, value))
        bar_width = width+value/6+1
        painter.setPen(Qt.white)
        painter.drawLine(width+1, value_y, bar_width, value_y)

    def paint_freqs(self, painter, fs, height):
        """Paint frequency scale to image"""

        painter.fillRect(0, 0, 63, height-1, Qt.black)

        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 10))

        for y in range(1, 512, 16):
            audio_freq = int((y-1)*(fs/(2*512)))
            freq = self.frequency + audio_freq
            painter.drawText(0, height-y-1, f"{freq:,.2f}".replace(',', ' '))
        return painter
