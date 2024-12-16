from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, QTextEdit, QScrollArea, QStackedWidget
)
from PyQt5.QtGui import QPalette, QColor, QFont, QPixmap
from PyQt5.QtCore import Qt
from menu_window import MenuWindow  # Импорт нового класса
from seating_window import SeatingWindow  # Импорт нового класса
from review_window import ReviewWindow  # Импорт нового класса
import requests
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

class RestaurantDetailsWindow(QWidget):
    def __init__(self, restaurant_info, stacked_widget, auth_window):
        super().__init__()
        self.auth_window = auth_window  # Сохраняем ссылку на окно аутентификации
        self.setWindowTitle(f"Детали ресторана: {restaurant_info.get('name', 'Неизвестный ресторан')}")
        self.setGeometry(100, 100, 800, 600)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#CCFFCC"))
        self.setPalette(palette)

        self.layout = QVBoxLayout()  # Инициализация self.layout
        self.setLayout(self.layout)

        # Сохраняем restaurant_info в атрибут класса
        self.restaurant_info = restaurant_info

        # Вывод всех данных, переданных в restaurant_info, в лог
        logger.debug(f"Данные ресторана: {self.restaurant_info}")

        # Убедитесь, что restaurant_info содержит ключ restaurant_id
        if "restaurant_id" not in self.restaurant_info:
            self.restaurant_info["restaurant_id"] = None  # Устанавливаем значение по умолчанию

        # Загрузка основных данных о ресторане (если они не были загружены ранее)
        if "opening_hours" not in self.restaurant_info or "phone_number" not in self.restaurant_info:
            self.fetch_restaurant_data(self.restaurant_info.get("restaurant_id"))

        # Фотография ресторана
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.set_background_image(self.restaurant_info.get("restaurant_image", ""))
        self.layout.addWidget(self.photo_label)

        # Информация о ресторане
        self.info_layout = QVBoxLayout()
        self.info_layout.setAlignment(Qt.AlignLeft)

        # Название ресторана
        self.name_label = QLabel(f"Название: {self.restaurant_info.get('name', 'Неизвестный ресторан')}")
        self.name_label.setStyleSheet("color: #000000; font-size: 18px; font-weight: bold;")
        self.info_layout.addWidget(self.name_label)

        # Адрес ресторана
        self.address_label = QLabel(f"Адрес: {self.restaurant_info.get('address', 'Не указан')}")
        self.address_label.setStyleSheet("color: #000000; font-size: 16px;")
        self.info_layout.addWidget(self.address_label)

        # Город
        self.city_label = QLabel(f"Город: {self.restaurant_info.get('city', 'Не указан')}")
        self.city_label.setStyleSheet("color: #000000; font-size: 16px;")
        self.info_layout.addWidget(self.city_label)

        # Тип кухни
        self.cuisine_label = QLabel(f"Тип кухни: {self.restaurant_info.get('cuisine_type', 'Не указан')}")
        self.cuisine_label.setStyleSheet("color: #000000; font-size: 16px;")
        self.info_layout.addWidget(self.cuisine_label)

        # Рейтинг
        self.rating_label = QLabel(f"Рейтинг: {self.restaurant_info.get('rating', 'Не указан')}")
        self.rating_label.setStyleSheet("color: #000000; font-size: 16px;")
        self.info_layout.addWidget(self.rating_label)

        # Телефон
        self.phone_label = QLabel(f"Телефон: {self.restaurant_info.get('phone_number', 'Не указан')}")
        self.phone_label.setStyleSheet("color: #000000; font-size: 16px;")
        self.info_layout.addWidget(self.phone_label)

        # Часы работы
        self.opening_hours_label = QLabel(f"Часы работы: {self.restaurant_info.get('opening_hours', 'Не указан')}")
        self.opening_hours_label.setStyleSheet("color: #000000; font-size: 16px;")
        self.info_layout.addWidget(self.opening_hours_label)

        # Добавляем информацию о ресторане в основной макет
        self.layout.addLayout(self.info_layout)

        # Описание ресторана
        self.description_label = QLabel("Описание:")
        self.description_label.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.description_label)

        self.description_text = QTextEdit()
        self.description_text.setPlainText(self.restaurant_info.get("description", "Описание отсутствует"))
        self.description_text.setReadOnly(True)
        self.description_text.setStyleSheet("background-color: #CCFFCC; color: #000000; border: 2px solid #000000; border-radius: 10px; padding: 10px;")
        self.layout.addWidget(self.description_text)

        # Средний чек
        self.average_bill_label = QLabel(f"Средний чек: {self.restaurant_info.get('average_bill', 'Не указан')}")
        self.average_bill_label.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.average_bill_label)

        # Кнопка "Отзывы"
        self.reviews_button = QPushButton("Отзывы")
        self.reviews_button.setStyleSheet("""
            background-color: #CCFFCC;
            color: #000000;
            border: 2px solid #000000;
            border-radius: 10px;
            padding: 10px;
        """)
        self.reviews_button.clicked.connect(self.open_reviews)
        self.layout.addWidget(self.reviews_button)

        # Кнопки
        button_layout = QHBoxLayout()

        self.menu_button = QPushButton("Меню")
        self.menu_button.setStyleSheet("""
            background-color: #CCFFCC;
            color: #000000;
            border: 2px solid #000000;
            border-radius: 10px;
            padding: 10px;
        """)
        self.menu_button.clicked.connect(self.open_menu)
        button_layout.addWidget(self.menu_button)

        self.tables_button = QPushButton("Свободные столики")
        self.tables_button.setStyleSheet("""
            background-color: #CCFFCC;
            color: #000000;
            border: 2px solid #000000;
            border-radius: 10px;
            padding: 10px;
        """)
        self.tables_button.clicked.connect(self.open_tables)
        button_layout.addWidget(self.tables_button)

        self.layout.addLayout(button_layout)

        # Добавляем QStackedWidget для отображения различных окон
        self.stacked_widget = stacked_widget

    def set_background_image(self, image_path):
        """Устанавливает фоновое изображение для ресторана."""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.photo_label.setPixmap(pixmap.scaled(self.photo_label.width(), 300, Qt.KeepAspectRatio))

    def fetch_restaurant_data(self, restaurant_id):
        """Загружает основные данные о ресторане по его ID."""
        if not restaurant_id:  # Проверяем, что restaurant_id не пустой
            logger.error("ID ресторана отсутствует или пуст.")
            return

        url = f"http://localhost:8000/restaurant/{restaurant_id}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                restaurant_data = response.json()
                # Обновляем restaurant_info
                self.restaurant_info.update(restaurant_data)
                logger.debug(f"Updated restaurant data: {self.restaurant_info}")
            else:
                logger.warning("Не удалось загрузить основные данные ресторана.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения: {e}")

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
        self.stacked_widget.addWidget(self.menu_window)
        self.stacked_widget.setCurrentWidget(self.menu_window)

    def open_tables(self):
        """Открывает окно со свободными столиками."""
        self.seating_window = SeatingWindow(self.restaurant_info.get("restaurant_id"), "Основной зал", self.auth_window)
        self.stacked_widget.addWidget(self.seating_window)
        self.stacked_widget.setCurrentWidget(self.seating_window)

    def open_reviews(self):
        """Открывает окно с отзывами."""
        self.review_window = ReviewWindow(self.restaurant_info.get("restaurant_id"), self.auth_window)
        self.stacked_widget.addWidget(self.review_window)
        self.stacked_widget.setCurrentWidget(self.review_window)

    def go_to_home(self):
        self.auth_window.show()  # Показываем окно аутентификации
        self.hide()  # Скрываем текущее окно