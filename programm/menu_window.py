from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QFrame)
from PyQt5.QtGui import QPixmap, QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
import os

def get_image_path(image_name):
    return os.path.join(os.path.dirname(__file__), "img", image_name)

class MenuWindow(QWidget):
    def __init__(self, restaurant_menu):
        super().__init__()
        self.setWindowTitle("Меню ресторана")
        self.setGeometry(100, 100, 800, 600)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        self.restaurant_menu = restaurant_menu
        self.current_page = 0

        self.layout = QVBoxLayout()

        self.page_layout = QHBoxLayout()
        self.layout.addLayout(self.page_layout)

        self.prev_button = QPushButton("Предыдущая страница")
        self.prev_button.clicked.connect(self.show_previous_page)
        self.layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Следующая страница")
        self.next_button.clicked.connect(self.show_next_page)
        self.layout.addWidget(self.next_button)

        self.setLayout(self.layout)

        self.show_current_page()

    def show_current_page(self):
        for i in reversed(range(self.page_layout.count())):
            self.page_layout.itemAt(i).widget().setParent(None)

        start_index = self.current_page * 2
        end_index = start_index + 2

        for i in range(start_index, end_index):
            if i < len(self.restaurant_menu):
                dish = self.restaurant_menu[i]
                dish_widget = self.create_dish_widget(dish)
                self.page_layout.addWidget(dish_widget)

    def create_dish_widget(self, dish):
        dish_widget = QFrame()
        dish_widget.setStyleSheet("""
            background-color: #001100;
            border: 2px solid #009900;
            border-radius: 10px;
            padding: 10px;
        """)

        layout = QVBoxLayout()

        # Фотография блюда
        photo_label = QLabel()
        photo_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(get_image_path(dish.get("image", "")))
        if not pixmap.isNull():
            photo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        layout.addWidget(photo_label)

        # Название блюда
        name_label = QLabel(dish.get("name", ""))
        name_label.setStyleSheet("color: #009900; font-size: 16px; font-weight: bold;")
        layout.addWidget(name_label)

        # Состав блюда
        ingredients_label = QLabel(f"Состав: {dish.get('ingredients', 'Не указан')}")
        ingredients_label.setStyleSheet("color: #009900; font-size: 14px;")
        layout.addWidget(ingredients_label)

        # Стоимость блюда
        price_label = QLabel(f"Цена: {dish.get('price', 'Не указана')} руб.")
        price_label.setStyleSheet("color: #009900; font-size: 14px;")
        layout.addWidget(price_label)

        dish_widget.setLayout(layout)
        return dish_widget

    def show_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_current_page()

    def show_next_page(self):
        if (self.current_page + 1) * 2 < len(self.restaurant_menu):
            self.current_page += 1
            self.show_current_page()