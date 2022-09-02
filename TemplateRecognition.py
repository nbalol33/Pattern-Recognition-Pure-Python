import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import PIL
from PIL import Image, ImageDraw
import numpy as np
import math


class Ui_MainWindow(object):
    big_pic_src = 0
    big_pic_clr = 0
    tmp_pic_src = 0

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Template Recognition")
        MainWindow.setEnabled(True)
        MainWindow.resize(1000, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.full = QtWidgets.QPushButton(self.centralwidget)
        self.full.setGeometry(QtCore.QRect(50, 510, 180, 50))
        self.full.setStyleSheet("background-color: rgb(0, 255, 127);\n"
                                "background-color: rgb(85, 255, 0);")
        self.full.setObjectName("full")
        self.frame = QtWidgets.QPushButton(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(410, 510, 170, 50))
        self.frame.setStyleSheet("background-color: rgb(0, 255, 127);\n"
                                 "background-color: rgb(85, 255, 0);")
        self.frame.setObjectName("frame")
        self.find = QtWidgets.QPushButton(self.centralwidget)
        self.find.setGeometry(QtCore.QRect(760, 510, 170, 50))
        self.find.setStyleSheet("background-color: rgb(255, 67, 10);")
        self.find.setObjectName("find")
        self.images = QtWidgets.QLabel(self.centralwidget)
        self.images.setGeometry(QtCore.QRect(20, 20, 951, 391))
        self.images.setScaledContents(False)
        self.images.setAlignment(QtCore.Qt.AlignCenter)
        self.images.setObjectName("images")
        self.results = QtWidgets.QLabel(self.centralwidget)
        self.results.setGeometry(QtCore.QRect(220, 440, 531, 51))
        self.results.setStyleSheet("background-color: rgb(255, 255, 127);")
        self.results.setAlignment(QtCore.Qt.AlignCenter)
        self.results.setObjectName("results")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # added
        self.full.clicked.connect(self.browsefiles1)
        self.frame.clicked.connect(self.browsefiles2)
        self.find.clicked.connect(self.finder)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Поиск шаблона"))
        self.full.setText(_translate("MainWindow", "Загрузить основное изображение"))
        self.frame.setText(_translate("MainWindow", "Загрузить фрагмент для поиска"))
        self.find.setText(_translate("MainWindow", "Поиск"))
        self.images.setText(_translate("MainWindow", "Здесь будут ваши изображения"))
        self.results.setText(_translate("MainWindow", "Выберите основное изображение"))

    def browsefiles1(self):
        fname = QFileDialog.getOpenFileName(None, "Выберите основное изображение", 'C:', 'Images (*.bmp)')
        self.results.setText("Выберите фрагмент для поиска")
        Ui_MainWindow.big_pic_src = fname[0]
        PIL.Image.open(fname[0]).show()
        self.images.setPixmap(QtGui.QPixmap(fname[0]))

    def browsefiles2(self):
        fname = QFileDialog.getOpenFileName(None, "Выберите фрагмент", 'C:', 'Images (*.bmp)')
        self.results.setText("Начните поиск")
        Ui_MainWindow.tmp_pic_src = fname[0]
        PIL.Image.open(fname[0]).show()
        self.images.setPixmap(QtGui.QPixmap(fname[0]))

    def finder(self):
        self.results.setText("Идет поиск шаблона")
        try:
            big_pic_clr = PIL.Image.open(Ui_MainWindow.big_pic_src)
            big_pic = PIL.Image.open(Ui_MainWindow.big_pic_src).convert("L")
            big = np.array(big_pic)
            tmp_pic = PIL.Image.open(Ui_MainWindow.tmp_pic_src).convert("L")
            tmp = np.array(tmp_pic)
        except:
            self.images.setText("Ошибка: Не выбрано одно из изображений")
            return

        if np.shape(tmp)[1] > np.shape(big)[1] or np.shape(tmp)[0] > np.shape(big)[0]:
            self.results.setText("Ошибка: Фрагмент больше основного изображения")
            self.images.setPixmap(QtGui.QPixmap('error.jpg'))
            return
        else:
            tmp_x = np.shape(tmp)[1]
            tmp_y = np.shape(tmp)[0]

            big_x = np.shape(big)[1]
            big_y = np.shape(big)[0]

            ncorr2d = np.zeros((big_y - tmp_y + 1, big_x - tmp_x + 1))
            big_mean = np.zeros((tmp_y, tmp_x))
            tmp_mean = np.mean(tmp)

            for x in range(big_x - tmp_x + 1):
                for y in range(big_y - tmp_y + 1):
                    for m in range(tmp_x):
                        for n in range(tmp_y):
                            # считаем среднее значение под шаблоном
                            big_mean[n][m] = big[y + n][x + m]
                    big_mean_total = np.mean(big_mean)

                    numerator = sum(
                        ((big[y + i][x + j] - big_mean_total) * (tmp[i][j] - tmp_mean)) for i in range(tmp_y) for j in
                        range(tmp_x))

                    denominator = (math.sqrt(
                        sum(((big[y + p][x + k] - big_mean_total) ** 2) for p in range(tmp_y) for k in range(tmp_x))
                        * sum(((tmp[t][r] - tmp_mean) ** 2) for t in range(tmp_y) for r in range(tmp_x))))

                    ncorr2d[y][x] = numerator / denominator
                    if ncorr2d[y][x] > 1 or ncorr2d[y][x] < -1:
                        print("Error ncorr2d value out of expected range -1<>1")
                        break
                    print(ncorr2d[y][x], x, y)

            np_ncorr2d = np.asarray(ncorr2d)
            max_value = np.amax(np_ncorr2d)
            index_y, index_x = (np.argwhere(np_ncorr2d == max_value)[0][0], np.argwhere(np_ncorr2d == max_value)[0][1])
            if max_value < 0.7:
                self.results.setText("Наибольшее значение коэффициента корреляции мало: " + str(max_value) +
                                    ". \n Возможно, искомого шаблона нет в изображении. \n Проверьте входные "
                                    "изображения и повторите попытку")
                self.images.setPixmap(QtGui.QPixmap('error.jpg'))
                return

            rectangle = ImageDraw.Draw(big_pic_clr)
            rectangle.rectangle([(index_x, index_y), (index_x + tmp_x, index_y + tmp_y)], width=2, outline='red')
            big_pic_clr.save('result.bmp')
            big_pic_clr.show()
            self.images.setPixmap(QtGui.QPixmap('result.bmp'))
            self.results.setText("Координаты фрагмента по X: " + str(index_x) + " и Y: " + str(index_y) + ", корреляция: " + str(max_value))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
