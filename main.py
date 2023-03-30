import shutil
import sys
import psutil
import pynvml
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QProgressBar, QLabel


class CPUMonitorThread(QThread):
    usage_signal = pyqtSignal(int)

    def run(self):
        while True:
            cpu_usage = int(psutil.cpu_percent())
            self.usage_signal.emit(cpu_usage)
            self.msleep(500)


class GPUMonitorThread(QThread):
    usage_signal = pyqtSignal(int)

    def run(self):
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        while True:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_usage = int(mem_info.used / mem_info.total * 100)
            self.usage_signal.emit(gpu_usage)
            self.msleep(500)
        pynvml.nvmlShutdown()


class RAMMonitorThread(QThread):
    usage_signal = pyqtSignal(int)

    def run(self):
        while True:
            ram_usage = int(psutil.virtual_memory().percent)
            self.usage_signal.emit(ram_usage)
            self.msleep(500)


# class DiskMonitorThread(QThread):
#     usage_signal = pyqtSignal(int)
#
#     def run(self):
#         while True:
#             disk_usage = shutil.disk_usage('/')
#             disk_usage_percent = int(disk_usage.used / disk_usage.total * 100)
#             self.usage_signal.emit(disk_usage_percent)
#             self.msleep(500)


class EthernetMonitorThread(QThread):
    usage_signal = pyqtSignal(int)

    def run(self):
        io_counters = psutil.net_io_counters(pernic=True)
        eth0_counters = io_counters.get('eth0', None)
        while True:
            if eth0_counters is not None:
                eth_usage = int(eth0_counters.bytes_sent + eth0_counters.bytes_recv)
            else:
                eth_usage = 0
            self.usage_signal.emit(eth_usage)
            self.msleep(500)


class SystemMonitorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cpu_progress_bar = QProgressBar()
        self.gpu_progress_bar = QProgressBar()
        self.ram_progress_bar = QProgressBar()
        # self.disk_progress_bar = QProgressBar()
        self.eth_progress_bar = QProgressBar()

        cpu_label = QLabel("CPU:")
        gpu_label = QLabel("GPU:")
        ram_label = QLabel("RAM:")
        # disk_label = QLabel("Disk:")
        eth_label = QLabel("Ethernet:")

        layout = QVBoxLayout()
        layout.addWidget(cpu_label)
        layout.addWidget(self.cpu_progress_bar)
        layout.addWidget(gpu_label)
        layout.addWidget(self.gpu_progress_bar)
        layout.addWidget(ram_label)
        layout.addWidget(self.ram_progress_bar)
        # layout.addWidget(disk_label)
        # layout.addWidget(self.disk_progress_bar)
        layout.addWidget(eth_label)
        layout.addWidget(self.eth_progress_bar)
        self.setLayout(layout)

        self.cpu_monitor_thread = CPUMonitorThread()
        self.gpu_monitor_thread = GPUMonitorThread()
        self.ram_monitor_thread = RAMMonitorThread()
        # self.disk_monitor_thread = DiskMonitorThread()
        self.eth_monitor_thread = EthernetMonitorThread()

        self.cpu_monitor_thread.usage_signal.connect(self.cpu_progress_bar.setValue)
        self.gpu_monitor_thread.usage_signal.connect(self.gpu_progress_bar.setValue)
        self.ram_monitor_thread.usage_signal.connect(self.ram_progress_bar.setValue)
        # self.disk_monitor_thread.usage_signal.connect(self.disk_progress_bar.setValue)
        self.eth_monitor_thread.usage_signal.connect(self.eth_progress_bar.setValue)

        self.cpu_monitor_thread.start()
        self.gpu_monitor_thread.start()
        self.ram_monitor_thread.start()
        # self.disk_monitor_thread.start()
        self.eth_monitor_thread.start()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Monitor")
        self.resize(300, 300)
        self.setCentralWidget(SystemMonitorWidget(self))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
