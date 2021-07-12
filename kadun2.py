# 思路是把所有数据处理计算的过程放在主线程之外的子线程内
#
# 问题，如果不对数据进行剪裁，长时间过后主线程内的绘图会消耗比较多的时间
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
import sys, os, random, time, psutil


# from UI import UI_MainWindow

class UI_MainWindow(QMainWindow):
    def __init__(self):
        super(UI_MainWindow, self).__init__()
        self.setWindowTitle('CPUinfo')
        self.setWindowIcon(QIcon('./CPU.png'))
        self.resize(600, 480)

        self.main_widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        self.plot_widget = QWidget()
        self.plot_layout = QGridLayout()
        self.plot_widget.setLayout(self.plot_layout)

        self.plot_plt = pg.PlotWidget()
        self.plot_plt.setYRange(max=100, min=0)
        self.plot_layout.addWidget(self.plot_plt)
        self.plot_plt.setYRange(max=100, min=0)

        self.main_layout.addWidget(self.plot_widget)

        self.setCentralWidget(self.main_widget)


class NewThread(QThread):
    trigger = pyqtSignal(list, list)

    def __init__(self):
        super(NewThread, self).__init__()
        self.dataList = []
        self.timeList = []
        self.a = 0

    def run(self):
        print('NewThread start!')

        while True:
            time.sleep(0.1)
            # Xtime = time.strftime("%H%M%S")
            Ycpu = "%0.2f" % psutil.cpu_percent(interval=0.1)
            self.dataList.append(float(Ycpu))
            self.timeList.append(self.a)
            # timelist.append(float(Xtime))
            # print(Xtime, Ycpu)
            self.a += 1
            self.trigger.emit(self.dataList, self.timeList)


class showMainWindow(UI_MainWindow):
    def __init__(self):
        super(showMainWindow, self).__init__()
        self.Thread1 = NewThread()
        self.Thread1.trigger.connect(self.Plot)

        self.Thread1.start()

    def Plot(self, list, list1):
        self.plot_plt.plot().setData(list1[len(list1) - 2:], list[len(list) - 2:], pen='g', symbol='o')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = showMainWindow()
    gui.show()
    sys.exit(app.exec_())
