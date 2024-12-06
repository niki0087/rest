from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, QTextEdit, QScrollArea)
from PyQt5.QtGui import QPalette, QColor, QFont, QPixmap
from PyQt5.QtCore import Qt
from menu_window import MenuWindow  # Импорт нового класса
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class RestaurantDetailsWindow(QWidget):
    def __init__(self, restaurant_info):
        super().__init__()
        self.setWindowTitle(f"Детали ресторана: {restaurant_info.get('name', 'Неизвестный ресторан')}")
        self.setGeometry(100, 100, 800, 600)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Фотография ресторана
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.set_background_image(restaurant_info.get("restaurant_image", ""))
        layout.addWidget(self.photo_label)

        # Описание ресторана
        self.description_label = QLabel("Описание:")
        self.description_label.setStyleSheet("color: #009900; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.description_label)

        self.description_text = QTextEdit()
        self.description_text.setPlainText(restaurant_info.get("description", "Описание отсутствует"))
        self.description_text.setReadOnly(True)
        self.description_text.setStyleSheet("background-color: #001100; color: #009900; border: 2px solid #009900; border-radius: 10px; padding: 10px;")
        layout.addWidget(self.description_text)

        # Средний чек
        self.average_bill_label = QLabel(f"Средний чек: {restaurant_info.get('average_bill', 'Не указан')}")
        self.average_bill_label.setStyleSheet("color: #009900; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.average_bill_label)

        # Кнопки
        button_layout = QHBoxLayout()

        self.menu_button = QPushButton("Меню")
        self.menu_button.setStyleSheet("""
            background-color: #001100;
            color: #009900;
            border: 2px solid #009900;
            border-radius: 10px;
            padding: 10px;
        """)
        self.menu_button.clicked.connect(self.open_menu)
        button_layout.addWidget(self.menu_button)

        self.tables_button = QPushButton("Свободные столики")
        self.tables_button.setStyleSheet("""
            background-color: #001100;
            color: #009900;
            border: 2px solid #009900;
            border-radius: 10px;
            padding: 10px;
        """)
        self.tables_button.clicked.connect(self.open_tables)
        button_layout.addWidget(self.tables_button)

        self.home_button = QPushButton("На главную")
        self.home_button.clicked.connect(self.go_to_home)
        button_layout.addWidget(self.home_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.restaurant_info = restaurant_info
        self.fetch_menu()

    def set_background_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.photo_label.setPixmap(pixmap.scaled(self.photo_label.width(), 300, Qt.KeepAspectRatio))

class RestaurantDetailsWindow(QWidget):
    def __init__(self, restaurant_info):
        super().__init__()
        self.setWindowTitle(f"Детали ресторана: {restaurant_info.get('name', 'Неизвестный ресторан')}")
        self.setGeometry(100, 100, 800, 600)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Фотография ресторана
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.set_background_image(restaurant_info.get("restaurant_image", ""))
        layout.addWidget(self.photo_label)

        # Описание ресторана
        self.description_label = QLabel("Описание:")
        self.description_label.setStyleSheet("color: #009900; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.description_label)

        self.description_text = QTextEdit()
        self.description_text.setPlainText(restaurant_info.get("description", "Описание отсутствует"))
        self.description_text.setReadOnly(True)
        self.description_text.setStyleSheet("background-color: #001100; color: #009900; border: 2px solid #009900; border-radius: 10px; padding: 10px;")
        layout.addWidget(self.description_text)

        # Средний чек
        self.average_bill_label = QLabel(f"Средний чек: {restaurant_info.get('average_bill', 'Не указан')}")
        self.average_bill_label.setStyleSheet("color: #009900; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.average_bill_label)

        # Кнопки
        button_layout = QHBoxLayout()

        self.menu_button = QPushButton("Меню")
        self.menu_button.setStyleSheet("""
            background-color: #001100;
            color: #009900;
            border: 2px solid #009900;
            border-radius: 10px;
            padding: 10px;
        """)
        self.menu_button.clicked.connect(self.open_menu)
        button_layout.addWidget(self.menu_button)

        self.tables_button = QPushButton("Свободные столики")
        self.tables_button.setStyleSheet("""
            background-color: #001100;
            color: #009900;
            border: 2px solid #009900;
            border-radius: 10px;
            padding: 10px;
        """)
        self.tables_button.clicked.connect(self.open_tables)
        button_layout.addWidget(self.tables_button)

        self.home_button = QPushButton("На главную")
        self.home_button.clicked.connect(self.go_to_home)
        button_layout.addWidget(self.home_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.restaurant_info = restaurant_info
        self.fetch_menu()

    def set_background_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.photo_label.setPixmap(pixmap.scaled(self.photo_label.width(), 300, Qt.KeepAspectRatio))

    def fetch_menu(self):
        restaurant_id = self.restaurant_info.get("restaurant_id", "")
        if restaurant_id:
            try:
                logger.debug(f"Fetching menu for restaurant with restaurant_id: {restaurant_id}")
                response = requests.get(f"http://localhost:8000/menu/{restaurant_id}/")
                response.raise_for_status()
                menu_data = response.json()
                logger.debug(f"Received menu data: {menu_data}")
                self.restaurant_info["menu"] = menu_data
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch menu data: {e}")
                self.restaurant_info["menu"] = []

    def open_menu(self):
        menu = self.restaurant_info.get("menu", [])
        logger.debug(f"Opening menu with data: {menu}")
        if not menu:
            QMessageBox.warning(self, "Меню недоступно", "Данные меню для этого ресторана отсутствуют.")
            return
        self.menu_window = MenuWindow(menu)
        self.menu_window.show()

    def open_tables(self):
        # Логика открытия свободных столиков
        QMessageBox.information(self, "Свободные столики", "Функционал свободных столиков будет реализован позже.")

    def go_to_home(self):
        from auth import AuthWindow
        self.auth_window = AuthWindow()
        self.auth_window.show()
        self.close()
    def open_menu(self):
        menu = self.restaurant_info.get("menu", [])
        logger.debug(f"Opening menu with data: {self.restaurant_info}")
        if not menu:
            QMessageBox.warning(self, "Меню недоступно", "Данные меню для этого ресторана отсутствуют.")
            return
        self.menu_window = MenuWindow(menu)
        self.menu_window.show()

    def open_tables(self):
        # Логика открытия свободных столиков
        QMessageBox.information(self, "Свободные столики", "Функционал свободных столиков будет реализован позже.")

    def go_to_home(self):
        from auth import AuthWindow
        self.auth_window = AuthWindow()
        self.auth_window.show()
        self.close()