from re import search
from typing import Tuple
import xlwt
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QIcon, QFont, QColor, QMouseEvent
from PyQt5.QtWidgets import QWidget, QPushButton, qApp, QLabel, QLineEdit, QDialog, QFormLayout, \
    QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QGraphicsDropShadowEffect, QPlainTextEdit, QSpacerItem, QSizePolicy
from github.jira_estimate_lib.from_jira_result import FromJiraResult
from github.jira_estimate_lib.utils import Utils


class CircleApp(QWidget):
    def __init__(self, main_win=None):
        super(CircleApp, self).__init__(main_win, Qt.Window)
        self.conf = main_win.conf
        self.ConnectJira = main_win.connect_jira
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.resize(230, 230)
        self.screen_width, self.screen_height = Utils.screenSize()  # Получили ширину и высоту рабочего стола
        self.move(self.screen_width - 240, self.screen_height - 1040)

        self.timer_refresh = QTimer()
        self.timer_refresh.timeout.connect(self.output_in_circle)

        self.buildCircleApp()

    def buildCircleApp(self):
        pixmap = QPixmap("gfx/fon.png")
        pal = self.palette()
        pal.setBrush(QPalette.Normal, QPalette.Window, QBrush(pixmap))
        pal.setBrush(QPalette.Inactive, QPalette.Window, QBrush(pixmap))
        self.setPalette(pal)
        self.setMask(pixmap.mask())

        # self.label_move = QLabel('...', self)
        self.label_move = MyLabel('...', self)
        self.label_move.setAlignment(Qt.AlignCenter)
        self.label_move.setFixedSize(30, 15)
        self.label_move.move(100, 0)

        self.label_name = QLabel('Фамилия', self)
        self.label_name.setFixedSize(170, 24)
        font5 = QFont()
        font5.setPointSize(14)
        font5.setBold(True)
        self.label_name.setFont(font5)
        self.label_name.setAlignment(Qt.AlignCenter)
        self.label_name.setStyleSheet('color:rgb(85, 85, 85);')
        self.label_name.move(30, 25)

        self.label_date = QLabel('Период отчета', self)
        self.label_date.setFixedSize(170, 24)
        font4 = QFont()
        font4.setPointSize(8)
        font4.setBold(False)
        self.label_date.setFont(font4)
        self.label_date.setAlignment(Qt.AlignCenter)
        self.label_date.move(30, 48)

        self.label_est = QLabel('0.0', self)
        self.label_est.setFixedSize(186, 90)
        self.label_est.setAlignment(Qt.AlignCenter)
        font3 = QFont()
        font3.setPointSize(40)
        font3.setBold(True)
        self.label_est.setFont(font3)
        self.label_est.setStyleSheet('color:rgb(85, 85, 85); background-color:rgb(225, 214, 170); border-radius: 15px')
        self.label_est.move(22, 70)
        # print(self.label_est.pos())
        # print(self.label_est.mapToGlobal(self.label_est.pos()))

        # self.button_refresh = PicButton(QPixmap("gfx_button/button1.png"), QPixmap("gfx_button/button2.png"), QPixmap("gfx_button/button3.png"))
        self.button_refresh = QPushButton(self)
        self.button_refresh.setFixedSize(38, 25)
        self.button_refresh.move(54, 162)
        self.button_refresh.setIcon(QIcon('gfx/refresh.png'))
        self.button_refresh.clicked.connect(self.output_in_circle)
        # self.button_refresh.setIconSize(QSize(24, 24))
        # self.button_refresh.setStyleSheet(
        #     'background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(153, 153, 153, 255), stop:1 rgba(255, 255, 255, 255)); border-radius: 15px;')
        self.button_refresh.setToolTip('Обновить данные из JIRA')

        self.button_logout = QPushButton(self)
        self.button_logout.setFixedSize(38, 25)
        self.button_logout.move(96, 162)
        self.button_logout.setIcon(QIcon('gfx/logout.png'))
        # self.button_settings.setIconSize(QSize(24, 24))
        # self.button_settings.setStyleSheet(
        #     'background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(153, 153, 153, 255), stop:1 rgba(255, 255, 255, 255)); border-radius: 15px;')
        self.button_logout.setToolTip('Разлогиниться')

        self.button_close = QPushButton(self)
        self.button_close.setFixedSize(38, 25)
        self.button_close.move(138, 162)
        self.button_close.clicked.connect(qApp.quit)
        self.button_close.setIcon(QIcon('gfx/Red-Close-Button.png'))
        # self.button_close.setIconSize(QSize(24, 24))
        # self.button_close.setStyleSheet(
        #     'background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 rgba(153, 153, 153, 255), stop:1 rgba(255, 255, 255, 255)); border-radius: 15px;')
        self.button_close.setToolTip('Закрыть программу')

        self.label_att = QLabel(self)
        self.label_att.setFixedSize(27, 24)
        self.label_att.setPixmap(QPixmap("gfx/attention.png"))
        self.label_att.move(102, 195)
        # self.label_att.setToolTip('Обнаружены следующие ошибки:\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd\ndfd')
        self.label_att.hide()

        self.timer_refresh.start(1800000)
        self.output_in_circle()

    def window_show_hide(self):
        pass

    def output_in_circle(self):
        try:
            result = FromJiraResult(self.ConnectJira, self.conf)  # Делаем выборку по сотрудникам в jira
            date = result.get_request_time()  # Получаем дату выборки отчета
            ierror = ''
            if result.issue_error != 'Проблемы с оценкой!:\n':
                ierror = result.issue_error
                self.label_att.setToolTip(ierror)
                self.label_att.show()
            for person in result.get_all_estimate().keys():
                if person != 'Закрытых задач нет':
                    print('с ' + date[0] + ' по ' + date[1] + '\n' + person + ' - ', result.get_all_estimate()[person])
                    self.label_date.setText('с ' + date[0] + ' по ' + date[1])
                    self.label_est.setText(str(result.get_all_estimate()[person]))
                    name_s = search(r'^\S+', person).group()
                    self.label_name.setText(name_s)
                else:
                    self.label_date.setText('с ' + date[0] + ' по ' + date[1])
                    self.label_att.setToolTip('Закрытых задач не обнаружено')
                    self.label_att.show()
            print(result.issue_error)  # Выводим в консоль задачи с неккоректной оценкой
        except KeyError:
            self.label_att.setToolTip('Закрытых задач не обнаружено')
            self.label_att.show()




