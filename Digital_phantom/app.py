from PyQt5 import QtWidgets, QtCore, QtGui
from D_ph import Ui_Dialog
import sys
from PyQt5.QtWidgets import QFileDialog


class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
