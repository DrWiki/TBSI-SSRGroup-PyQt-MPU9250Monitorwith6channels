import WinLayout
import socket
# import pyqtgraph as pg
import pandas as pd
import Universaltool.TransLogic.udp_logic as UDP
import Universaltool.TransLogic.Serial_logic as SER
import Universaltool.TransLogic.tcp_logic as TCP
import sys
import time
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import threading
import pyqtgraph as pg
class WinLogic(WinLayout.WinLayout):

    def __init__(self, parent=None):
        super(WinLogic, self).__init__(parent)
        self.CONNECT()
        self.listlabel = ["X", "Y", "Z", "XR", "YR", "ZR"]
        # self.thlist = [threading.Thread(target=self.update0),threading.Thread(target=self.update1),threading.Thread(target=self.update2),
        #                threading.Thread(target=self.update3),threading.Thread(target=self.update4),threading.Thread(target=self.update5)]
        self.th0 = threading.Thread(target=self.update0)
        self.th1 = threading.Thread(target=self.update1)
        self.th2 = threading.Thread(target=self.update2)
        self.th3 = threading.Thread(target=self.update3)
        self.th4 = threading.Thread(target=self.update4)
        self.th5 = threading.Thread(target=self.update5)

    def CONNECT(self):
        # self.MyCB.signal_NewDataComing.connect(self.ProcessData)
        self.MyCB.signal_trigerthread.connect(self.triger)

    def triger(self, flag):
        if flag==1:
            self.th0.start()
            self.th1.start()
            self.th2.start()
            self.th3.start()
            self.th4.start()
            self.th5.start()

        elif flag==4:
            self.th0.start()
            self.th1.start()

    def update2(self):
        tt = []
        t = 0
        while 1:
            if self.MyCB.metadata.datareadyZ == True:
                self.MyCB.metadata.datareadyZ = False
                tt.append(t)
                if t>500:
                    self.PWPlot1Ploterlist[2].setData(np.array(tt[-501:-1]), np.array(self.MyCB.metadata.DataStreamZ[-501:-1]))
                elif t>3:
                    self.PWPlot1Ploterlist[2].setData(np.array(tt[0:t]), np.array(self.MyCB.metadata.DataStreamZ[0:t]))
                t += 1
            while not self.MyCB.metadata.datareadyZ:
                pg.QtGui.QApplication.processEvents()

    def update1(self):
        tt = []
        t = 0
        while 1:
            if self.MyCB.metadata.datareadyY == True:
                self.MyCB.metadata.datareadyY = False
                tt.append(t)
                if t>500:
                    self.PWPlot1Ploterlist[1].setData(np.array(tt[-501:-1]), np.array(self.MyCB.metadata.DataStreamY[-501:-1]))
                elif t>3:
                    self.PWPlot1Ploterlist[1].setData(np.array(tt[0:t]), np.array(self.MyCB.metadata.DataStreamY[0:t]))
                t += 1
            while not self.MyCB.metadata.datareadyY:
                pg.QtGui.QApplication.processEvents()

    def update0(self):
        tt = []
        t = 0
        while 1:
            if self.MyCB.metadata.datareadyX == True:
                self.MyCB.metadata.datareadyX = False
                tt.append(t)
                if t>500:
                    self.PWPlot1Ploterlist[0].setData(np.array(tt[-501:-1]), np.array(self.MyCB.metadata.DataStreamX[-501:-1]))
                elif t>3:
                    self.PWPlot1Ploterlist[0].setData(np.array(tt[0:t]), np.array(self.MyCB.metadata.DataStreamX[0:t]))
                t += 1
            while not self.MyCB.metadata.datareadyX:
                pg.QtGui.QApplication.processEvents()

    def update3(self):
        tt = []
        t = 0
        while 1:
            if self.MyCB.metadata.datareadyRX == True:
                self.MyCB.metadata.datareadyRX = False
                tt.append(t)
                if t>500:
                    self.PWPlot1Ploterlist[3].setData(np.array(tt[-501:-1]), np.array(self.MyCB.metadata.DataStreamRX[-501:-1]))
                elif t>3:
                    self.PWPlot1Ploterlist[3].setData(np.array(tt[0:t]), np.array(self.MyCB.metadata.DataStreamRX[0:t]))
                t += 1
            while not self.MyCB.metadata.datareadyRX:
                pg.QtGui.QApplication.processEvents()

    def update4(self):
        tt = []
        t = 0
        while 1:
            if self.MyCB.metadata.datareadyRY == True:
                self.MyCB.metadata.datareadyRY = False
                tt.append(t)
                if t>500:
                    self.PWPlot1Ploterlist[4].setData(np.array(tt[-501:-1]), np.array(self.MyCB.metadata.DataStreamRY[-501:-1]))
                elif t>3:
                    self.PWPlot1Ploterlist[4].setData(np.array(tt[0:t]), np.array(self.MyCB.metadata.DataStreamRY[0:t]))
                t += 1
            while not self.MyCB.metadata.datareadyRY:
                pg.QtGui.QApplication.processEvents()
    def update5(self):
        tt = []
        t = 0
        while 1:
            if self.MyCB.metadata.datareadyRZ == True:
                self.MyCB.metadata.datareadyRZ = False
                tt.append(t)
                if t>500:
                    self.PWPlot1Ploterlist[5].setData(np.array(tt[-501:-1]), np.array(self.MyCB.metadata.DataStreamRZ[-501:-1]))
                elif t>3:
                    self.PWPlot1Ploterlist[5].setData(np.array(tt[0:t]), np.array(self.MyCB.metadata.DataStreamRZ[0:t]))
                t += 1
            while not self.MyCB.metadata.datareadyRZ:
                pg.QtGui.QApplication.processEvents()

    # def ProcessData(self, data):
    #
    #     return

    # def ConnectTimerFun(self):
    #     pass

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # app.setAttribute(QtCore.Qt.AA_Use96Dpi)
    mainWindow = WinLogic()
    mainWindow.show()
    sys.exit(app.exec_())
