from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QFileDialog
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__() # методу super задаем с какого родительского класса производить поиск метода
        self.setWindowTitle("Нанокриптоступенчатый преобразователь")  # Установить заголовок окна
        self.setMaximumSize(470, 510)
        self.setMinimumSize(470, 510)

        self.createMenuBar()

        # Добавляем объект Текст на наше окно
        self.text = QtWidgets.QLabel(self)  # создаем объект текст и указываем какому окну он будет пренадлежать
        self.text.setText('Вставьте текст требующий преобразования')  # Задаем содержимое текста
        self.text.move(1, 14)  # Сдвигает виджет в пределах окна от левого угла
        #self.text.adjustSize()  # Подстраивает ширину объекта под его содержимое
        self.text.setFixedWidth(350)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.text.setFont(font)

        self.plane1 = QtWidgets.QPlainTextEdit(self)
        self.plane1.setGeometry(0, 40, 400, 200)

        self.plane2 = QtWidgets.QPlainTextEdit(self)
        self.plane2.setGeometry(0, 300, 400, 200)
        self.plane2.setReadOnly(True)

        # Создаем прогрессбар
        self.progresBar = QtWidgets.QProgressBar(self)
        self.progresBar.setGeometry(410, 40, 50, 460)
        self.progresBar.setOrientation(QtCore.Qt.Vertical)
        self.progress = 0
        self.progresBar.setValue(0)

        # Создадим кнопку
        self.btn = QtWidgets.QPushButton(self)  # создаем объект кнопка и указываем какому окну он будет пренадлежать
        self.btn.move(200, 255)  # Задаем смещение для кнопки
        self.btn.setText("Начать преобразование")  # Задаем тектс для кнопки
        self.btn.setFixedWidth(200)  # Задаем фиксированную ширину кнопки

        # Тут отслеживаем нажатие кнопки
        self.btn.clicked.connect(self.timerstart)

        # Создаем экземпляр таймера
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)

    # по нажатию кнопки принудительно устанавливаем значение прогресбара в 0, бликируем кнопку и запускаем таймер
    def timerstart(self):
        print('Кнопка нажата')
        self.progress = 0
        self.btn.blockSignals(True)
        self.timer.start(50) # только после запуска таймера начнется вызываться функция tick

    # каждые 50 мс мы обновляем прогресс бар и проверяем когда он станет 100,
    # после чего останавливаем таймер и вызываем функцию преобразования
    def tick(self):
        self.progress +=2
        self.progresBar.setValue(self.progress)
        if self.progress == 100:
            self.timer.stop()
            self.add_text()

    def createMenuBar(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)
        self.menuBar.addAction("Открыть", self.action_clicked)
        self.menuBar.addAction("Сохранить", self.action_clicked)

    @QtCore.pyqtSlot()
    def action_clicked(self):
        action = self.sender()
        if action.text() == "Открыть":
            fname = QFileDialog.getOpenFileName(self, "Сохранение текстового файла", "", "Text Files (*.txt);;All files()")[0] # ;;выбор фильтра
            try:
                with open(fname, "r", encoding="utf-8") as f:
                    date1 = f.read()
                    self.plane1.setPlainText(date1)
            except FileNotFoundError:
                print("файл не найден")
        elif action.text() == "Сохранить":
            fname = QFileDialog.getSaveFileName(self, "Сохранение текстового файла", "", "Text Files (*.txt)")[0] #Заголовок, директория, фильтр
            try:
                with open(fname, "w") as f:
                    date2 = self.plane2.toPlainText()
                    f.write(date2)
            except FileNotFoundError:
                print("файл не найден")
            print("Save")

    # функция преобразования текста
    def add_text(self):
        string1 = self.plane1.toPlainText()
        string2 = ''
        for leng in range(0, len(string1)):
            if leng % 2 == 0:
                    string2 += string1[leng].upper()
            else:
                    string2 += string1[leng].lower()
        self.plane2.setPlainText(string2)
        self.btn.blockSignals(False)


def application():
    app = QApplication(sys.argv)  # Создать объект приложения
    main_window = MainWindow()  # Создаем объект окна на основе собственного класса

    main_window.show()  # показать окно
    sys.exit(app.exec_()) # Запуск программы

if __name__ == "__main__":
    application()
