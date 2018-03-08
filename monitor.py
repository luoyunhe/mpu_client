# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\lyh\eric work\test.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

import sys
import struct
from fun import *
from ui import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QByteArray, QThread, QMutex, QWaitCondition, QTimer, QObject
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket, QUdpSocket, QHostAddress
from PyQt5.QtWidgets import QMessageBox
from simpletreemodel import TreeModel
import socket
import numpy as np
import math

class tcpWorker(QObject):
    def __init__(self, parent = None):
        super(tcpWorker, self).__init__(parent)
    addDataSignal = QtCore.pyqtSignal(list)
    def download(self, tuple):
        # print("download")
        socket = tuple[0]
        path = tuple[1]
        percent = tuple[2]
        dataList = []
        packetLength = len(path) + 10
        msg = struct.pack('<3sIHHHI', b'KDS', packetLength, 6, 0, 0, percent)
        msg += path
        socket.write(QByteArray(msg))
        socket.waitForBytesWritten(1000)
        socket.waitForReadyRead(5000)
        respond = b''
        respond += socket.read(11)
        # print(respond)
        while len(respond) < 11:
            socket.waitForReadyRead(100)
            respond += socket.read(36 - len(respond))
        str, length, packetSize, = struct.unpack('<3sII', respond)
        # print(length)
        # print(packetSize)

        if str == b'KDS':
            while packetSize > 0:
                packetSize -= 1
                packet = b''
                packet += socket.read(36)
                while len(packet) < 36:
                    socket.waitForReadyRead(100)
                    packet += socket.read(36 - len(packet))
                datatuple = struct.unpack('<9f', packet)
                # print(datatuple)
                yaw = math.radians(datatuple[6])
                pitch = math.radians(datatuple[7])
                roll = math.radians(datatuple[8])
                Rx = np.mat([[1, 0, 0], [0, math.cos(roll), -math.sin(roll)], [0, math.sin(roll), math.cos(roll)]])
                Ry = np.mat([[math.cos(pitch), 0, math.sin(pitch)], [0, 1, 0], [-math.sin(pitch), 0, math.cos(pitch)]])
                Rz = np.mat([[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]])
                Vx = np.mat([[1], [0], [0]])
                Vy = np.mat([[0], [1], [0]])
                Vz = np.mat([[0], [0], [1]])
                Vxx = Rx * Ry * Rz * Vx
                Vyy = Rx * Ry * Rz * Vy
                Vzz = Rx * Ry * Rz * Vz
                dataList.append([datatuple[0:6], Vxx.tolist(), Vyy.tolist(), Vzz.tolist()])

            self.addDataSignal.emit(dataList)




class tcpThread(QThread):
    def __init__(self, parent = None):
        super(tcpThread, self).__init__(parent)
        self.W = tcpWorker()
    def run(self):
        # pass
        self.exec_()

class worker(QObject):
    def __init__(self, s, p, parent = None):
        super(worker, self).__init__(parent)
        self.socket = s
        self.path = p
        self.dataList = []
        self.percent = 0
        self.check()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check)
        self.timer.start(3000)
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.update)
        self.timer2.start(33)
    updateSignal = QtCore.pyqtSignal(list)
    updateSlide = QtCore.pyqtSignal(int)
    downloadSignal = QtCore.pyqtSignal(tuple)
    def check(self):
        if len(self.dataList) < 50:
            # print("place 1")
            self.downloadSignal.emit((self.socket, self.path, self.percent))
            self.percent += 1
            self.percent %= 100
            self.updateSlide.emit(self.percent)
            print('precent = ', self.percent)
    def update(self):
        if len(self.dataList) > 0:
            # print("update")
            # print(type(self.dataList[0]))
            # print(self.dataList[0])
            self.updateSignal.emit(self.dataList.pop(0))
            # self.updateSignal.emit(self.dataList.pop(0))
            # self.updateSignal.emit(self.dataList.pop(0))
    def addData(self, list):
        self.dataList.extend(list)

    def onSliderValueChange(self, p):
        pass
        # self.percent = p
        # self.dataList = []
        # self.check()


class HThread(QThread):
    def __init__(self, s, p, parent = None):
        super(HThread, self).__init__(parent)
        self.socket = s
        self.path = p
        self.W = worker(s=self.socket, p=self.path)
        self.tcpThread = tcpThread()
    def run(self):

        # self.tcpThread.W.moveToThread(self.tcpThread)
        self.W.downloadSignal.connect(self.tcpThread.W.download)
        self.tcpThread.W.addDataSignal.connect(self.W.addData)
        self.tcpThread.start()
        self.exec_()

