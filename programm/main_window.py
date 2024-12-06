import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGridLayout, QListWidget, QComboBox, QLineEdit, QLabel, QMessageBox, QListWidgetItem, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect, QSizePolicy, QStackedWidget)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QTimer, QEasingCurve, QSize
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon, QPixmap, QPainter, QBrush, QPen
import requests
from restaurant_details import RestaurantDetailsWindow  # Импорт нового класса

def get_image_path(image_name):
    return os.path.join(os.path.dirname(__file__), "img", image_name)

class RestaurantButton(QPushButton):
    def __init__(self, restaurant_info, main_menu_instance):
        super().__init__()
        self.restaurant_info = restaurant_info
        self.main_menu_instance = main_menu_instance
        self.setFixedHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
                border-radius: 15px;
            }
            QPushButton::hover {
                opacity: 0.8;
            }
        """)
        self.set_background_image(get_image_path(restaurant_info.get("restaurant_image", "")))
        self.set_text_overlay()
        self.clicked.connect(self.open_restaurant_details)  # Подключение сигнала нажатия кнопки

    def set_background_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.setIcon(QIcon(pixmap))
            self.setIconSize(QSize(self.width(), 200))

    def set_text_overlay(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        layout.setContentsMargins(10, 10, 10, 10)

        name_label = QLabel(self.restaurant_info.get("name", ""))
        name_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(name_label)

        rating_label = QLabel(f"Рейтинг: {self.restaurant_info.get('rating', 'N/A')}")
        rating_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(rating_label)

        opening_hours_label = QLabel(f"Часы работы: {self.restaurant_info.get('opening_hours', 'N/A')}")
        opening_hours_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(opening_hours_label)

        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("background-color: rgba(0, 0, 0, 100); border-radius: 10px;")

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(container)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_background_image(get_image_path(self.restaurant_info.get("restaurant_image", "")))

    def open_restaurant_details(self):
        self.details_window = RestaurantDetailsWindow(self.restaurant_info)
        self.details_window.show()

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Основное меню")
        self.setGeometry(100, 100, 800, 600)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        main_layout = QVBoxLayout()

        self.filter_button = QPushButton()
        self.filter_button.setIcon(QIcon(get_image_path("filter-list-svgrepo-com1.svg")))
        self.filter_button.setStyleSheet("""
            background-color: #001100;
            color: #009900;
            border: 2px solid #009900;
            border-radius: 10px;
            padding: 5px;
            min-width: 50px;
            min-height: 50px;
        """)
        self.filter_button.clicked.connect(self.toggle_filter_menu)

        main_layout.addWidget(self.filter_button, alignment=Qt.AlignTop | Qt.AlignRight)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.home_button = QPushButton("На главную")
        self.home_button.clicked.connect(self.go_to_home)
        main_layout.addWidget(self.home_button)

        self.setLayout(main_layout)

        self.create_filter_menu()
        self.create_restaurant_layout()

        self.filter_restaurants()
        self.is_filter_menu_open = False  # Добавляем флаг для отслеживания состояния меню фильтров

    def create_filter_menu(self):
        self.filter_menu = QWidget(self)
        self.filter_menu.setStyleSheet("""
            background-color: #001100;
            color: #009900;
            border: 2px solid #009900;
            border-radius: 10px;
            padding: 10px;
        """)
        self.filter_menu.setGeometry(0, 0, self.width(), int(self.height() * 0.6))
        self.filter_menu.hide()

        filter_layout = QGridLayout()

        custom_widget_style = """
            background-color: #001100;
            color: #009900;
            padding: 10px;
            border: 2px solid #009900;
            border-radius: 20px;
        """

        self.rating_label = QLabel("Рейтинг:")
        self.rating_label.setStyleSheet("color: #009900;")
        self.rating_combo = QComboBox()
        self.rating_combo.setStyleSheet(custom_widget_style)
        self.rating_combo.addItems(["Рейтинг", "1.0", "2.0", "3.0", "4.0", "5.0"])
        self.rating_combo.activated.connect(self.filter_restaurants)
        filter_layout.addWidget(self.rating_label, 0, 0)
        filter_layout.addWidget(self.rating_combo, 0, 1)

        self.cuisine_type_label = QLabel("Тип кухни:")
        self.cuisine_type_label.setStyleSheet("color: #009900;")
        self.cuisine_type_combo = QComboBox()
        self.cuisine_type_combo.setStyleSheet(custom_widget_style)
        self.cuisine_type_combo.addItems(["Тип кухни", "Итальянская", "Японская", "Китайская", "Русская", "Другая"])
        self.cuisine_type_combo.activated.connect(self.filter_restaurants)
        filter_layout.addWidget(self.cuisine_type_label, 1, 0)
        filter_layout.addWidget(self.cuisine_type_combo, 1, 1)

        self.average_bill_label = QLabel("Средний чек:")
        self.average_bill_label.setStyleSheet("color: #009900;")
        self.average_bill_combo = QComboBox()
        self.average_bill_combo.setStyleSheet(custom_widget_style)
        self.average_bill_combo.addItems(["Средний чек", "От 0 до 1000", "От 1000 до 2000", "От 2000 до 3000"])
        self.average_bill_combo.activated.connect(self.filter_restaurants)
        filter_layout.addWidget(self.average_bill_label, 2, 0)
        filter_layout.addWidget(self.average_bill_combo, 2, 1)

        self.city_label = QLabel("Город:")
        self.city_label.setStyleSheet("color: #009900;")
        self.city_input = QLineEdit()
        self.city_input.setStyleSheet(custom_widget_style)
        self.city_input.textChanged.connect(self.filter_restaurants)
        filter_layout.addWidget(self.city_label, 3, 0)
        filter_layout.addWidget(self.city_input, 3, 1)

        self.filter_menu.setLayout(filter_layout)

        self.filter_animation = QPropertyAnimation(self.filter_menu, b"geometry")
        self.filter_animation.setDuration(600)
        self.filter_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def create_restaurant_layout(self):
        self.restaurant_layout = QVBoxLayout()
        self.restaurant_widget = QWidget()
        self.restaurant_widget.setLayout(self.restaurant_layout)
        self.stacked_widget.addWidget(self.restaurant_widget)

    def toggle_filter_menu(self):
        if self.is_filter_menu_open:
            self.filter_animation.setStartValue(self.filter_menu.geometry())
            self.filter_animation.setEndValue(QRect(
                self.filter_menu.x(),
                self.filter_menu.y(),
                self.filter_menu.width(),
                0
            ))
            self.filter_animation.start()
            QTimer.singleShot(600, self.filter_menu.hide)
            self.stacked_widget.setCurrentIndex(0)
        else:
            self.filter_menu.show()
            self.filter_menu.raise_()  # Поднять список фильтров на вершину иерархии

            start_y = self.filter_button.geometry().bottom()
            filter_height = int(self.height() * 0.6)

            self.filter_animation.setStartValue(QRect(
                0,
                start_y,
                self.width(),
                0
            ))

            self.filter_animation.setEndValue(QRect(
                0,
                start_y,
                self.width(),
                filter_height
            ))
            self.filter_animation.start()
            self.stacked_widget.setCurrentIndex(1)

        self.is_filter_menu_open = not self.is_filter_menu_open

    def filter_restaurants(self):
        self.rating_filter = self.rating_combo.currentText() if self.rating_combo.currentText() != "Рейтинг" else None
        self.cuisine_type_filter = self.cuisine_type_combo.currentText() if self.cuisine_type_combo.currentText() != "Тип кухни" else None
        self.average_bill_filter = self.average_bill_combo.currentText() if self.average_bill_combo.currentText() != "Средний чек" else None
        self.city_filter = self.city_input.text().upper() if self.city_input.text() else None

        params = {
            "rating": self.rating_filter,
            "cuisine_type": self.cuisine_type_filter,
            "average_bill": self.average_bill_filter,
            "city": self.city_filter,
        }

        url = "http://localhost:8000/filter-restaurants/"
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                restaurants = response.json()
                self.display_restaurants(restaurants)
                self.is_filter_menu_open = False
                self.toggle_filter_menu()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить данные о ресторанах.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def display_restaurants(self, restaurants):
        for i in reversed(range(self.restaurant_layout.count())):
            self.restaurant_layout.itemAt(i).widget().setParent(None)

        for restaurant in restaurants:
            button = RestaurantButton(restaurant, self)
            self.restaurant_layout.addWidget(button)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.filter_menu.setGeometry(0, 0, self.width(), int(self.height() * 0.6))
        for i in range(self.restaurant_layout.count()):
            button = self.restaurant_layout.itemAt(i).widget()
            button.setFixedWidth(int(self.width() * 0.75))

    def go_to_home(self):
        from auth import AuthWindow
        self.auth_window = AuthWindow()
        self.auth_window.show()
        self.close()