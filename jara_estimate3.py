from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QStyle, qApp, QAction, QMessageBox
from PyQt5.QtCore import QTimer
import sys
from github.jira_estimate_lib.windows import CircleApp, AuthorizationWindow, RectApp, PrintApp
from github.jira_estimate_lib.connect_to_jira import ConnectionToJIRA
from jira_estimate_lib.configuration import Configuration


class MainWindowApp(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.conf = Configuration()  # Считываем файл конфигурации
        self.connect_jira = None  # Создаем заранее переменную для подключения к JIRA
        # Таймаут для того что бы делать неактивным интерфейс перед попыткой подключиться к JIRE
        self.timer_set_enable = QTimer()
        self.timer_set_enable.timeout.connect(self.__serverConnection)

        # Создаем окно авторизации и заполняем поля из файла конфигурации
        self.__authorizationWindow(*self.conf.getUrlLoginPassword())
        self.__startTimeoutServerConnection()  # Пробуем подключатся к JIRA

    def __buildMainWindow(self) -> None:
        """Конструктор главного окна программы"""
        # Создаем иконку в системном трее и крепим к ней контекстное меню
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        quit_action = QAction("Закрыть", self)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        if self.conf.get_launch_mode() == 'circle':
            self.__circleApp()
        elif self.conf.get_launch_mode() == 'print':
            self.__printApp()
        else:
            self.__rectApp()

    def __serverConnection(self) -> None:
        """Пробуем подключатся к JIRA"""
        if self.auth_window.isFieldsAreNotEmpty():
            self.connect_jira = ConnectionToJIRA(*self.auth_window.getFieldContent())
            if self.connect_jira.connectionStatus() == 1:
                self.conf.set_url_login_password(*self.auth_window.getFieldContent())  # Сохраняем успешные данные
                self.auth_window.close()
                self.__buildMainWindow()
            elif self.connect_jira.connectionStatus() == 2:
                self.__failedAuthorization('Ошибка авторизации!')
            elif self.connect_jira.connectionStatus() == 3:
                self.__failedAuthorization('Ошибка подключения к серверу!')
            else:
                self.__failedAuthorization('Неизвестная ошибка!')
        else:
            self.__failedAuthorization('Ожидается авторизация')
        self.timer_set_enable.stop()

    def __startTimeoutServerConnection(self) -> None:
        """Таймаут перед попыткой подключения к серверу JIRA"""
        self.auth_window.setInterfaceEnable(False)
        self.timer_set_enable.start(100)

    def __failedAuthorization(self, message: str) -> None:
        """Выводит сообщение о неудачной авторизации и активирует интерфейс для ввода"""
        self.auth_window.label_status_authorization.setText(message)
        self.auth_window.setInterfaceEnable(True)
        if message != 'Ожидается авторизация':
            QMessageBox.warning(self.auth_window, 'Ошибка', message)

    def __authorizationWindow(self, url, login, password) -> None:
        self.auth_window = AuthorizationWindow(self)
        self.auth_window.inFieldsFromFileConfiguration(url, login, password)
        self.auth_window.btn_ok.clicked.connect(self.__startTimeoutServerConnection)  # отслеживаем клик по ОК в окне авторизации

    def __circleApp(self):
        """"Создает окно круглого дизайна"""
        cfo = self.conf
        self.window_app = CircleApp(self)
        self.window_app.button_logout.clicked.connect(self.__logout)
        self.window_app.show()

    def __rectApp(self):
        """Создает окно квадратного дизайна"""
        self.window_app = RectApp(self)
        self.window_app.btn_logout.clicked.connect(self.__logout)
        self.tray_icon.activated.connect(self.__one_click)  # При нажатии ЛКМ по значку в трее, окно развернется
        self.window_app.show()

    def __printApp(self):
        """Создает окно для вывода отчета в файл"""
        self.window_app = PrintApp(self)
        self.window_app.show()

    def __one_click(self, reason):
        """При нажатии иконки в трее ЛКМ окно отобразиться на 10 секунд"""
        if reason == QSystemTrayIcon.Trigger:
            self.window_app.window_show_hide()

    def __logout(self):
        self.window_app.close()
        self.__authorizationWindow(self.conf.get_url_server_jira(), '', '')
        self.conf.set_url_login_password(*self.auth_window.getFieldContent())





if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_app = MainWindowApp()
    sys.exit(app.exec_())
