import requests
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys


class Parser:
    def __init__(self):
        self.org_apikey = '85bdbf69-a248-4ef5-8968-ed2566c2ce41'
        self.geo_apikey = '40d1649f-0493-4b70-98ba-98533de7710b'
        self.geo_service = 'http://geocode-maps.yandex.ru/1.x/'
        self.map_service = 'https://static-maps.yandex.ru/1.x/'
        self.org_service = 'https://search-maps.yandex.ru/v1/'

    def request_map(self, cords, zoom, style, pt=None):
        str_cords = ','.join(cords[::-1])
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
        response = requests.get(self.map_service, params=map_params)
        with open('map.png', 'wb') as image:
            image.write(response.content)

    def request_cords(self, place):
        geo_params = {
            'geocode': place,
            'apikey': self.geo_apikey,
            'format': 'json'
        }
        response = requests.get(self.geo_service, params=geo_params).json()
        toponym = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        return toponym_coodrinates

    def request_address(self, cords):
        geo_params = {
            'geocode': ','.join(cords[::-1]),
            'apikey': self.geo_apikey,
            'format': 'json'
        }
        response = requests.get(self.geo_service, params=geo_params).json()
        toponym = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
        toponym_address = toponym['metaDataProperty']['GeocoderMetaData']['text']
        return toponym_address


class InputWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi('map.ui', self)
        self.setWindowTitle('MapApp')
        self.showMap.clicked.connect(self.load_image)
        self.parser = Parser()
        self.map_show = False
        self.pt = None
        self.map_cords = None
        self.zoom = 9
        self.lineEdit_3.setText('Москва')
        self.style = 'map'
        self.address = None
        lst = [self.mapButton, self.satButton, self.sklButton]
        for i in lst:
            i.clicked.connect(lambda state, name=i.text(): self.sut(name))
        self.resetButton.clicked.connect(self.reset)

    def load_image(self):
        first_cords = self.lineEdit.text()
        sec_cords = self.lineEdit_2.text()
        toponym = self.lineEdit_3.text()
        if first_cords and sec_cords:
            cords = [first_cords, sec_cords]
            self.map_cords = cords
            self.set_map()
            self.map_show = True
            address = self.parser.request_address(self.map_cords)
            self.addressLabel.setText('Адресс: ' + address)
            self.address = address
        elif toponym:
            right_cords = self.parser.request_cords(toponym).split(' ')
            self.map_cords = right_cords[::-1]
            crd = ','.join(self.map_cords[::-1])
            self.parser.request_map(self.map_cords, self.zoom, self.style, pt=f'{crd},pma')
            self.pt = f'{crd},pma'
            self.set_map()
            self.map_show = True
            self.addressLabel.setText('Адресс: ' + toponym)
            self.address = toponym

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown and self.map_show:
            if self.zoom < 17:
                self.zoom += 1
        if event.key() == Qt.Key_PageUp and self.map_show:
            if self.zoom > 0:
                self.zoom -= 1
        if event.nativeVirtualKey() == Qt.Key_D and self.map_show:
            self.map_cords[1] = str(
                float(self.map_cords[1]) + ((360 / pow(2, self.zoom + 8)) * 325))
        if event.nativeVirtualKey() == Qt.Key_A and self.map_show:
            self.map_cords[1] = str(
                float(self.map_cords[1]) - ((360 / pow(2, self.zoom + 8)) * 325))
        if event.nativeVirtualKey() == Qt.Key_W and self.map_show:
            self.map_cords[0] = str(
                float(self.map_cords[0]) + ((360 / pow(2, self.zoom + 8)) * 225))
        if event.nativeVirtualKey() == Qt.Key_S and self.map_show:
            self.map_cords[0] = str(
                float(self.map_cords[0]) - ((360 / pow(2, self.zoom + 8)) * 225))
        if self.map_show:
            self.set_map()

    def set_map(self):
        self.parser.request_map(self.map_cords, self.zoom, self.style, self.pt)
        pixmap = QPixmap('map.png')
        self.address = None
        self.label_3.setPixmap(pixmap)

    def reset(self):
        self.pt = None
        self.set_map()
        self.addressLabel.clear()

    def sut(self, text):
        if text == 'Гибрид':
            self.style = 'sat,skl'
        if text == 'Карта':
            self.style = 'map'
        if text == 'Спутник':
            self.style = 'sat'
        self.set_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    p = Parser()
    m = InputWindow()
    m.show()
    sys.exit(app.exec())
