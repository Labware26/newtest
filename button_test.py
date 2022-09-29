from PyQt5 import QtCore, QtGui, QtWidgets, Qt
import sys


class AButton(QtWidgets.QGraphicsWidget):
    # нажата ли кнопка мыши
    mouse_isPressed = False

    def __init__(self, parent=None):
        QtWidgets.QGraphicsWidget.__init__(self)

    def boundingRect(self):
        # размеры кнопки
        # для наглядности возвращается фиксированное значение
        # хотя можно считать размеры текста и иконки и
        # использовать их динамически.
        # QRectF, в отличие от QRect, позволяет оперировать
        # числами с плавающей точкой.
        return QtCore.QRectF(0, 0, 40, 40)

    def paint(self, painter, option, widget=0):
        # метод прорисовки кнопки со стилями
        opt = QtWidgets.QStyleOptionButton()

        # стиль нажатой и отжатой кнопки в зависимости от того,
        # нажата ли кнопка мыши
        opt.state = ((QtWidgets.QStyle.State_Sunken if self.mouse_isPressed else QtWidgets.QStyle.State_Raised) | QtWidgets.QStyle.State_Enabled)
        # текст на кнопке
        opt.text = self.text()
        # иконка кнопки
        opt.icon = self.icon()
        # геометрия
        opt.rect = option.rect
        # палитра для стиля
        opt.palette = option.palette

        # сама прорисовка кнопки с определённым выше стилем и опциями
        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_PushButton, opt, painter)

    def text(self):
        # метод, возвращающий текст, отображаемый на кнопке
        # для наглядности возвращаем фиксированное значение
        return "hi"


    def icon(self):
        # метод, возвращающий иконку кнопки
        # пока возвращаем пустую иконку
        # вроде можно использовать QPixmap вместо QIcon
        return QtGui.QIcon()

    def mousePressEvent(self, event):
        # событие нажания кнопки мыши и обновление
        # внешнего вида состояния кнопки
        self.mouse_isPressed = True
        self.update()

    def mouseReleaseEvent(self, event):
        # отжатие кнопки
        self.mouse_isPressed = False
        # метод update - обязательный, он отвечает за перерисовку
        # любого графического виджета
        self.update()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # создаём графическую область, на которой будет рисоваться
    # наша кнопка
    scene = QtWidgets.QGraphicsScene()
    # создаём кнопку
    button = AButton()
    # добавляем кнопку в графическую область
    scene.addItem(button)

    # и создаём графическое поле, на которое накладывается
    # графическая область с кнопкой
    view = QtWidgets.QGraphicsView(scene)
    # сглаживание
    view.setRenderHint(QtGui.QPainter.Antialiasing)
    # задаём размер графического поля
    view.resize(200, 100)
    # фон
    # view.setBackgroundBrush(QtWidgets.QApplication.palette())
    view.show()

    sys.exit(app.exec_())