class RectApp(QWidget):
    def __init__(self, main_win=None):
        super(RectApp, self).__init__(main_win, Qt.Window)
        self.conf = main_win.conf
        self.ConnectJira = main_win.connect_jira

        self.setMinimumSize(QSize(260, 250))
        self.setMaximumSize(QSize(260, 250))
        self.screen_width, self.screen_height = Utils.screenSize()  # Получили ширину и высоту рабочего стола
        self.move(self.screen_width - self.minimumWidth(), self.screen_height - self.minimumHeight() - 50)
        self.setWindowFlags(Qt.ToolTip | Qt.WindowStaysOnTopHint)  # Поверху всех окон
        self.setStyleSheet("RectApp{background-color:rgb(195, 201, 159)}")

        self.timerHide = QTimer()
        self.timerHide.timeout.connect(self.window_hide)
        self.timerHide.start(10000)

        self.timer_refresh = QTimer()
        self.timer_refresh.timeout.connect(self.output_to_plain_text)
        self.__buildRectApp()

    def __buildRectApp(self):
        grid_layout = QGridLayout(self)
        self.setLayout(grid_layout)

        self.label_estimate = QLabel('0.0')
        self.label_estimate.setMinimumSize(150, 90)
        self.label_estimate.setAlignment(Qt.AlignCenter)
        self.label_estimate.setFrameStyle(QFrame.Box)
        font3 = QFont()
        font3.setPointSize(60)
        font3.setBold(True)
        self.label_estimate.setFont(font3)
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(0, 0)
        effect.setBlurRadius(10)
        effect.setColor(QColor(0, 0, 0))
        self.label_estimate.setGraphicsEffect(effect)
        self.label_estimate.setStyleSheet('color:rgb(85, 85, 85); background-color:rgb(225, 214, 170);')
        grid_layout.addWidget(self.label_estimate, 0, 0)

        self.plane2 = QPlainTextEdit('ФИО', self)
        self.plane2.setGeometry(5, 5, 250, 50)
        self.plane2.setReadOnly(True)
        font = QFont()
        font.setPointSize(11)
        font.setBold(False)
        self.plane2.setFont(font)
        grid_layout.addWidget(self.plane2, 1, 0)

        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 2, 0)

        horizontal_layout2 = QHBoxLayout()
        btn_hide = QPushButton("Скрыть")
        font4 = QFont()
        font4.setBold(True)
        btn_hide.setFont(font4)
        btn_hide.clicked.connect(self.window_hide)
        btn_update = QPushButton("Обновить")
        btn_update.clicked.connect(self.output_to_plain_text)
        horizontal_layout2.addWidget(btn_hide)
        horizontal_layout2.addWidget(btn_update)
        grid_layout.addLayout(horizontal_layout2, 3, 0)

        horizontal_layout = QHBoxLayout()
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(qApp.quit)
        self.btn_logout = QPushButton("Разлогиниться")
        horizontal_layout.addWidget(self.btn_logout)
        horizontal_layout.addWidget(btn_close)
        grid_layout.addLayout(horizontal_layout, 4, 0)

        self.timer_refresh.start(1800000)
        self.output_to_plain_text()  # Подсчитываем баллы и выводим на отображение

    def window_hide(self):
        self.hide()
        self.timerHide.stop()

    def window_show_hide(self):
        self.show()
        self.timerHide.start(10000)

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
                self.label_estimate.setText(str(result.get_all_estimate()[person]))
            print(result.issue_error)  # Выводим в консоль задачи с неккоректной оценкой
        except KeyError:
            self.plane2.setPlainText('Закрытых задач не обнаружено')


