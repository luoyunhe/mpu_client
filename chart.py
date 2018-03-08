# embedding_in_qt5.py --- Simple Qt5 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
# 2006 Darren Dale
# 2015 Jens H Nielsen
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.
from __future__ import unicode_literals
from mpl_toolkits.mplot3d import Axes3D
import sys
import os
import random
import matplotlib
import numpy as np

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from numpy import arange
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
progname = os.path.basename(sys.argv[0])
progversion = "0.1"
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        # self.axes = fig.add_subplot(111)
        self.axes = fig.add_axes([0.1, 0.15, 0.88, 0.8])
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                        QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
    def compute_initial_figure(self):
        pass
class MyAccelDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(50)
        self.index = 0
        self.x = np.linspace(0, 10, 400)
        self.y0 = [0] * 400
        self.y1 = [0] * 400
        self.y2 = [0] * 400
    def clearData(self):
        self.y0 = [0] * 400
        self.y1 = [0] * 400
        self.y2 = [0] * 400
    def compute_initial_figure(self):
        # self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')
        pass

    def new_data(self, data):
        pass

        self.y0 = self.y0[1:400] + [data[0] / 16384]
        self.y1 = self.y1[1:400] + [data[1] / 16384]
        self.y2 = self.y2[1:400] + [data[2] / 16384]

    def update_figure(self):
        self.axes.cla()
        self.axes.set_xlabel('time(s)')
        self.axes.set_ylabel('ACCEL(g)')
        self.axes.plot(self.x, self.y0, 'r')
        self.axes.plot(self.x, self.y1, 'g')
        self.axes.plot(self.x, self.y2, 'b')
        self.draw()

class MyGyroDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(50)
        self.index = 0
        self.x = np.linspace(0, 10, 400)
        self.y0 = [0] * 400
        self.y1 = [0] * 400
        self.y2 = [0] * 400
    def clearData(self):
        self.y0 = [0] * 400
        self.y1 = [0] * 400
        self.y2 = [0] * 400
    def compute_initial_figure(self):
        # self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')
        pass

    def new_data(self, data):
        pass
        self.y0 = self.y0[1:400] + [data[0] * 360]
        self.y1 = self.y1[1:400] + [data[1] * 360]
        self.y2 = self.y2[1:400] + [data[2] * 360]

    def update_figure(self):
        self.axes.cla()
        # self.axes.set_ylim(-1, 1)
        self.axes.set_xlabel('time(s)')
        self.axes.set_ylabel('GYRO(°/s)')
        self.axes.plot(self.x, self.y0, 'r')
        self.axes.plot(self.x, self.y1, 'g')
        self.axes.plot(self.x, self.y2, 'b')
        self.draw()

class My3DMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111, projection='3d')
        self.axes.disable_mouse_rotation()
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class My3DDynamicMplCanvas(My3DMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        My3DMplCanvas.__init__(self, *args, **kwargs)
        self.xx = [0, 0.0]
        self.yx = [0, 0.0]
        self.zx = [0, 0.1]
        self.xy = [0, 0.0]
        self.yy = [0, 0.0]
        self.zy = [0, 0.0]
        self.xz = [0, 0.0]
        self.yz = [0, 0.0]
        self.zz = [0, 0.0]
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(500)

    def new_data(self, list):
        # print(list)
        self.xx[1] = list[0][0][0]
        self.yx[1] = list[0][1][0]
        self.zx[1] = list[0][2][0]
        self.xy[1] = list[1][0][0]
        self.yy[1] = list[1][1][0]
        self.zy[1] = list[1][2][0]
        self.xz[1] = list[2][0][0]
        self.yz[1] = list[2][1][0]
        self.zz[1] = list[2][2][0]
        # print(list[0][2][0])
        # print(self.xx[1], self.yx[1], self.zx[1])
    def compute_initial_figure(self):
        pass

    def update_figure(self):
        self.axes.cla()
        self.axes.set_xlim(-1, 1)
        self.axes.set_ylim(-1, 1)
        self.axes.set_zlim(-1, 1)
        self.axes.plot(self.xx, self.yx, self.zx, 'r')
        # print(self.xx[1], self.yx[1], self.zx[1])
        self.axes.plot(self.xy, self.yy, self.zy, 'g')
        self.axes.plot(self.xz, self.yz, self.zz, 'b')
        # self.axes.plot(self.x, self.y1, 'g')
        # self.axes.plot(self.x, self.y2, 'b')
        self.draw()