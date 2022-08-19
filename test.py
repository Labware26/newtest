from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QFileDialog
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__() # методу super задаем с какого родительского класса производить поиск метода
        self.setWindowTitle("Таблица")  # Установить заголовок окна
        self.setMaximumSize(800, 600)
        self.setMinimumSize(800, 600)

        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setShowGrid(True)
        self.tableWidget.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setGeometry(1,1,798,598)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setHorizontalHeaderLabels(['Фамилия', 'Оценка', 'Прогресс', 'Порог'])
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setStretchLastSection(False)
        self.tableWidget.verticalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setSortIndicatorShown(False)
        self.tableWidget.verticalHeader().setStretchLastSection(False)


        #Инициируем виджет прогресбара
        self.progresBar = QtWidgets.QProgressBar(self)
        self.progresBar.setOrientation(QtCore.Qt.Horizontal)
        self.progresBar.setValue(120)
        self.progresBar.setTextVisible(True)
        self.progresBar.setGeometry(10,10,10,10)
        self.progresBar.setMaximum(160)
        #Помещаем виджет в ячейку таблици
        self.tableWidget.setCellWidget(1, 2, self.progresBar)

        #Инициируем объект QTableWidgetItem, в котором задаем содержимое ячейки в формате СТРОКА
        self.a = QtWidgets.QTableWidgetItem("Фамилия")
        self.tableWidget.setItem(0,0,self.a) #Помещаем ранее созданный item в ячейку




def application():
    app = QApplication(sys.argv)  # Создать объект приложения
    main_window = MainWindow()  # Создаем объект окна на основе собственного класса

    main_window.show()  # показать окно
    sys.exit(app.exec_()) # Запуск программы

if __name__ == "__main__":
    application()