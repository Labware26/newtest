from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSystemTrayIcon, QSpacerItem, \
    QSizePolicy, QMenu, QStyle, qApp, QAction, QPushButton, QPlainTextEdit, QLabel, QLineEdit, QHBoxLayout, QFrame, \
    QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer, QSize, Qt
from PyQt5.QtGui import QFont, QColor
from jira import JIRA
import datetime
from re import search
import sys
import json


class FileIsNotCorrectError(Exception):
    def __init__(self, *arg):
        pass


class Configuration:
    def __init__(self):
        default_configuration = {'url_server_jira': 'http://192.168.100.230:8080/', 'login': '', 'password': '',
                                 'launch_mode': 'noprint', 'date_start': '', 'date_end': '', 'timeout_hide': 10000,
                                 'point_size': 11, 'bold': False}
        try:
            with open('config.json', 'r', encoding='utf-8') as f_conf:
                self.configuration = json.load(f_conf)
                print('Считан файл конфигурации ' + f_conf.name)
            if self.configuration.keys() != default_configuration.keys():
                raise FileIsNotCorrectError('Содержимое файла ' + f_conf.name + ' не корректно')
        except (FileNotFoundError, FileIsNotCorrectError) as log:
            print(log)
            self.configuration = default_configuration
            print('Создана новая конфигурация!', self.configuration)
            self.save_configuration()

    def get_configuration(self):
        return self.configuration

    def get_url_server_jira(self):
        return self.configuration['url_server_jira']

    def get_login(self):
        return self.configuration['login']

    def get_password(self):
        return self.configuration['password']

    def get_timeout_hide(self):
        return self.configuration['timeout_hide']

    def get_point_size(self):
        return self.configuration['point_size']

    def get_bold(self):
        return self.configuration['bold']

    def get_launch_mode(self):
        return self.configuration['launch_mode']

    def get_configuration_tuple(self):
        return tuple(self.configuration.values())

    def get_date(self):
        return self.configuration['date_start'], self.configuration['date_end']

    def set_url_server_jira(self, url_server_jira):
        self.configuration['url_server_jira'] = url_server_jira
        self.save_configuration()

    def set_login(self, login):
        self.configuration['login'] = login
        self.save_configuration()

    def set_password(self, password):
        self.configuration['password'] = password
        self.save_configuration()

    def set_launch_mode(self, launch_mode):
        self.configuration['launch_mode'] = launch_mode
        self.save_configuration()

    def set_url_login_password(self, url_server_jira, login, password):
        self.configuration['url_server_jira'] = url_server_jira
        self.configuration['login'] = login
        self.configuration['password'] = password
        self.save_configuration()

    def save_configuration(self):
        try:
            with open('config.json', 'w', encoding='utf-8') as f_conf:
                json.dump(self.configuration, f_conf, indent=4, ensure_ascii=False)
                print('Конфигурация успешно сохранена')
            return True
        except FileNotFoundError:
            print('Ошибка открытия файла ' + f_conf.name + 'для записи')
            return False


class ConnectToJIRA:
    def __init__(self, url_server_jira: str, login_user: str, password_user: str):
        self.isCon = 1
        try:
            jira_options = {'server': url_server_jira}
            self.jira = JIRA(options=jira_options, basic_auth=(login_user, password_user), max_retries=0)
            print('Успешное подключение к серверу!')
        except Exception as jira_error_log:
            jira_error_log = str(jira_error_log)
            if search(r'Unauthorized', jira_error_log) != None:
                self.isCon = 2
                print('Ошибка авторизации!!')
                print(url_server_jira, login_user, password_user)
            elif search(r'Max retries exceeded with', jira_error_log) != None:
                self.isCon = 3
                print('Ошибка подключения')
            print(jira_error_log)


    def getConnectToJira(self):
        return self.jira

    def isConnect(self):
        return self.isCon


class RequestTime:  # Время запроса
    @staticmethod
    def time():
        date_now = datetime.datetime.now().date()
        # Получаем номер месяца в фомате - 07 и номер года в формате - 2022
        month_now = date_now.strftime("%m")
        year_now = str(date_now.year)
        the_beginning_of_the_month = year_now + '-' + month_now + '-01'
        return the_beginning_of_the_month, str(date_now)


