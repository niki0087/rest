from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QFrame, QHBoxLayout, QVBoxLayout)
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
        self.setGeometry(100, 100, 500, 600)  # Устанавливаем начальные размеры
        self.setMaximumWidth(500)  # Ограничиваем максимальную ширину
        self.setMaximumHeight(600)
        
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#CCFFCC"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            border: 2px solid #000000;
            background-color: white;
        """)

        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background-color: white;
            border: none;  /* Убираем внутренние рамки */
        """)
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)

        scroll_area.setWidget(content_widget)

        self.pages = []
        self.current_page = 0

        self.create_pages(restaurant_menu, content_layout)

        layout.addWidget(scroll_area)

        self.prev_button = QPushButton("Предыдущая страница")
        self.prev_button.setStyleSheet("""
            background-color: #CCFFCC;
            color: #000000;
            border: 2px solid #000000;
            border-radius: 10px;
            padding: 10px;
        """)
        self.prev_button.clicked.connect(self.prev_page)
        layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Следующая страница")
        self.next_button.setStyleSheet("""
            background-color: #CCFFCC;
            color: #000000;
            border: 2px solid #000000;
            border-radius: 10px;
            padding: 10px;
        """)
        self.next_button.clicked.connect(self.next_page)
        layout.addWidget(self.next_button)

        self.setLayout(layout)

        self.show_page(self.current_page)

    def create_pages(self, menu, layout):
        page_layout = QVBoxLayout()
        page_frame = QFrame()
        page_frame.setStyleSheet("""
            background-color: white;
            border: none;  /* Убираем внутренние рамки */
        """)
        page_frame.setLayout(page_layout)
        self.pages.append(page_frame)

        for i, dish in enumerate(menu):
            if i % 2 == 0 and i != 0:
                page_layout = QVBoxLayout()
                page_frame = QFrame()
                page_frame.setLayout(page_layout)
                self.pages.append(page_frame)

            dish_widget = self.create_dish_widget(dish)
            page_layout.addWidget(dish_widget)

        for page in self.pages:
            layout.addWidget(page)
            page.hide()

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
        name_label.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold;")
        layout.addWidget(name_label)

        # Описание
        description_label = QLabel(f"Описание: {dish.get('description', 'Не указано')}")
        description_label.setStyleSheet("color: #000000; font-size: 14px;")
        layout.addWidget(description_label)

        # Цена
        price_label = QLabel(f"Цена: {dish.get('price', 'Не указана')} руб.")
        price_label.setStyleSheet("color: #000000; font-size: 14px;")
        layout.addWidget(price_label)

        widget = QWidget()
        widget.setStyleSheet("background-color: white;")
        widget.setLayout(layout)
        return widget

    def show_page(self, page_index):
        if 0 <= page_index < len(self.pages):
            for page in self.pages:
                page.hide()
            self.pages[page_index].show()
            self.current_page = page_index

    def prev_page(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.show_page(self.current_page + 1)