import requests
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys
import os


class Parser:
    def request_map(self, cords, zoom, sutl):
        str_cords = ','.join(cords[::-1])
        service = 'https://static-maps.yandex.ru/1.x/'
        map_params = {
            'll': str_cords,
            'size': '450,450',
            'l': f'{sutl}',
            'z': zoom
        }
        response = requests.get(service, params=map_params)
        with open('map.png', 'wb') as image:
            image.write(response.content)


class Input_window(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi('map.ui', self)
        self.sutl = 'map'
        self.setWindowTitle('Ввод координат')
        self.showMap.clicked.connect(self.load_image)
        self.parser = Parser()
        self.map_show = False
        self.map_cords = None
        self.zoom = 9
        self.comboBox.activated[str].connect(self.sut) 
    def load_image(self):
        first_cords = self.lineEdit.text()
        sec_cords = self.lineEdit_2.text()
        cords = [first_cords, sec_cords]
        self.map_cords = cords
        self.parser.request_map(cords, self.zoom, self.sutl)
        pixmap = QPixmap('map.png')
        self.label_3.setPixmap(pixmap)
        self.map_show = True

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_PageDown and self.map_show:
                if self.zoom < 17:
                    self.zoom += 1
                    self.parser.request_map(self.map_cords, self.zoom, self.sutl)
                    pixmap = QPixmap('map.png')
                    self.label_3.setPixmap(pixmap)
            if event.key() == Qt.Key_PageUp and self.map_show:
                if self.zoom > 0:
                    self.zoom -= 1
                    self.parser.request_map(self.map_cords, self.zoom, self.sutl)
                    pixmap = QPixmap('map.png')
                    self.label_3.setPixmap(pixmap)
            print(self.map_cords)
        except Exception as e:
            print(e)
    def sut(self, text):
        if text == 'Гибрид':
            self.sutl = 'sat,skl'
        if text == 'Карта':
            self.sutl = 'map'
        if text == 'Спутник':
            self.sutl = 'sat'
        if self.map_show:
            print(1)
            self.parser.request_map(self.map_cords, self.zoom, self.sutl)
            pixmap = QPixmap('map.png')
            self.label_3.setPixmap(pixmap)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    p = Parser()
    m = Input_window()
    m.show()
    sys.exit(app.exec())
