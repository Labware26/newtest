from PyQt5 import QtCore, QtWidgets
# import pyqtgraph as pg

class App(QtWidgets.QApplication):
    def __init__(self, args):
        super(App, self).__init__(args)
        #window tracking
        self.last_idx = 0
        self.windows = {}

        #chart data
        self.x = [1,2,3,4,5]
        self.y = [1,2,3,4,5]

        #create button window
        self.button_window = ButtonWindow()

        #enter event loop
        self.exec_()

    @QtCore.pyqtSlot()
    def new_window(self):
        window = ChartWindow(self, self.last_idx)
        window.closed.connect(self.remove_window)
        self.windows[self.last_idx] = window
        self.last_idx += 1

    @QtCore.pyqtSlot(int)
    def remove_window(self, idx):
        w = self.windows[idx]
        w.deleteLater()
        del self.windows[idx]
        print(self.windows)

class ButtonWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ButtonWindow, self).__init__(parent)
        grid = QtWidgets.QGridLayout(self)
        self.btn = QtWidgets.QPushButton('+1 Chart Window')
        self.btn.clicked.connect(QtWidgets.QApplication.instance().new_window)
        grid.addWidget(self.btn, 0, 0)
        self.show()

class ChartWindow(QtWidgets.QWidget):
    closed = QtCore.pyqtSignal(int)

    def __init__(self, app, window_id):
        super(ChartWindow, self).__init__()
        grid = QtWidgets.QGridLayout(self)
        self.window_id = window_id
        self.setWindowTitle('Chart Window '+str(self.window_id))
        #add a chart
        # self.chart = pg.PlotWidget()
        # self.chart.plot(app.x,app.y)
        # grid.addWidget(self.chart,0,0)
        #show window
        self.show()

    def closeEvent(self, event):
        self.closed.emit(self.window_id)
        super(ChartWindow, self).closeEvent(event)

def main():
    app = App([])
if __name__ == '__main__':
    main()