from random import randint

from PyQt5.QtCore import pyqtSignal, QEvent, Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QLineEdit, QVBoxLayout


class SettingsWindow(QWidget):
    logout = pyqtSignal()
    def __init__(self, main_window, parent=None):
        # QWidget.__init__(self)
        super(SettingsWindow, self).__init__(parent, Qt.Window)
        self.main_window1 = main_window
        self.setWindowTitle("Настройки")
        self.resize(350, 500)
        self.move(500, 400)

        # central_widget = QWidget(self)
        vertical_layout = QVBoxLayout(self)
        # central_widget.setLayout(vertical_layout)

        btn_log_out = QPushButton('Разлогиниться')
        btn_log_out.clicked.connect(self.__logout)
        vertical_layout.addWidget(btn_log_out, 0)

        btn_edit_estimate = QPushButton('Мне повезет!')
        btn_edit_estimate.clicked.connect(self.in_main_window)
        vertical_layout.addWidget(btn_edit_estimate), 1

        self.lable_test = QLineEdit()
        vertical_layout.addWidget(self.lable_test, 2)

        # self.setCentralWidget(central_widget)

    def in_main_window(self):
        self.main_window1.label_est.setText(str(randint(1, 100)))

    def __logout(self):
        self.logout.emit()

    # def closeEvent(self, event: QCloseEvent) -> None:
        # self.window_settings_close.emit()
        # print('Вызов closeEvent SettingsWindow')
        # super(SettingsWindow, self).closeEvent(event)

    # def event(self, e):
    #     if e.type() == QEvent.Close:
    #         print("Окно закрыто")
    #     return QWidget.event(self, e)  # Отправляем дальше