class udpThread(QThread):
    def __init__(self, M, parent = None):
        super(udpThread, self).__init__(parent)
        self.monitor = M
        self.accel = M.ui.accelWidget
        self.gyro = M.ui.gyroWidget
        self.euler = M.ui.eulerWidget
    updateSignal = QtCore.pyqtSignal(list)

    def run(self):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(('',5555))
        while True:
            data, addr = self.udpSocket.recvfrom(36)
            # print(len(data))
            if data[0:3] == b'bye':
                print('client has exit')
                break
            else:
                # print('received:', data, " from", addr)
                datatuple = struct.unpack('<9f', data)
                # print(datatuple)
                yaw = math.radians(datatuple[6])
                pitch = math.radians(datatuple[7])
                roll = math.radians(datatuple[8])
                # yaw = math.radians(0)
                # pitch = math.radians(0)
                # roll = math.radians(90)
                Rx = np.mat([[1, 0, 0], [0, math.cos(roll), -math.sin(roll)], [0, math.sin(roll), math.cos(roll)]])
                Ry = np.mat([[math.cos(pitch), 0, math.sin(pitch)], [0, 1, 0], [-math.sin(pitch), 0, math.cos(pitch)]])
                Rz = np.mat([[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]])
                Vx = np.mat([[1], [0], [0]])
                Vy = np.mat([[0], [1], [0]])
                Vz = np.mat([[0], [0], [1]])
                # print(datatuple[6:9])
                Vxx = Rx * Ry * Rz * Vx
                Vyy = Rx * Ry * Rz * Vy
                Vzz = Rx * Ry * Rz * Vz
                self.updateSignal.emit([datatuple[0:6], Vxx.tolist(), Vyy.tolist(), Vzz.tolist()])
                # print(Vxx.tolist(), Vyy.tolist(), Vzz.tolist())
                # print([datatuple[0:6], np.array(Vxx)])


        self.udpSocket.close()


