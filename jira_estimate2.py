import xlrd, xlwt  # Работа с EXCEL
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSystemTrayIcon, QSpacerItem, \
    QSizePolicy, QMenu, QStyle, qApp, QAction, QPushButton, QPlainTextEdit, QLabel, QLineEdit, QHBoxLayout, QFrame, \
    QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer, QSize, Qt
from PyQt5.QtGui import QFont, QColor
from jira import JIRA
from re import search
import sys
from jira_estimate_lib.lib import *


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


class DictPersons:
    def __init__(self, connect_to_jira, conf):
        self.config = conf
        self.dict_persons = dict()
        jira = connect_to_jira.getConnectToJira()
        self.issue_error = 'Проблемы с оценкой!:\n'
        self.dict_persons = dict()
        with open('person_list.ini', 'r', encoding='utf-8') as f_n:
            person_file = f_n.read().split()
        self.request_date = conf.get_date()
        if conf.get_date()[0] == '' or conf.get_date()[1] == '':
            self.request_date = request_time()  #Получаем даты текущего месяца для выгрузки
        self.key = str()
        for name in person_file:
            jql_all = 'cf[10110] >= "' + self.request_date[0] + ' 06:00" AND cf[10110] <= "' + self.request_date[1] + ' 22:00" AND assignee in (' + name + ')'
            jql_tester = 'status in (Closed, Протестированный) AND "Дата проверки" >= "' + self.request_date[0] + ' 06:00" AND "Дата проверки" <= "' + self.request_date[1] + ' 22:00" AND "Испытатель/тестировщик" in (' + name + ')'
            issues_list = self.__get_issue_list(jira, jql_all)
            issues_list_tester = self.__get_issue_list(jira, jql_tester)
            self.key = name

            self.dict_persons.update(self.__dictPersons(jira, issues_list, issues_list_tester))

            if conf.get_launch_mode() != 'print':
                break

    @staticmethod
    def __get_issue_list(jira, jql):
        start = 0
        leng = 50
        issues_list = None
        while True:
            if issues_list == None:
                issues_list = jira.search_issues(jql, start, leng)  #2 параметр говорит место старта, 3 сколько задач вычитать
            else:
                issues_list.extend(jira.search_issues(jql, start, leng))
            start += 50
            if start > issues_list.total:
                break
        return issues_list

    def __dictPersons(self, jira, issues_list, issues_list_tester):
        if issues_list != None:
            for i in issues_list:
                issue = jira.issue(i)
                if issue.fields.project.key == 'TS':
                    if issue.fields.assignee.name not in self.dict_persons:
                        if issue.fields.customfield_10106 != None:
                            self.dict_persons[issue.fields.assignee.name] = {'name': self.short_name(issue.fields.assignee.displayName), 'issue': {str(issue): {'estimate': issue.fields.customfield_10106, 'dev_name': issue.fields.customfield_10108[0].fields.summary, 'date_close': search(r"\d{4}-\d{2}-\d{2}", issue.fields.resolutiondate).group()}}}
                        else:
                            self.dict_persons[issue.fields.assignee.name] = {'name': self.short_name(issue.fields.assignee.displayName), 'issue': {str(issue): {'estimate': 0.0, 'dev_name': issue.fields.customfield_10108[0].fields.summary, 'date_close': search(r"\d{4}-\d{2}-\d{2}", issue.fields.resolutiondate).group()}}}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
                    else:
                        if issue.fields.customfield_10106 != None:
                            self.dict_persons[issue.fields.assignee.name]['issue'][str(issue)] = {'estimate': issue.fields.customfield_10106, 'dev_name': issue.fields.customfield_10108[0].fields.summary, 'date_close': search(r"\d{4}-\d{2}-\d{2}", issue.fields.resolutiondate).group()}
                        else:
                            self.dict_persons[issue.fields.assignee.name]['issue'][str(issue)] = {'estimate': 0.0, 'dev_name': issue.fields.customfield_10108[0].fields.summary, 'date_close': search(r"\d{4}-\d{2}-\d{2}", issue.fields.resolutiondate).group()}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
                else:
                    if issue.fields.assignee.name not in self.dict_persons:
                        if issue.fields.customfield_10106 != None:
                            self.dict_persons[issue.fields.assignee.name] = {'name': self.short_name(issue.fields.assignee.displayName), 'issue': {str(issue): {'estimate': issue.fields.customfield_10106, 'dev_name': issue.fields.project.key}}}
                        else:
                            self.dict_persons[issue.fields.assignee.name] = {'name': self.short_name(issue.fields.assignee.displayName), 'issue': {str(issue): {'estimate': 0.0, 'dev_name': issue.fields.project.key}}}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
                    else:
                        if issue.fields.customfield_10106 != None:
                            self.dict_persons[issue.fields.assignee.name]['issue'][str(issue)] = {'estimate': issue.fields.customfield_10106, 'dev_name': issue.fields.project.key}
                        else:
                            self.dict_persons[issue.fields.assignee.name]['issue'][str(issue)] = {'estimate': 0.0, 'dev_name': issue.fields.project.key}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
        if issues_list_tester != None:
            for i in issues_list_tester:
                issue = jira.issue(i)
                if issue.fields.customfield_10408.name not in self.dict_persons:
                    try:
                        if issue.fields.customfield_10412 != None:
                            self.dict_persons[issue.fields.customfield_10408.name] = {'name': self.short_name(issue.fields.customfield_10408.displayName), 'issue': {str(issue): {'estimate': issue.fields.customfield_10412, 'dev_name': issue.fields.project.key}}}
                        else:
                            self.dict_persons[issue.fields.customfield_10408.name] = {'name': self.short_name(issue.fields.customfield_10408.displayName), 'issue': {str(issue): {'estimate': 0.0, 'dev_name': issue.fields.project.key}}}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
                    except AttributeError:
                        self.dict_persons[issue.fields.customfield_10408.name] = {'name': self.short_name(issue.fields.customfield_10408.displayName), 'issue': {str(issue): {'estimate': 0.0, 'dev_name': issue.fields.project.key}}}
                        self.issue_error += str(issue) + ' - поля с оценкой не существует\n'
                else:
                    try:
                        if issue.fields.customfield_10412 != None:
                            self.dict_persons[issue.fields.customfield_10408.name]['issue'][str(issue)] = {'estimate': issue.fields.customfield_10412, 'dev_name': issue.fields.project.key}
                        else:
                            self.dict_persons[issue.fields.customfield_10408.name]['issue'][str(issue)] = { 'estimate': 0.0, 'dev_name': issue.fields.project.key}
                            self.issue_error += str(issue) + ' - задача не оценена\n'
                    except AttributeError:
                        self.dict_persons[issue.fields.customfield_10408.name]['issue'][str(issue)] = {'estimate': 0.0, 'dev_name': issue.fields.project.key}
                        self.issue_error += str(issue) + ' - поля с оценкой не существует\n'
        return self.dict_persons

    def getDictPersons(self):
        return self.dict_persons

    def get_issue_error(self):
        return self.issue_error

    def get_request_time(self):
        return self.request_date

    def get_all_estimate(self):
        person_dict = dict()
        if self.dict_persons != {}:
            for person in self.dict_persons.keys():
                estimate_result = 0.0
                for issue in self.dict_persons[person]['issue']:
                    estimate_result = round(estimate_result + self.dict_persons[person]['issue'][issue]['estimate'], 1)
                person_dict[self.dict_persons[person]['name']] = estimate_result
        else:
            person_dict['Закрытых задач нет'] = 0.0
        return person_dict

    def get_estimate_to_project(self):
        person_dict = dict()
        for person in self.dict_persons.keys():
            sett = set()
            for issue in self.dict_persons[person]['issue']:
                sett.add(self.dict_persons[person]['issue'][issue]['dev_name'])
            dev = dict()
            for ittr in sett:
                dev[ittr] = 0.0
            for iss in self.dict_persons[person]['issue']:
                dev[self.dict_persons[person]['issue'][iss]['dev_name']] = round(dev[self.dict_persons[person]['issue'][iss]['dev_name']] + self.dict_persons[person]['issue'][iss]['estimate'], 1)
            person_dict[self.dict_persons[person]['name']] = dev
        return person_dict

    @staticmethod
    def short_name(name):
        regex_name = search(r'^\S+\s\S+', name).group()
        return regex_name


