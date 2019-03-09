from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap
from mriui import Ui_MainWindow
from phantom import phantom
import numpy as np
import qimage2ndarray
import sys
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtTest
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QCoreApplication

MAX_CONTRAST = 2
MIN_CONTRAST = 0.1
MAX_BRIGHTNESS = 100
MIN_BRIGHTNESS = -100
SAFETY_MARGIN = 10


class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.comboSheppSize.currentTextChanged.connect(self.showPhantom)
        self.ui.comboViewMode.currentTextChanged.connect(self.changePhantomMode)
        self.ui.FlipAngle.textChanged.connect(self.validateFA)
        self.ui.TimeRepeat.textChanged.connect(self.validateTR)
        self.ui.TimeEcho.textChanged.connect(self.validateTE)
        self.ui.phantomlbl.setMouseTracking(False)
        self.ui.phantomlbl.mouseMoveEvent = self.editContrastAndBrightness

        self.qimg = None
        self.img = None
        self.originalPhantom = None
        self.FA = 30
        self.TR = 0
        self.TE = 0
        # For Mouse moving, changing Brightness and Contrast
        self.lastY = None
        self.lastX = None

        # For Contrast Control
        self.contrast = 1.0
        self.brightness = 0

    def validateFA(self, value):
        #FA = self.ui.FlipAngle.text()
        if isinstance(value, int): 
            if value >= 0 and value < 90:
                self.FA = value
             
    def validateTE(self, value):
        if isinstance(value, int) and value >= 0 and value < 90:
            self.TE = value
        else:
            self.error('Please enter FA between 0 & 90 deg')

    def validateTR(self, value):
        QtTest.QTest.qWait(200)
        if isinstance(value, int) and value >= 0 and value < 90:
            self.TR = value
        else:
            self.error('Please enter FA between 0 & 90 deg')

    def error(self, message):
        warning = QMessageBox()
        warning.setIcon(QMessageBox.Warning)
        warning.setWindowTitle('WARNING')
        warning.setText(message)
        warning.setStandardButtons(QMessageBox.Ok)
        warning.exec_()

    def showPhantom(self, value):
        size = int(value)
        img = phantom(size)
        img = img * 255
        self.img = img
        self.originalPhantom = img
        self.showPhantomImage(size)

    def showPhantomImage(self, size=512):
        self.qimg = qimage2ndarray.array2qimage(self.img)
        self.ui.phantomlbl.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.phantomlbl.setPixmap(QPixmap(self.qimg))

    def changePhantomMode(self, value):
        if value == "T1":
            self.img = self.img % 90
            self.showPhantomImage()
        if value == "T2":
            self.img = self.img % 900
            self.showPhantomImage()

    def editContrastAndBrightness(self, event):
        if self.lastX is None:
            self.lastX = event.pos().x()
        if self.lastY is None:
            self.lastY = event.pos().y()
            return

        currentPositionX = event.pos().x()
        if currentPositionX - SAFETY_MARGIN > self.lastX:
            self.contrast += 0.01
        elif currentPositionX < self.lastX - SAFETY_MARGIN:
            self.contrast -= 0.01

        currentPositionY = event.pos().y()
        if currentPositionY - SAFETY_MARGIN > self.lastY:
            self.brightness += 1
        elif currentPositionY < self.lastY - SAFETY_MARGIN:
            self.brightness -= 1
        # Sanity Check
        if self.contrast > MAX_CONTRAST:
            self.contrast = MAX_CONTRAST
        elif self.contrast < MIN_CONTRAST:
            self.contrast = MIN_CONTRAST
        if self.brightness > MAX_BRIGHTNESS:
            self.brightness = MAX_BRIGHTNESS
        elif self.brightness < MIN_BRIGHTNESS:
            self.brightness = MIN_BRIGHTNESS

        self.img = 128 + self.contrast * (self.originalPhantom - 128)
        self.img = np.clip(self.img, 0, 255)

        self.img = self.img + self.brightness
        self.img = np.clip(self.img, 0, 255)
        self.showPhantomImage()

        self.lastY = currentPositionY
        self.lastX = currentPositionX
        
    def plotting(self, T1=1000, T2=300):
        t1graph = self.ui.graphicsPlotT1
        t2gragh = self.ui.graphicsPlotT2
        #t1graph.clear()
       # t2gragh.clear()
        t = np.linspace(0, 10000, 100)
        deltT = t/T1
        t1 = np.exp(deltT) 	
        angle = np.cos(self.FA)*t1
        t1graph.plot(angle)
        t2gragh.plot(-np.sin(self.FA)*np.exp(-t/T2))  

def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