class DictPersons:
    def __init__(self, connect_to_jira, date):
        jira = connect_to_jira.getConnectToJira()
        self.issue_error = 'Не оцененные задачи: '
        self.dict_persons = dict()
        with open('person_list.ini', 'r', encoding='utf-8') as f_n:
            person_file = f_n.read().split()
        self.request_date = date
        if date[0] == '' or date[1] == '':
            self.request_date = RequestTime.time()  #Получаем даты для выгрузки
        self.key = str()
        for name in person_file:
            jql_all = 'cf[10110] >= "' + self.request_date[0] + ' 06:00" AND cf[10110] <= "' + self.request_date[1] + ' 22:00" AND assignee in (' + name + ')'
            jql_krt = 'status in (Closed, Протестированный) AND "Дата проверки" >= "' + self.request_date[0] + ' 06:00" AND "Дата проверки" <= "' + self.request_date[1] + ' 22:00" AND "Испытатель/тестировщик" in (' + name + ')'
            issues_list = self.__get_issue_list(jira, jql_all)
            issues_list_krt = self.__get_issue_list(jira, jql_krt)
            self.key = name

            self.dict_persons.update(self.__dictPersons(jira, issues_list, issues_list_krt))
            break
    @staticmethod
    def __get_issue_list(jira, jql):
        start = 0
        leng = 50
        issues_list = None
        while True:
            if issues_list == None:
                issues_list = jira.search_issues(jql, start,
                                                 leng)  # второй параметр говорит место старта, третий сколько задач вычитать
            else:
                issues_list.extend(jira.search_issues(jql, start, leng))
            start += 50
            if start > issues_list.total:
                break
        return issues_list

    def __dictPersons(self, jira, issues_list, issues_list_krt):
        dict_persons = dict()
        if issues_list != None:
            for i in issues_list:
                issue = jira.issue(i)
                if issue.fields.assignee.name not in dict_persons:
                    dict_persons[issue.fields.assignee.name] = [issue.fields.assignee.displayName,
                                                                issue.fields.customfield_10106,
                                                                self.short_name(issue.fields.assignee.displayName),
                                                                [issue]]
                else:
                    dict_persons[issue.fields.assignee.name][1] = round(
                        dict_persons[issue.fields.assignee.name][1] + issue.fields.customfield_10106, 1)
                    dict_persons[issue.fields.assignee.name][3].append(issue)
        if issues_list_krt != None:
            for i in issues_list_krt:
                issue = jira.issue(i)
                if issue.fields.customfield_10408.name not in dict_persons:
                    if issue.fields.customfield_10412 != None:
                        dict_persons[issue.fields.customfield_10408.name] = [issue.fields.customfield_10408.displayName,
                                                                             issue.fields.customfield_10412,
                                                                             self.short_name(
                                                                                 issue.fields.assignee.displayName),
                                                                             [issue]]
                    else:
                        dict_persons[issue.fields.customfield_10408.name] = [issue.fields.customfield_10408.displayName,
                                                                             0.0, self.short_name(
                                issue.fields.assignee.displayName), [issue]]
                        self.issue_error += str(issue) + ' '
                else:
                    try:
                        dict_persons[issue.fields.customfield_10408.name][1] = round(
                            dict_persons[issue.fields.customfield_10408.name][1] + issue.fields.customfield_10412, 1)
                    except TypeError:
                        self.issue_error += str(issue) + ' '
                    dict_persons[issue.fields.customfield_10408.name][3].append(issue)
        return dict_persons

    def getDictPersons(self):
        return self.dict_persons

    def get_issue_error(self):
        return self.issue_error

    def get_request_time(self):
        return self.request_date

    def get_estimate(self):
        return self.dict_persons[self.key][1]

    @staticmethod
    def short_name(name):
        regex_name = search(r'^\S+\s\S+', name).group()
        return regex_name


