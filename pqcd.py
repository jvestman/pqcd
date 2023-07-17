import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile, QIODevice, Slot, QThreadPool
import threading
import socket
import time
import pyaudio
from worker import Worker

window = None
audio = None
threadpool = None
worker = None
chunk = 64


def freq_monitor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 7356))
    while worker.exiting is False:
        time.sleep(1)
        sock.send(bytes("f\n", "ascii"))
        frequency = int(str(sock.recv(1024), "ascii"))
        worker.frequency = frequency
        window.frequency.setText(str(frequency) + " Hz")
        worker.log.frequency = frequency

@Slot()
def record():
    global worker
    if window.record.text() == "Stop":
        worker.exiting = True
        window.record.setText("Record")
    else:
        window.record.setText("Stop")
        if worker and worker.exiting:
            worker = Worker(window, audio)
        threadpool.start(worker)
        freq_monitor_thread = threading.Thread(target=freq_monitor)
        freq_monitor_thread.start()


def resizeEvent(self, event):
    print("Resize")


def myExitHandler():
    worker.exiting = True


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ui_file_name = "pqcd.ui"
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        sys.exit(-1)

    window.show()
    resizeEvent.__get__(window)

    audio = pyaudio.PyAudio()  # Create an interface to PortAudio
    for i in range(audio.get_device_count()):
        window.device.addItem(audio.get_device_info_by_index(i)["name"])

    window.device.setCurrentText("pulse")

    threadpool = QThreadPool()
    worker = Worker(window, audio)
    window.record.clicked.connect(record)
    window.chunksize.currentTextChanged.connect(worker.set_chunk_size)
    window.break_threshold.valueChanged.connect(worker.set_threshold)
    window.dat_threshold.valueChanged.connect(worker.set_threshold)
    window.detect_threshold.valueChanged.connect(worker.set_detect_threshold)
    app.aboutToQuit.connect(myExitHandler)

    sys.exit(app.exec_())