class PrintApp(QWidget):
    def __init__(self, parent=None):
        super(PrintApp, self).__init__(parent, Qt.Window)
        self.conf = parent.conf
        self.ConnectJira = parent.connect_jira
        self.timerPrint = QTimer()
        self.timerPrint.timeout.connect(self.output_to_file)

        grid_layout = QGridLayout(self)
        self.setLayout(grid_layout)
        font4 = QFont()
        font4.setPointSize(14)
        self.label_log_auth = QLabel('Режим вывода в файл.\nОжидайте')
        self.label_log_auth.setFont(font4)
        grid_layout.addWidget(self.label_log_auth, 1, 0)
        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 2, 0)

        self.timerPrint.start(500)

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

        qApp.quit()  # Завершаем работу программы


class AuthorizationWindow(QDialog):
    def __init__(self, parent=None):
        super(AuthorizationWindow, self).__init__(parent, Qt.Dialog)
        self.setWindowTitle('Окно авторизации')
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setFixedSize(300, 160)

        self.server = QLineEdit()
        self.server.setPlaceholderText('Введите адрес сервера...')
        self.server.setText('http://192.168.100.230:8080/')
        self.login = QLineEdit()
        self.login.setPlaceholderText('Введите логин...')
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText('Введите пароль...')
        self.btn_ok = QPushButton('Ok')
        self.btn_cancel = QPushButton('Отмена')
        self.btn_cancel.clicked.connect(qApp.quit)
        self.label_status_authorization = QLabel('Ожидается авторизация')
        self.__buildAuthorizationWindow()

    def __buildAuthorizationWindow(self):
        layout_form = QFormLayout()
        layout_form.addRow('Сервер:', self.server)
        layout_form.addRow('Логин:', self.login)
        layout_form.addRow('Пароль:', self.password)
        layout_form.addRow('Статус:', self.label_status_authorization)

        layout_horizontal = QHBoxLayout()
        layout_horizontal.addStretch(1)
        layout_horizontal.addWidget(self.btn_ok, 0)
        layout_horizontal.addWidget(self.btn_cancel, 1)

        layout_vertical = QVBoxLayout()
        layout_vertical.addLayout(layout_form, 0)
        layout_vertical.addStretch(1)
        layout_vertical.addLayout(layout_horizontal, 1)
        self.setLayout(layout_vertical)
        self.login.setFocus()  # Устанавливаем курсор ввода в поле Логина
        self.show()

    def getFieldContent(self) -> Tuple[str, str, str]:
        """Возвращает кортеж из содержимого полей адреса, логина и пароля"""
        return self.server.text(), self.login.text(), self.password.text()

    def isFieldsAreNotEmpty(self) -> bool:
        """Проверка на то что поля в форме авторизации не пустые"""
        server, login, password = self.getFieldContent()
        if server != '' and login != '' and password != '':
            return True
        else:
            return False

    def inFieldsFromFileConfiguration(self, server: str, login: str, password: str):
        """Заполняет поля формы авторизации значениями из файла конфигурации"""
        self.server.setText(server)
        self.login.setText(login)
        self.password.setText(password)

    def setInterfaceEnable(self, value_bool: bool):
        """Включает и отключает доступность элементов интерфейса"""
        self.server.setEnabled(value_bool)
        self.login.setEnabled(value_bool)
        self.password.setEnabled(value_bool)
        self.btn_ok.setEnabled(value_bool)
        self.btn_cancel.setEnabled(value_bool)


class MyLabel(QLabel):
    """Переопределил лейбл что бы за него перемещать основное окно"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = args[1]

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        """Переопределил mouseMoveEvent что бы отслеживать координаты перемещения мышки"""
        pos = a0.globalPos()
        pos.setX(pos.x() - 115)
        pos.setY(pos.y() - 7)
        self.main_window.move(pos)