class OutputToStr:
    @staticmethod
    def text(dict_Persons):
        # Определяем самое длинное имя
        max_len_name = str()
        for r in dict_Persons.getDictPersons().keys():
            if len(max_len_name) < len(dict_Persons.getDictPersons()[r][2]):
                max_len_name = dict_Persons.getDictPersons()[r][2]

        output = ''
        for key in dict_Persons.getDictPersons().keys():
            output += dict_Persons.getDictPersons()[key][2] + '\n'
        time = dict_Persons.get_request_time()
        if dict_Persons.get_issue_error() == 'Не оцененные задачи: ':
            output = 'c ' + time[0] + ' по ' + time[1] + '\n' + output
        else:
            output = 'c ' + time[0] + ' по ' + time[1] + '\n' + output + dict_Persons.get_issue_error()
        print(output)
        print(dict_Persons.get_issue_error())
        return output


class MainWindow(QMainWindow):
    tray_icon = None

    def __init__(self):
        QMainWindow.__init__(self)
        self.conf = Configuration()  # Считываем файл конфигурации

        # Получить размер разрешения монитора
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()
        self.setMinimumSize(QSize(260, 250))
        self.setMaximumSize(QSize(260, 250))
        self.move(self.width - self.minimumWidth(), self.height - self.minimumHeight() - 50)
        self.setWindowFlags(Qt.ToolTip | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("MainWindow{background-color:rgb(195, 201, 159)}")

        self.timerHide = QTimer()
        self.timerHide.timeout.connect(self.window_hide)

        # Авторизуемся в программе и делаем подключение к базе
        self.__log_in(self.conf.get_url_server_jira(), self.conf.get_login(), self.conf.get_password())

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))

        quit_action = QAction("Закрыть", self)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.show()
        self.tray_icon.activated.connect(self.__one_click)

        self.timer = QTimer()
        self.timer.start(1800000)
        self.timer.timeout.connect(self.output_to_plain_text)

    def output_to_plain_text(self):
        self.result = DictPersons(self.ConnectJira, self.conf.get_date())
        self.plane2.setPlainText(OutputToStr.text(self.result))
        self.lable_estimate.setText(str(self.result.get_estimate()))

    def authorized(self):
        central_widget = QWidget(self)
        # self.setCentralWidget(central_widget)

        grid_layout = QGridLayout(self)
        central_widget.setLayout(grid_layout)

        self.lable_estimate = QLabel()
        self.lable_estimate.setMinimumSize(150, 90)
        self.lable_estimate.setAlignment(Qt.AlignCenter)
        self.lable_estimate.setFrameStyle(QFrame.Box)
        font3 = QFont()
        font3.setPointSize(60)
        font3.setBold(True)
        self.lable_estimate.setFont(font3)
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(0, 0)
        effect.setBlurRadius(10)
        effect.setColor(QColor(0, 0, 0))
        self.lable_estimate.setGraphicsEffect(effect)
        self.lable_estimate.setStyleSheet('color:rgb(85, 85, 85); background-color:rgb(225, 214, 170);')
        grid_layout.addWidget(self.lable_estimate, 0, 0)

        self.plane2 = QPlainTextEdit(self)
        self.plane2.setGeometry(5, 5, 250, 50)
        self.plane2.setReadOnly(True)
        font = QFont()
        font.setPointSize(self.conf.get_point_size())
        font.setBold(self.conf.get_bold())
        self.plane2.setFont(font)
        grid_layout.addWidget(self.plane2, 1, 0)

        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 2, 0)

        horizontalLayout2 = QHBoxLayout()
        btn_hide = QPushButton("Скрыть")
        font4 = QFont()
        font4.setBold(True)
        btn_hide.setFont(font4)
        btn_hide.clicked.connect(self.window_hide)
        btn_update = QPushButton("Обновить")
        btn_update.clicked.connect(self.output_to_plain_text)
        horizontalLayout2.addWidget(btn_hide)
        horizontalLayout2.addWidget(btn_update)
        grid_layout.addLayout(horizontalLayout2, 3, 0)

        horizontalLayout = QHBoxLayout()
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(qApp.quit)
        btn_log_out = QPushButton("Разлогиниться")
        btn_log_out.clicked.connect(self.__log_out)
        horizontalLayout.addWidget(btn_log_out)
        horizontalLayout.addWidget(btn_close)
        grid_layout.addLayout(horizontalLayout, 4, 0)

        self.timerHide.start(self.conf.get_timeout_hide())
        self.output_to_plain_text()  # Подсчитываем баллы и выводим на отображение

        return central_widget

    def not_authorized(self):
        central_widget = QWidget(self)
        # self.setCentralWidget(central_widget)
        grid_layout = QGridLayout(self)
        central_widget.setLayout(grid_layout)

        lable_url = QLabel("Адрес сервера:")
        grid_layout.addWidget(lable_url, 0, 0)
        self.line_edit_url = QLineEdit()
        self.line_edit_url.setText(self.conf.get_url_server_jira())
        grid_layout.addWidget(self.line_edit_url, 1, 0)

        lable_login = QLabel("Логин:")
        grid_layout.addWidget(lable_login, 2, 0)
        self.line_edit_login = QLineEdit()
        grid_layout.addWidget(self.line_edit_login, 3, 0)

        lable_password = QLabel("Пароль:")
        grid_layout.addWidget(lable_password, 4, 0)
        self.line_edit_password = QLineEdit()
        grid_layout.addWidget(self.line_edit_password, 5, 0)

        self.btn_auth = QPushButton("Авторизоваться")
        self.btn_auth.clicked.connect(lambda: self.__log_in(self.line_edit_url.text(), self.line_edit_login.text(), self.line_edit_password.text()))
        grid_layout.addWidget(self.btn_auth, 6, 0)

        self.btn_close = QPushButton("Закрыть программу")
        self.btn_close.clicked.connect(qApp.quit)
        grid_layout.addWidget(self.btn_close, 7, 0)

        self.lable_log_auth = QLabel('')
        grid_layout.addWidget(self.lable_log_auth, 8, 0)

        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 9, 0)

        return central_widget

    def __log_in(self, url='', login='', password=''):
        if self.conf.get_url_server_jira() != '' and self.conf.get_login() != '':
            self.ConnectJira = ConnectToJIRA(self.conf.get_url_server_jira(), self.conf.get_login(), self.conf.get_password())
            if self.ConnectJira.isConnect() == 1:
                central_widget = self.authorized()
                # self.conf.set_url_login_password(url, login, password)
                self.timerHide.start(self.conf.get_timeout_hide())
            elif self.ConnectJira.isConnect() == 3:
                central_widget = self.not_authorized()
                self.lable_log_auth.setText('Ошибка подключения к серверу!')
            elif self.ConnectJira.isConnect() == 2:
                central_widget = self.not_authorized()
                self.lable_log_auth.setText('Ошибка авторизации!')
            else:
                central_widget = self.not_authorized()
                self.lable_log_auth.setText('Неизвестная ошибка!')
            self.setCentralWidget(central_widget)
            return self.ConnectJira.isConnect()
        elif login != '' and password != '':
            self.ConnectJira = ConnectToJIRA(url, login, password)
            if self.ConnectJira.isConnect() == 1:
                central_widget = self.authorized()
                self.conf.set_url_login_password(url, login, password)
                self.timerHide.start(self.conf.get_timeout_hide())
            elif self.ConnectJira.isConnect() == 3:
                central_widget = self.not_authorized()
                self.lable_log_auth.setText('Ошибка подключения к серверу!')
            elif self.ConnectJira.isConnect() == 2:
                central_widget = self.not_authorized()
                self.lable_log_auth.setText('Ошибка авторизации!')
            else:
                central_widget = self.not_authorized()
                self.lable_log_auth.setText('Неизвестная ошибка!')
            self.setCentralWidget(central_widget)
            return self.ConnectJira.isConnect()
        else:
            central_widget = self.not_authorized()
            self.setCentralWidget(central_widget)

    def __log_out(self):
        central_widget = self.not_authorized()
        self.setCentralWidget(central_widget)
        print('Пользователь разлогинился')
        print('Удаление логина из конфигурации')
        self.conf.set_login('')
        print('Удаление пароля из конфигурации')
        self.conf.set_password('')
        self.timerHide.stop()

    def window_show(self):
        self.show()

    def window_show_hide(self):
        self.show()
        self.timerHide.start(self.conf.get_timeout_hide())

    def window_hide(self):
        self.hide()

    def __one_click(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.window_show_hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.window_show()

    sys.exit(app.exec_())
