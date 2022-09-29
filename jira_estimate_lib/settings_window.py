from random import randint

from PyQt5.QtCore import pyqtSignal, QEvent, Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QLineEdit


class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        # QWidget.__init__(self)
        super(SettingsWindow, self).__init__(parent, Qt.Window)
        self.main_window1 = parent
        self.setWindowTitle("Настройки")
        self.resize(500, 500)
        self.move(200, 200)
        self.but = QPushButton('Изменить оценку', self)
        self.but.clicked.connect(self.in_main_window)
        self.lab = QLineEdit(self)
        self.lab.move(50, 50)

    def in_main_window(self):
        self.main_window1.lable_est.setText(str(randint(1, 100)))
        pass

    def closeEvent(self, event: QCloseEvent) -> None:
        # self.window_settings_close.emit()
        print('Вызов closeEvent SettingsWindow')
        # super(SettingsWindow, self).closeEvent(event)

    # def event(self, e):
    #     if e.type() == QEvent.Close:
    #         print("Окно закрыто")
    #     return QWidget.event(self, e)  # Отправляем дальше


