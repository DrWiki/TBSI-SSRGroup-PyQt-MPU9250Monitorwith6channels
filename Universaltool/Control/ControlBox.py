import threading
import Control
import sys
import PyQt5
import socket
import pandas as pd
import Universaltool.TransLogic.udp_logic as UDP
import Universaltool.TransLogic.Serial_logic as SER
import Universaltool.TransLogic.tcp_logic as TCP
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
import time
import ctypes
import inspect
import Metadata
import struct
import pyqtgraph as pg
# 强制关闭线程的方法
def _async_raise(tid, exc_type):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exc_type):
        exc_type = type(exc_type)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exc_type))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


class ControlBox(Control.Ui_GroupBox, QtWidgets.QGroupBox, UDP.UdpLogic, TCP.TcpLogic, SER.PyQt_Serial):
    def __init__(self, parent=None):
        super(ControlBox,self).__init__(parent)
        self.setupUi(self)
        self.metadata = Metadata.metadata()
        self.NewTimerX = threading.Thread(target=self.NewTimerfunX)
        self.NewTimerY = threading.Thread(target=self.NewTimerfunY)

        ## 文字
        # 自动填充文字
        self.on_refreshCom()
        self.click_get_ip()
        self.LEUDP2.setText("192.167.43.20")
        self.SBUDP.setValue(8090)
        self.SBUDP2.setValue(1122)
        self.SBTCPServer.setValue(8090)
        self.RBTUDP.setChecked(True)
        self.CONNECT()

    def CONNECT(self):
        self.BTFilePath.clicked.connect(self.ChooseFile)
        self.BTTest.clicked.connect(self.click_get_ip)
        self.BTSend.clicked.connect(self.Send)
        self.BTDisconnect.clicked.connect(self.Disconnect)
        self.BTConnect.clicked.connect(self.Connect)
        self.signal_PackedDataComing.connect(self.Datasplit)


    def Datasplit(self, msg):
        if self.RBTUDP.isChecked():
            datas = struct.unpack('<iffffff', msg)

            self.metadata.DataStreamT.append(datas[0])

            self.metadata.CurrentdataX = datas[1]
            self.metadata.DataStreamX.append(datas[1])
            self.metadata.datareadyX = True

            self.metadata.CurrentdataY = datas[2]
            self.metadata.DataStreamY.append(datas[2])
            self.metadata.datareadyY = True

            self.metadata.CurrentdataZ = datas[3]
            self.metadata.DataStreamZ.append(datas[3])
            self.metadata.datareadyZ = True

            self.metadata.CurrentdataRX = datas[4]
            self.metadata.DataStreamRX.append(datas[4])
            self.metadata.datareadyRX = True

            self.metadata.CurrentdataRY = datas[5]
            self.metadata.DataStreamRY.append(datas[5])
            self.metadata.datareadyRY = True

            self.metadata.CurrentdataRZ = datas[6]
            self.metadata.DataStreamRZ.append(datas[6])
            self.metadata.datareadyRZ = True

    # 自动获取本机IP
    def click_get_ip(self):
        # 获取本机ip
        self.LETCPServer.clear()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            my_addr = s.getsockname()[0]
            self.LETCPServer.setText(str(my_addr))
            self.CBTCP2.addItem("0.0.0.0  :  0000")
            self.LEUDP.setText(str(my_addr))
            self.LEUDP2.setText("0.0.0.0")
            self.signal_write_msg.emit("自动获取IP "+str(my_addr)+"\n")
        except Exception as ret:
            # 若无法连接互联网使用，会调用以下方法
            try:
                my_addr = socket.gethostbyname(socket.gethostname())
                self.LETCPServer.setText(str(my_addr))
            except Exception as ret_e:
                self.signal_write_msg.emit("无法获取ip，请连接网络！\n")
        finally:
            s.close()


    def NewClient(self,tupleinfo):
        self.CBTCP2.addItem(tupleinfo[0] + ":" + str(tupleinfo[1]))

    def ChooseFile(self):
        files = QtWidgets.QFileDialog.getOpenFileNames(self, "CSV选择", "../res/data", "All Files (*)")[0]
        filecsv = pd.read_csv(files[0], sep=',')
        self.metadata.filedataX = filecsv["X"]
        self.metadata.filedataY = filecsv["Y"]
        self.LEFilePath.setText(files[0])

    def on_refreshCom(self):
        self.CBSerial.clear()
        com = QSerialPort()
        for info in QSerialPortInfo.availablePorts():
            com.setPort(info)
            if com.open(QSerialPort.ReadWrite):
                self.CBSerial.addItem(info.portName())
                com.close()

    def write_msg(self, msg):
        self.TERceive.insertPlainText(msg)
        # 滚动条移动到结尾
        self.TERceive.moveCursor(QtGui.QTextCursor.End)

    def Send(self):
        if self.RBTUDP.isChecked():
            self.udp_ip2 = self.LEUDP2.text()
            self.udp_port2 = self.SBUDP2.value()
            self.udp_send(self.TESend.document().toPlainText())

        elif self.RBTSerial.isChecked():
            self.on_sendData(self.TESend.document().toPlainText())

    def Connect(self):
        if self.RBTUDP.isChecked():
            self.udp_port1 = self.SBUDP.value()
            self.udp_server_start()
            self.signal_trigerthread.emit(1)


        elif self.RBTTCPServer.isChecked():
            self.tcp_port1 = self.SBTCPServer.value()
            self.tcp_server_start()

        elif self.RBTSerial.isChecked():
            self.on_openSerial()

        elif self.RBTFile.isChecked():
            self.NewTimerX.start()
            self.NewTimerY.start()
            self.signal_trigerthread.emit(4)

    def Disconnect(self):
        if self.RBTUDP.isChecked():
            self.udp_close()
            self.metadata.save("./data.csv")

        elif self.RBTTCPServer.isChecked():
            self.tcp_close()
        elif self.RBTSerial.isChecked():
            self.on_closeSerial()
        elif self.RBTFile.isChecked():
            stop_thread(self.NewTimerX)
            stop_thread(self.NewTimerY)
            self.metadata.save("./data.csv")


    def NewTimerfunX(self):
        while 1:
            if self.RBTFile.isChecked():
                if self.metadata.filedataX.__len__() > self.metadata.filedataindexX:
                    self.metadata.CurrentdataX = self.metadata.filedataX[self.metadata.filedataindexX]
                    self.metadata.DataStreamX.append(self.metadata.CurrentdataX)
                    self.metadata.datareadyX = True
                    self.metadata.filedataindexX += 1
                else:
                    self.signal_write_msg.emit("文件读取完成！")
                    self.metadata.filedataindexX = 0
                    stop_thread(self.NewTimerX)
            while(self.metadata.datareadyX):
                # print("")
                pg.QtGui.QApplication.processEvents()

            # time.sleep(1)
                # pass
    def NewTimerfunY(self):
        while 1:
            if self.RBTFile.isChecked():
                if self.metadata.filedataY.__len__() > self.metadata.filedataindexY:
                    self.metadata.CurrentdataY = self.metadata.filedataY[self.metadata.filedataindexY]
                    self.metadata.DataStreamY.append(self.metadata.CurrentdataY)
                    self.metadata.datareadyY = True
                    self.metadata.filedataindexY += 1
                else:
                    self.signal_write_msg.emit("文件读取完成！")
                    self.metadata.filedataindexY = 0
                    stop_thread(self.NewTimerY)
            while(self.metadata.datareadyY):
                # print("")
                # pass
                pg.QtGui.QApplication.processEvents()





if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = ControlBox()
    mainWindow.show()
    sys.exit(app.exec_())
