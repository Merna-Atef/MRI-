from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap
from mriui import Ui_MainWindow
from phantom import phantom
import numpy as np
import qimage2ndarray
import sys
import math
import threading
from rotation import rotateX, gradientXY
from RD import recovery, decay
from PyQt5.QtWidgets import QFileDialog

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
        self.ui.startSeq.clicked.connect(self.runSequence)
        self.ui.FlipAngle.textChanged.connect(self.setFA)

        self.ui.phantomlbl.setMouseTracking(False)
        self.ui.phantomlbl.mouseMoveEvent = self.editContrastAndBrightness
        self.ui.phantomlbl.mousePressEvent = self.pixelClicked
        self.ui.phantomlbl.setScaledContents(True)

        self.ui.kspaceLbl.setScaledContents(True)

        self.ui.graphicsPlotT1.setMouseEnabled(False, False)
        self.ui.graphicsPlotT2.setMouseEnabled(False, False)

        # initialization
        self.qimg = None
        self.img = None
        self.originalPhantom = None
        self.T1 = None
        self.T2 = None
        self.phantomSize = 512
        self.FA = 90
        self.TE = 0.001
        self.TR = 0.5

        # For Mouse moving, changing Brightness and Contrast
        self.lastY = None
        self.lastX = None

        # For Contrast Control
        self.contrast = 1.0
        self.brightness = 0

    def showPhantom(self, value):
        size = int(value)
        self.phantomSize = size
        img = phantom(size)
        img = img * 255
        self.img = img
        self.T1 = phantom(size, 'T1')
        self.T2 = phantom(size, 'T2')
        self.originalPhantom = img
        self.showPhantomImage()

    def showPhantomImage(self):
        self.qimg = qimage2ndarray.array2qimage(self.img)
        # self.ui.phantomlbl.setAlignment(QtCore.Qt.AlignCenter)
        # self.ui.phantomlbl.setFixedWidth(self.phantomSize)
        # self.ui.phantomlbl.setFixedHeight(self.phantomSize)
        self.ui.phantomlbl.setPixmap(QPixmap(self.qimg))

    def changePhantomMode(self, value):
        self.img = phantom(self.phantomSize, value)
        self.img = self.img * (255 / np.max(self.img))
        self.originalPhantom = self.img
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

    def pixelClicked(self, event):
        t1Matrix = self.T1
        t2Matrix = self.T2
        xt = self.ui.phantomlbl.frameGeometry().width()
        yt = self.ui.phantomlbl.frameGeometry().height()
        x = event.pos().x() * (self.phantomSize / xt)
        y = event.pos().y() * (self.phantomSize / yt)
        x = math.floor(x)
        y = math.floor(y)
        t1 = t1Matrix[y][x]
        t2 = t2Matrix[y][x]
        self.plotting(t1 * 1000, t2 * 1000)

    def plotting(self, T1=1000, T2=45):
        t1graph = self.ui.graphicsPlotT1
        t2gragh = self.ui.graphicsPlotT2
        t1graph.clear()
        t2gragh.clear()

        t = np.linspace(0, 10000, 1000)
        t1graph.plot(1 - np.exp(-t / T1))
        t2gragh.plot(np.exp(-t / T2))

    def setFA(self, value):
        print(value)

    def runSequence(self):
        threading.Thread(target=self.reconstructImage).start()
        return

    def reconstructImage(self):
        kSpace = np.zeros((self.phantomSize, self.phantomSize), dtype=np.complex_)
        vectors = np.zeros((self.phantomSize, self.phantomSize, 3))
        vectors[:, :, 2] = 1

        for i in range(0, self.phantomSize):
            rotatedMatrix = rotateX(vectors, self.FA)
            decayedRotatedMatrix = decay(rotatedMatrix, self.T2, self.TE)

            for j in range(0, self.phantomSize):
                stepX = (360 / self.phantomSize) * j
                stepY = (360 / self.phantomSize) * i
                phaseEncodedMatrix = gradientXY(decayedRotatedMatrix, stepY, stepX)
                sigmaX = np.sum(phaseEncodedMatrix[:, :, 0])
                sigmaY = np.sum(phaseEncodedMatrix[:, :, 1])
                valueToAdd = np.complex(sigmaX, sigmaY)
                kSpace[i, j] = valueToAdd

            decayedRotatedMatrix[:, :, 0] = 0
            decayedRotatedMatrix[:, :, 1] = 0
            vectors = recovery(decayedRotatedMatrix, self.T1, self.TR)
            self.showKSpace(kSpace)
            print(i)

        kSpace = np.fft.ifftshift(kSpace)
        self.showKSpace(kSpace)

    def showKSpace(self, img):
        qimg = qimage2ndarray.array2qimage(np.abs(img))
        self.ui.kspaceLbl.setPixmap(QPixmap(qimg))


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