class OutputToStr:  # Пока не используется
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

    @staticmethod
    def text_for_file(dict_Persons):
        # Определяем самое длинное имя
        max_len_name = str()
        for key1 in dict_Persons.getDictPersons().keys():
            if len(max_len_name) < len(dict_Persons.getDictPersons()[key1][2]):
                max_len_name = dict_Persons.getDictPersons()[key1][2]

        vivod = ''


        for key in dict_Persons.getDictPersons().keys():
            issue = str()
            for x in dict_Persons.getDictPersons()[key][3]:
                issue += str(x) + ' '
            vivod += dict_Persons.getDictPersons()[key][2] + '_' * (len(max_len_name) + 1 - len(dict_Persons.getDictPersons()[key][2])) + str(dict_Persons.getDictPersons()[key][1]) + '\n' + f'{issue}' + '\n'
        vivod = vivod + dict_Persons.get_issue_error()
        print(vivod)
        # Сохранение в файл
        # with open('_ОТЧЕТ_' + date_file[0] + '-' + date_file[1] + '.txt', 'w', encoding='utf-8') as f_n:
        #     f_n.write(vivod)


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

        self.timerPrint = QTimer()
        self.timerPrint.timeout.connect(self.output_to_file)

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
        try:
            result = DictPersons(self.ConnectJira, self.conf)  # Делаем выборку по сотрудникам в jira
            date = result.get_request_time()  # Получаем дату выборки отчета
            ierror = ''
            if result.issue_error != 'Проблемы с оценкой!:\n':
                ierror = result.issue_error
            for person in result.get_all_estimate().keys():
                print('с ' + date[0] + ' по ' + date[1] + '\n' + person + ' - ', result.get_all_estimate()[person])
                self.plane2.setPlainText('с ' + date[0] + ' по ' + date[1] + '\n' + person + '\n' + ierror)
                self.lable_estimate.setText(str(result.get_all_estimate()[person]))
            print(result.issue_error)  # Выводим в консоль задачи с неккоректной оценкой
        except KeyError:
            self.plane2.setPlainText('Закрытых задач не обнаружено')

    def output_to_file(self):
        result = DictPersons(self.ConnectJira, self.conf)  # Делаем выборку по сотрудникам в jira
        date = result.get_request_time()  # Получаем дату выборки отчета
        # Обрабатываем результат выборки и сохраняем в .txt файл
        stroka = 'ОТЧЕТ с ' + date[0] + ' по ' + date[1] + '\n'
        print(stroka)
        for person in result.get_all_estimate().keys():
            print(person + ' - ', result.get_all_estimate()[person])
            stroka += '\n' + person + ' - ' + str(result.get_all_estimate()[person]) + '\n'
            for g in result.get_estimate_to_project()[person].keys():
                print('    ' + g + ' - ', result.get_estimate_to_project()[person][g])
                stroka +='    ' + g + ' - ' + str(result.get_estimate_to_project()[person][g]) + '\n'
        with open('_ОТЧЕТ_' + date[0] + '-' + date[1] + '.txt', 'w', encoding='utf-8') as f_n:
            f_n.write(stroka + '\n' + result.issue_error)
        # Подготовка двумерного массива с данными для таблицы
        xls_list = list()
        xls_list.append(['с ' + str(date[0]) + ' по ' + str(date[1]), '', 'Всего'])
        for person in result.get_all_estimate().keys():
            xls_list.append([])
            xls_list.append([person, '', result.get_all_estimate()[person]])
            for g in result.get_estimate_to_project()[person].keys():
                xls_list.append(['    ' + g, result.get_estimate_to_project()[person][g]])

        # Выводим данные в файл .xls
        wb = xlwt.Workbook()  # Создаем новую книгу
        ws = wb.add_sheet('Отчет')  # Создаем страницу в книге
        for ind_w, val_w in enumerate(xls_list):
            for ind_r, val_r in enumerate(val_w):
                ws.write(ind_w, ind_r, val_r)  # Записываем значения в ячейки таблицы

        for st in range(len(result.issue_error.split('\n'))):
            ws.write(st, 5, result.issue_error.split('\n')[st])  # Записываем значения в ячейки таблицы

        wb.save('_ОТЧЕТ_' + date[0] + '-' + date[1] + '.xls')  # Сохраняем книгу c заданным именем
        print(result.issue_error)  # Выводим в консоль задачи с неккоректной оценкой
        sys.exit()  # Завершаем работу программы

    def authorized_app(self):
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

    def not_authorized_app(self):
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
        self.line_edit_login.returnPressed.connect(lambda: self.__log_in(self.line_edit_url.text(), self.line_edit_login.text(), self.line_edit_password.text()))
        grid_layout.addWidget(self.line_edit_login, 3, 0)

        lable_password = QLabel("Пароль:")
        grid_layout.addWidget(lable_password, 4, 0)
        self.line_edit_password = QLineEdit()
        self.line_edit_password.setEchoMode(QLineEdit.Password)
        self.line_edit_password.returnPressed.connect(lambda: self.__log_in(self.line_edit_url.text(), self.line_edit_login.text(), self.line_edit_password.text()))
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

    def print_mod_app(self):
        central_widget = QWidget(self)
        grid_layout = QGridLayout(self)
        central_widget.setLayout(grid_layout)

        font4 = QFont()
        font4.setPointSize(14)
        self.lable_log_auth = QLabel('Режим вывода в файл.\nОжидайте')
        self.lable_log_auth.setFont(font4)
        grid_layout.addWidget(self.lable_log_auth, 1, 0)

        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 2, 0)

        self.timerPrint.start(500)

        return central_widget

    def __log_in(self, url='', login='', password=''):
        #Проверяем что пользователь уже авторизован
        if self.conf.get_url_server_jira() != '' and self.conf.get_login() != '':
            self.ConnectJira = ConnectToJIRA(self.conf.get_url_server_jira(), self.conf.get_login(), self.conf.get_password())
            if self.ConnectJira.isConnect() == 1:
                if self.conf.get_launch_mode() != 'print':
                    central_widget = self.authorized_app()
                else:
                    central_widget = self.print_mod_app()
                # self.conf.set_url_login_password(url, login, password)
                self.timerHide.start(self.conf.get_timeout_hide())
            elif self.ConnectJira.isConnect() == 3:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Ошибка подключения к серверу!')
            elif self.ConnectJira.isConnect() == 2:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Ошибка авторизации!')
            else:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Неизвестная ошибка!')
            self.setCentralWidget(central_widget)
            return self.ConnectJira.isConnect()
        #Если пользователь ранее не авторизовывался, то проверяем что поля для авторизации не пустые
        elif login != '' and password != '':
            self.ConnectJira = ConnectToJIRA(url, login, password)  # Пробуем подключиться к jira
            if self.ConnectJira.isConnect() == 1:  # Проверяем на успешность подключения
                if self.conf.get_launch_mode() != 'print':  # Выбираем отрисовку окна в зависимости от режима запуска
                    central_widget = self.authorized_app()
                else:
                    central_widget = self.print_mod_app()
                self.conf.set_url_login_password(url, login, password)
                self.timerHide.start(self.conf.get_timeout_hide())
            elif self.ConnectJira.isConnect() == 3:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Ошибка подключения к серверу!')
            elif self.ConnectJira.isConnect() == 2:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Ошибка авторизации!')
            else:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Неизвестная ошибка!')
            self.setCentralWidget(central_widget)
            return self.ConnectJira.isConnect()
        else:
            central_widget = self.not_authorized_app()
            self.setCentralWidget(central_widget)

    def __log_out(self):
        central_widget = self.not_authorized_app()
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