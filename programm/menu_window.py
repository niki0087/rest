from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy)
from PyQt5.QtGui import QPixmap, QPalette, QColor, QFont
from PyQt5.QtCore import Qt
import logging
import base64

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MenuWindow(QWidget):
    def __init__(self, restaurant_menu):
        super().__init__()
        self.setWindowTitle("Меню ресторана")
        self.setGeometry(100, 100, 800, 600)
        
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)
        
        scroll_area.setWidget(content_widget)
        
        for dish in restaurant_menu:
            dish_widget = self.create_dish_widget(dish)
            content_layout.addWidget(dish_widget)
        
        layout.addWidget(scroll_area)
        self.setLayout(layout)
    
    def create_dish_widget(self, dish):
        layout = QVBoxLayout()
        
        # Фотография
        photo_label = QLabel()
        if dish.get("photo"):
            try:
                pixmap = QPixmap()
                pixmap.loadFromData(base64.b64decode(dish["photo"]))
                photo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            except Exception as e:
                logger.error(f"Ошибка декодирования фотографии для блюда {dish['name']}: {e}")
                photo_label.setText("Ошибка декодирования изображения")
        else:
            photo_label.setText("Нет изображения")
        layout.addWidget(photo_label)
        
        # Название
        name_label = QLabel(dish.get("name", "Нет названия"))
        name_label.setStyleSheet("color: #009900; font-size: 16px; font-weight: bold;")
        layout.addWidget(name_label)
        
        # Описание
        description_label = QLabel(f"Описание: {dish.get('description', 'Не указано')}")
        description_label.setStyleSheet("color: #009900; font-size: 14px;")
        layout.addWidget(description_label)
        
        # Цена
        price_label = QLabel(f"Цена: {dish.get('price', 'Не указана')} руб.")
        price_label.setStyleSheet("color: #009900; font-size: 14px;")
        layout.addWidget(price_label)
        
        widget = QWidget()
        widget.setLayout(layout)
        return widget