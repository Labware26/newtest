import random

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
import sys


class SettingsWindow(QtWidgets.QWidget):
    def __init__(self, main_window):
        QtWidgets.QWidget.__init__(self)
        self.main_window1 = main_window
        self.setWindowTitle("Настройки")
        self.resize(500, 500)
        self.but = QtWidgets.QPushButton('Изменить оценку', self)
        self.but.clicked.connect(self.close_window)

    def close_window(self):
        self.close()
        self.main_window1.lable_est.setText(str(random.randint(1, 100)))
        # self.main_window1.lable_name.setText('fdff')


class MainCircleWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnBottomHint)
        self.setWindowTitle("Создание окна произвольной формы")
        self.resize(230, 230)
        self.move(1680, 40)
        pixmap = QtGui.QPixmap("fon.png")
        pal = self.palette()
        pal.setBrush(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QBrush(pixmap))
        pal.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, QtGui.QBrush(pixmap))
        self.setPalette(pal)
        self.setMask(pixmap.mask())

        self.button1 = QtWidgets.QPushButton(self)
        self.button1.setFixedSize(38, 30)
        self.button1.move(54, 162)
        self.button1.clicked.connect(QtWidgets.qApp.quit)
        self.button1.setIcon(QtGui.QIcon('refresh.png'))
        self.button1.setIconSize(QtCore.QSize(24, 24))
        self.button1.setStyleSheet(
            'background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(153, 153, 153, 255), stop:1 rgba(255, 255, 255, 255)); border-radius: 15px;')
        self.button1.setToolTip('Обновить данные из JIRA')

        self.button2 = QtWidgets.QPushButton(self)
        self.button2.setFixedSize(38, 30)
        self.button2.move(96, 162)
        self.button2.clicked.connect(self.window_settings)
        self.button2.setIcon(QtGui.QIcon('while.png'))
        self.button2.setIconSize(QtCore.QSize(24, 24))
        self.button2.setStyleSheet(
            'background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(153, 153, 153, 255), stop:1 rgba(255, 255, 255, 255)); border-radius: 15px;')
        self.button2.setToolTip('Настройки')

        self.button3 = QtWidgets.QPushButton(self)
        self.button3.setFixedSize(38, 30)
        self.button3.move(138, 162)
        self.button3.clicked.connect(QtWidgets.qApp.quit)
        self.button3.setIcon(QtGui.QIcon('Red-Close-Button.png'))
        self.button3.setIconSize(QtCore.QSize(24, 24))
        self.button3.setStyleSheet(
            'background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(153, 153, 153, 255), stop:1 rgba(255, 255, 255, 255)); border-radius: 15px;')
        self.button3.setToolTip('Закрыть программу')

        self.lable_est = QtWidgets.QLabel('384.6', self)
        self.lable_est.setFixedSize(186, 90)
        self.lable_est.setAlignment(QtCore.Qt.AlignCenter)
        font3 = QtGui.QFont()
        font3.setPointSize(40)
        font3.setBold(True)
        self.lable_est.setFont(font3)
        self.lable_est.setStyleSheet('color:rgb(85, 85, 85); background-color:rgb(225, 214, 170); border-radius: 15px')
        self.lable_est.move(22, 70)

        self.lable_att = QtWidgets.QLabel(self)
        self.lable_att.setFixedSize(27, 24)
        pixmap1 = QtGui.QPixmap("attention.png")
        self.lable_att.setPixmap(pixmap1)
        self.lable_att.move(102, 195)
        self.lable_att.setToolTip('Обнаружены следующие ошибки:\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd')
        # lable_att.hide()

        self.lable_date = QtWidgets.QLabel('с 2022-01-01 по 2022-01-31', self)
        self.lable_date.setFixedSize(170, 24)
        font4 = QtGui.QFont()
        font4.setPointSize(8)
        font4.setBold(False)
        self.lable_date.setFont(font4)
        self.lable_date.setAlignment(QtCore.Qt.AlignCenter)
        self.lable_date.move(30, 48)

        self.lable_name = QtWidgets.QLabel('Салпагаров', self)
        self.lable_name.setFixedSize(170, 24)
        font5 = QtGui.QFont()
        font5.setPointSize(14)
        font5.setBold(True)
        self.lable_name.setFont(font5)
        self.lable_name.setAlignment(QtCore.Qt.AlignCenter)
        self.lable_name.setStyleSheet('color:rgb(85, 85, 85);')
        self.lable_name.move(30, 25)

        self.two_window = SettingsWindow(self)
        # self.two_window2 = QtWidgets.QDialog()

    def window_settings(self):
        print('Создание второго окна')
        self.two_window.show()









if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = MainCircleWindow()
    mw.show()

    sys.exit(app.exec_())

