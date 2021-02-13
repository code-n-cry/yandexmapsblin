import requests
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys


class Parser:
    def request_map(self, cords, zoom, style, pt=None):
        str_cords = ','.join(cords[::-1])
        service = 'https://static-maps.yandex.ru/1.x/'
        if pt:
            map_params = {
                'll': str_cords,
                'size': '450,450',
                'l': f'{style}',
                'z': zoom,
                'pt': pt
            }
        else:
            map_params = {
                'll': str_cords,
                'size': '450,450',
                'l': f'{style}',
                'z': zoom
            }
        response = requests.get(service, params=map_params)
        with open('map.png', 'wb') as image:
            image.write(response.content)

    def request_cords(self, place):
        service = 'http://geocode-maps.yandex.ru/1.x/'
        paramss = {
            'geocode': place,
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
            'format': 'json'
        }
        response = requests.get(service, params=paramss).json()
        toponym = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        return toponym_coodrinates


class InputWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi('map.ui', self)
        self.setWindowTitle('Ввод координат')
        self.showMap.clicked.connect(self.load_image)
        self.parser = Parser()
        self.map_show = False
        self.pt = None
        self.map_cords = None
        self.zoom = 9
        self.lineEdit_3.setText('Москва')
        self.style = 'map'
        lst = [self.mapButton, self.satButton, self.sklButton]
        for i in lst:
            i.clicked.connect(lambda state, name=i.text(): self.sut(name))

    def load_image(self):
        first_cords = self.lineEdit.text()
        sec_cords = self.lineEdit_2.text()
        toponym = self.lineEdit_3.text()
        if first_cords and sec_cords:
            cords = [first_cords, sec_cords]
            self.map_cords = cords
            self.parser.request_map(cords, self.zoom, self.style)
            pixmap = QPixmap('map.png')
            self.label_3.setPixmap(pixmap)
            self.map_show = True
        elif toponym:
            right_cords = self.parser.request_cords(toponym).split(' ')
            self.map_cords = right_cords[::-1]
            crd = ','.join(self.map_cords[::-1])
            self.parser.request_map(self.map_cords, self.zoom, self.style, pt=f'{crd},pma')
            self.pt = f'{crd},pma'
            pixmap = QPixmap('map.png')
            self.label_3.setPixmap(pixmap)
            self.map_show = True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown and self.map_show:
            if self.zoom < 17:
                self.zoom += 1
        if event.key() == Qt.Key_PageUp and self.map_show:
            if self.zoom > 0:
                self.zoom -= 1
        if event.key() == Qt.Key_D and self.map_show:
            self.map_cords[1] = str(float(self.map_cords[1]) + ((360 / pow(2, self.zoom + 8)) * 325))
        if event.key() == Qt.Key_A and self.map_show:
            self.map_cords[1] = str(float(self.map_cords[1]) - ((360 / pow(2, self.zoom + 8)) * 325))
        if event.key() == Qt.Key_W and self.map_show:
            self.map_cords[0] = str(float(self.map_cords[0]) + ((360 / pow(2, self.zoom + 8)) * 225))
        if event.key() == Qt.Key_S and self.map_show:
            self.map_cords[0] = str(float(self.map_cords[0]) - ((360 / pow(2, self.zoom + 8)) * 225))
        if self.pt:
            self.parser.request_map(self.map_cords, self.zoom, self.style, self.pt)
        else:
            self.parser.request_map(self.map_cords, self.zoom, self.style)
        pixmap = QPixmap('map.png')
        self.label_3.setPixmap(pixmap)

    def sut(self, text):
        if text == 'Гибрид':
            self.style = 'sat,skl'
        if text == 'Карта':
            self.style = 'map'
        if text == 'Спутник':
            self.style = 'sat'
        if self.pt:
            self.parser.request_map(self.map_cords, self.zoom, self.style, self.pt)
        else:
            self.parser.request_map(self.map_cords, self.zoom, self.style)
        pixmap = QPixmap('map.png')
        self.label_3.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    p = Parser()
    m = InputWindow()
    m.show()
    sys.exit(app.exec())
