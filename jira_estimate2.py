import xlwt  # Работа с EXCEL
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QSystemTrayIcon, QSpacerItem, \
    QSizePolicy, QMenu, QStyle, qApp, QAction, QPushButton, QPlainTextEdit, QLabel, QLineEdit, QHBoxLayout, QFrame, \
    QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer, QSize, Qt
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QPixmap, QIcon, QCloseEvent
from jira import JIRA
from re import search
import sys
from github.jira_estimate_lib.settings_window import SettingsWindow
from github.jira_estimate_lib.from_jira_result import FromJiraResult
from jira_estimate_lib.cases import Cases
from jira_estimate_lib.configuration import *


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


class OutputToStr:  # Пока не используется
    @staticmethod
    def text(dict_Persons):
        # Определяем самое длинное имя
        max_len_name = str()
        for r in dict_Persons.get_from_jira_result().keys():
            if len(max_len_name) < len(dict_Persons.get_from_jira_result()[r][2]):
                max_len_name = dict_Persons.get_from_jira_result()[r][2]

        output = ''
        for key in dict_Persons.get_from_jira_result().keys():
            output += dict_Persons.get_from_jira_result()[key][2] + '\n'
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
        for key1 in dict_Persons.get_from_jira_result().keys():
            if len(max_len_name) < len(dict_Persons.get_from_jira_result()[key1][2]):
                max_len_name = dict_Persons.get_from_jira_result()[key1][2]

        vivod = ''


        for key in dict_Persons.get_from_jira_result().keys():
            issue = str()
            for x in dict_Persons.get_from_jira_result()[key][3]:
                issue += str(x) + ' '
            vivod += dict_Persons.get_from_jira_result()[key][2] + '_' * (len(max_len_name) + 1 - len(dict_Persons.get_from_jira_result()[key][2])) + str(dict_Persons.get_from_jira_result()[key][1]) + '\n' + f'{issue}' + '\n'
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

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        quit_action = QAction("Закрыть", self)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # self.build_rect()
        # Авторизуемся в программе и делаем подключение к базе
        self.__log_in(self.conf.get_url_server_jira(), self.conf.get_login(), self.conf.get_password())


    def build_rect(self):
        self.setMinimumSize(QSize(260, 250))
        self.setMaximumSize(QSize(260, 250))
        self.move(self.width - self.minimumWidth(), self.height - self.minimumHeight() - 50)
        self.setWindowFlags(Qt.ToolTip | Qt.WindowStaysOnTopHint)  # Поверху всех окон
        self.setStyleSheet("MainWindow{background-color:rgb(195, 201, 159)}")

        self.timerHide = QTimer()
        self.timerHide.timeout.connect(self.window_hide)

        self.timerPrint = QTimer()
        self.timerPrint.timeout.connect(self.output_to_file)

        self.timer = QTimer()
        self.timer.timeout.connect(self.output_to_plain_text)



    def output_to_plain_text(self):
        try:
            result = FromJiraResult(self.ConnectJira, self.conf)  # Делаем выборку по сотрудникам в jira
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

    def output_to_plain_text_circle(self):
        try:
            result = FromJiraResult(self.ConnectJira, self.conf)  # Делаем выборку по сотрудникам в jira
            date = result.get_request_time()  # Получаем дату выборки отчета
            ierror = ''
            if result.issue_error != 'Проблемы с оценкой!:\n':
                ierror = result.issue_error
                self.lable_att.setToolTip(ierror)
                self.lable_att.show()
            for person in result.get_all_estimate().keys():
                print('с ' + date[0] + ' по ' + date[1] + '\n' + person + ' - ', result.get_all_estimate()[person])
                self.lable_date.setText('с ' + date[0] + ' по ' + date[1])
                self.lable_est.setText(str(result.get_all_estimate()[person]))
                name_s = search(r'^\S+', person).group()
                self.lable_name.setText(name_s)

            print(result.issue_error)  # Выводим в консоль задачи с неккоректной оценкой
        except KeyError:
            self.lable_att.setToolTip('Закрытых задач не обнаружено')
            self.lable_att.show()

    def output_to_file(self):
        result = FromJiraResult(self.ConnectJira, self.conf)  # Делаем выборку в jira по задачам

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

        # Делаем выборку в jira по кейсам и сохраняем в файл
        cases_estimate = result.get_cases_estimate(result.get_from_cases_rezult())  # Делаем выборку в jira по кейсам
        period_report = 'ОТЧЕТ-Кейсы с ' + date[0] + ' по ' + date[1] + '\n'
        for name_by_cases in cases_estimate.keys():
            period_report += name_by_cases + ' - ' + str(cases_estimate[name_by_cases]) + '\n'
        period_report += '\n' + result.cases_error
        with open('_ОТЧЕТ-Кейсы_' + date[0] + '-' + date[1] + '.txt', 'w', encoding='utf-8') as f_c:
            f_c.write(period_report)

        sys.exit()  # Завершаем работу программы

    def authorized_app(self):
        self.build_rect()
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
        self.timer.start(1800000)
        self.tray_icon.activated.connect(self.__one_click)  # При нажатии ЛКМ по значку в трее, окно развернется
        self.output_to_plain_text()  # Подсчитываем баллы и выводим на отображение

        return central_widget

    def build_circle_app(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.setWindowTitle("Окно программы")
        self.resize(230, 230)
        # self.move(1680, 40)
        self.move(self.width - 240, self.height - 1040)
        pixmap = QPixmap("/gfx/fon.png")
        pal = self.palette()
        pal.setBrush(QPalette.Normal, QPalette.Window, QBrush(pixmap))
        pal.setBrush(QPalette.Inactive, QPalette.Window, QBrush(pixmap))
        self.setPalette(pal)
        self.setMask(pixmap.mask())

        self.button1 = QPushButton(self)
        self.button1.setFixedSize(38, 30)
        self.button1.move(54, 162)
        self.button1.clicked.connect(self.output_to_plain_text_circle)
        self.button1.setIcon(QIcon('/gfx/refresh.png'))
        self.button1.setIconSize(QSize(24, 24))
        self.button1.setStyleSheet(
            'background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(153, 153, 153, 255), stop:1 rgba(255, 255, 255, 255)); border-radius: 15px;')
        self.button1.setToolTip('Обновить данные из JIRA')

        self.button2 = QPushButton(self)
        self.button2.setFixedSize(38, 30)
        self.button2.move(96, 162)
        self.button2.clicked.connect(self.show_window_settings)
        self.button2.setIcon(QIcon('/gfx/while.png'))
        self.button2.setIconSize(QSize(24, 24))
        self.button2.setStyleSheet(
            'background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(153, 153, 153, 255), stop:1 rgba(255, 255, 255, 255)); border-radius: 15px;')
        self.button2.setToolTip('Настройки')

        self.button3 = QPushButton(self)
        self.button3.setFixedSize(38, 30)
        self.button3.move(138, 162)
        self.button3.clicked.connect(qApp.quit)
        self.button3.setIcon(QIcon('/gfx/Red-Close-Button.png'))
        self.button3.setIconSize(QSize(24, 24))
        self.button3.setStyleSheet(
            'background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(153, 153, 153, 255), stop:1 rgba(255, 255, 255, 255)); border-radius: 15px;')
        self.button3.setToolTip('Закрыть программу')

        self.lable_est = QLabel('0.0', self)
        self.lable_est.setFixedSize(186, 90)
        self.lable_est.setAlignment(Qt.AlignCenter)
        font3 = QFont()
        font3.setPointSize(40)
        font3.setBold(True)
        self.lable_est.setFont(font3)
        self.lable_est.setStyleSheet('color:rgb(85, 85, 85); background-color:rgb(225, 214, 170); border-radius: 15px')
        self.lable_est.move(22, 70)

        self.lable_att = QLabel(self)
        self.lable_att.setFixedSize(27, 24)
        pixmap1 = QPixmap("/gfx/attention.png")
        self.lable_att.setPixmap(pixmap1)
        self.lable_att.move(102, 195)
        # self.lable_att.setToolTip('Обнаружены следующие ошибки:\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd')
        self.lable_att.hide()

        self.lable_date = QLabel('Период отчета', self)
        self.lable_date.setFixedSize(170, 24)
        font4 = QFont()
        font4.setPointSize(8)
        font4.setBold(False)
        self.lable_date.setFont(font4)
        self.lable_date.setAlignment(Qt.AlignCenter)
        self.lable_date.move(30, 48)

        self.lable_name = QLabel('Фамилия', self)
        self.lable_name.setFixedSize(170, 24)
        font5 = QFont()
        font5.setPointSize(14)
        font5.setBold(True)
        self.lable_name.setFont(font5)
        self.lable_name.setAlignment(Qt.AlignCenter)
        self.lable_name.setStyleSheet('color:rgb(85, 85, 85);')
        self.lable_name.move(30, 25)


        self.output_to_plain_text_circle()
        self.show()

    def show_window_settings(self):
        print('show окна настроек')
        self.two_window = SettingsWindow(self)
        self.two_window.show()

    def not_authorized_app(self):
        self.build_rect()
        central_widget = QWidget(self)
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
        # lable_password.setToolTip('Окно для ввода пароля JIRA')
        # lable_password.setToolTipDuration(4000)
        grid_layout.addWidget(lable_password, 4, 0)
        self.line_edit_password = QLineEdit()
        # self.line_edit_password.setToolTip('Введите пароль')
        # self.line_edit_password.setToolTipDuration(4000)
        self.line_edit_password.setEchoMode(QLineEdit.Password)
        self.line_edit_password.returnPressed.connect(lambda: self.__log_in(self.line_edit_url.text(), self.line_edit_login.text(), self.line_edit_password.text()))
        grid_layout.addWidget(self.line_edit_password, 5, 0)

        self.btn_auth = QPushButton("Авторизоваться")
        self.btn_auth.clicked.connect(lambda: self.__log_in(self.line_edit_url.text(), self.line_edit_login.text(), self.line_edit_password.text()))
        self.btn_auth.setToolTip("Произвести авторизацию")  # Всплывающая подсказка
        self.btn_auth.setToolTipDuration(4000)  # Время вывода подсказки
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
                    if self.conf.get_interface() == 'circle':
                        self.build_circle_app()
                    else:
                        central_widget = self.authorized_app()
                        self.timerHide.start(self.conf.get_timeout_hide())
                else:
                    central_widget = self.print_mod_app()
                # self.conf.set_url_login_password(url, login, password)

            elif self.ConnectJira.isConnect() == 3:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Ошибка подключения к серверу!')
            elif self.ConnectJira.isConnect() == 2:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Ошибка авторизации!')
            else:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Неизвестная ошибка!')
            if self.conf.get_interface() != 'circle':
                self.setCentralWidget(central_widget)
                print('setCentralWidget1')
            return self.ConnectJira.isConnect()
        #Если пользователь ранее не авторизовывался, то проверяем что поля для авторизации не пустые
        elif login != '' and password != '':
            self.ConnectJira = ConnectToJIRA(url, login, password)  # Пробуем подключиться к jira
            if self.ConnectJira.isConnect() == 1:  # Проверяем на успешность подключения
                if self.conf.get_launch_mode() != 'print':  # Выбираем отрисовку окна в зависимости от режима запуска
                    if self.conf.get_interface() == 'circle':
                        self.conf.set_url_login_password(url, login, password)  #Важно записать значения до того как перестроиться форма авторизации
                        self.build_circle_app()
                    else:
                        central_widget = self.authorized_app()
                        self.conf.set_url_login_password(url, login, password)
                        self.timerHide.start(self.conf.get_timeout_hide())
                else:
                    central_widget = self.print_mod_app()

            elif self.ConnectJira.isConnect() == 3:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Ошибка подключения к серверу!')
            elif self.ConnectJira.isConnect() == 2:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Ошибка авторизации!')
            else:
                central_widget = self.not_authorized_app()
                self.lable_log_auth.setText('Неизвестная ошибка!')
            if self.conf.get_interface() != 'circle':
                self.setCentralWidget(central_widget)
                print('setCentralWidget2')
            return self.ConnectJira.isConnect()
        else:
            central_widget = self.not_authorized_app()
            self.setCentralWidget(central_widget)
            print('setCentralWidget3')

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