class Monitor(QtWidgets.QMainWindow):
    def __init__(self):
        super(Monitor, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('& About', self.about)
        self.s = QTcpSocket(self)
        self.ui.BtnShow.setEnabled(False)
        self.ui.BtnCon.clicked.connect(self.connectToServer)
        self.ui.BtnDiscon.clicked.connect(self.disconnectToServer)
        self.ui.RBHistory.clicked.connect(self.onClickRBHistory)
        self.ui.RBRealTime.clicked.connect(self.onClickRBRealTime)
        self.ui.BtnRef.clicked.connect(self.reflesh)
        self.treeModel = TreeModel(QByteArray())
        self.ui.treeView.setModel(self.treeModel)
        self.ui.treeView.clicked.connect(self.onClickDir)
        self.ui.BtnShow.clicked.connect(self.showChart)
        self.s.error.connect(self.netError)
        self.s.connected.connect(self.netConnect)
        self.s.disconnected.connect(self.netDisconnect)
        self.timer0Id = 0
        self.timer1Id = 0
        self.isShow = False
    quitSignal = QtCore.pyqtSignal()
    def about(self):
        QtWidgets.QMessageBox.about(self, "About",
"""                    JNU                
Department of electronic engineering  
                    2017
"""
                                    )
    def onClickRBHistory(self):
        self.ui.BtnShow.setEnabled(False)
        self.ui.BtnRef.setEnabled(True)
    def onClickRBRealTime(self):
        self.ui.BtnShow.setEnabled(True)
        self.ui.BtnRef.setEnabled(False)
        self.ui.lineEdit.setText("")
    def onClickDir(self, QModelIndex):
        if QModelIndex.parent().isValid():
            self.path = self.treeModel.itemData(QModelIndex.parent())[0]
            self.path = self.path + b'/' + self.treeModel.itemData(QModelIndex)[0]
            self.ui.lineEdit.setText(self.path.data().decode())
            self.ui.BtnShow.setEnabled(True)

    def netError(self, netError):
        self.ui.BtnCon.setEnabled(True)
        print(netError)
        QMessageBox.warning(self, ("error"), ("Net Error!"),
                            QMessageBox.StandardButtons(QMessageBox.Close))
    def netConnect(self):
        self.ui.BtnCon.setEnabled(False)
        self.ui.BtnDiscon.setEnabled(True)
        self.ui.RBHistory.setEnabled(True)
        self.ui.RBRealTime.setEnabled(True)
        self.ui.BtnShow.setEnabled(True)
    def netDisconnect(self):
        self.ui.BtnDiscon.setEnabled(False)
        self.ui.BtnCon.setEnabled(True)
        self.ui.RBRealTime.setChecked(True)
        self.ui.RBHistory.setEnabled(False)
        self.ui.RBRealTime.setEnabled(False)
        self.ui.BtnRef.setEnabled(False)
        self.ui.BtnShow.setEnabled(False)
        self.treeModel = TreeModel(QByteArray())
        self.ui.treeView.setModel(self.treeModel)
        self.ui.lineEdit.setText("")
        self.ui.BtnShow.setText("Show")
        self.isShow = False

    def showChart(self):
        if self.ui.RBRealTime.isChecked():
            self.ui.BtnShow.setEnabled(False)
            if not self.isShow:
                self.ui.BtnShow.setText("Stop")
                self.ui.RBHistory.setEnabled(False)
                self.ui.RBRealTime.setEnabled(False)
                self.msg = struct.pack('<3sIHHH',b'KDS',6,3,0,0)
            else:
                self.ui.accelWidget.clearData()
                self.ui.gyroWidget.clearData()
                self.ui.BtnShow.setText("Show")
                self.ui.RBHistory.setEnabled(True)
                self.ui.RBRealTime.setEnabled(True)
                self.msg = struct.pack('<3sIHHH', b'KDS', 6, 4, 0, 0)

            self.s.write(QByteArray(self.msg))
            self.s.waitForBytesWritten(1000)
            self.s.waitForReadyRead(3000)
            respond = self.s.read(7)
            str, length = struct.unpack('<3sI', respond)
            tmp = QByteArray()
            if str == b'KDS':
                tmp.append(self.s.read(length))
                while len(tmp) < length:
                    self.s.waitForReadyRead(10000)
                    tmp.append(self.s.read(length - len(tmp)))
                if tmp.data().decode() == 'OK':
                    if not self.isShow:
                        self.myThread = udpThread(self)
                        self.myThread.updateSignal.connect(self.updateSlot)
                        self.myThread.start()
                        self.isShow = True
                    else:
                        self.isShow = False
                        pass
            self.timer1Id = self.startTimer(1000)
        else:
            self.ui.BtnShow.setEnabled(False)
            if not self.isShow:
                # self.ui.horizontalSlider.setEnabled(True)
                self.ui.BtnShow.setText("Stop")
                self.ui.RBHistory.setEnabled(False)
                self.ui.RBRealTime.setEnabled(False)
                self.HThread = HThread(s  = self.s, p = self.path)
                self.HThread.W.moveToThread(self.HThread)
                self.HThread.W.timer.moveToThread(self.HThread)
                self.HThread.W.timer2.moveToThread(self.HThread)
                self.HThread.tcpThread.W.moveToThread(self.HThread.tcpThread)
                self.HThread.W.updateSignal.connect(self.updateSlot)
                self.HThread.W.updateSlide.connect(self.onControlSlider)
                self.ui.horizontalSlider.valueChanged.connect(self.HThread.W.onSliderValueChange)
                self.quitSignal.connect(self.HThread.quit)
                self.quitSignal.connect(self.HThread.tcpThread.quit)
                self.HThread.start()
                self.isShow = True
            else:
                self.ui.accelWidget.clearData()
                self.ui.gyroWidget.clearData()
                self.HThread.W.timer.stop()
                self.HThread.W.timer2.stop()
                self.quitSignal.emit()
                self.HThread.wait()
                # self.ui.horizontalSlider.setEnabled(True)
                self.ui.BtnShow.setText("Show")
                self.ui.RBHistory.setEnabled(True)
                self.ui.RBRealTime.setEnabled(True)
                self.isShow = False

            self.timer1Id = self.startTimer(2000)
            print("history")
    def reflesh(self):
        self.ui.BtnRef.setEnabled(False)
        msg = struct.pack('<3sIHHH',b'KDS',6,5,0,0)
        self.s.write(QByteArray(msg))
        self.s.waitForBytesWritten(1000)
        self.s.waitForReadyRead(3000)
        respond = self.s.read(7)
        str, length = struct.unpack('<3sI', respond)
        print(length)
        tmp = QByteArray()
        if str == b'KDS':
            tmp.append(self.s.read(length))
            while len(tmp) < length:
                self.s.waitForReadyRead(10000)
                tmp.append(self.s.read(length - len(tmp)))
            self.treeModel = TreeModel(tmp)
            self.ui.treeView.setModel(self.treeModel)
        self.timer0Id = self.startTimer(2000)

    def connectToServer(self):
        if is_valid_ip(self.ui.LEIP.text()) and self.ui.LEPort.text().isdigit():
            self.s.connectToHost(self.ui.LEIP.text(), int(self.ui.LEPort.text()))
            self.ui.BtnCon.setEnabled(False)
        else:
            QMessageBox.warning(self, ("error"), ("incorrect IP address or Port"),
                                QMessageBox.StandardButtons(QMessageBox.Close))

    def disconnectToServer(self):
        if self.isShow and self.ui.RBHistory.isChecked():
            self.showChart()
        self.s.close()

    def updateSlot(self, data):
        self.ui.accelWidget.new_data(data[0][0:3])
        self.ui.gyroWidget.new_data(data[0][3:6])
        # print(data[1:4])
        self.ui.eulerWidget.new_data(data[1:4])
        # print(data)
    def onControlSlider(self, percent):
        self.ui.horizontalSlider.setValue(percent)
    def timerEvent(self, event):
        if event.timerId() == self.timer0Id:
            self.ui.BtnRef.setEnabled(True)
            self.killTimer(self.timer0Id)
        elif event.timerId() == self.timer1Id:
            self.ui.BtnShow.setEnabled(True)
            self.killTimer(self.timer1Id)








if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    print(QThread.currentThreadId())
    myMonitor = Monitor()
    myMonitor.show()
    sys.exit(app.exec_())