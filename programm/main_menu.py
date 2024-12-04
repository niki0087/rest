from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGridLayout, QListWidget, QComboBox, QLineEdit, QLabel, QMessageBox, QListWidgetItem)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QTimer, QEasingCurve
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon
import requests


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Основное меню")
        self.setGeometry(100, 100, 800, 600)

        # Настройка цвета окна
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Кнопка фильтров
        self.filter_button = QPushButton()
        self.filter_button.setIcon(QIcon("/home/nikita/Загрузки/arts_for_kurs/filter-list-svgrepo-com1.svg"))
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

        layout.addWidget(self.filter_button, alignment=Qt.AlignTop | Qt.AlignRight)

        # Список ресторанов
        self.restaurant_list = QListWidget()
        self.restaurant_list.setStyleSheet("""
            background-color: #001100;
            color: #009900;
            border: 2px solid #009900;
            border-radius: 10px;
            padding: 10px;
        """)
        layout.addWidget(self.restaurant_list)

        self.setLayout(layout)

        # Фильтры
        self.rating_filter = None
        self.cuisine_type_filter = None
        self.average_bill_filter = None
        self.city_filter = None

        # Меню фильтров
        self.create_filter_menu()

        self.filter_restaurants()

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

        # Стиль виджетов
        custom_widget_style = """
            background-color: #001100;
            color: #009900;
            padding: 10px;
            border: 2px solid #009900;
            border-radius: 20px;
        """

        # Рейтинг
        self.rating_label = QLabel("Рейтинг:")
        self.rating_label.setStyleSheet("color: #009900;")
        self.rating_combo = QComboBox()
        self.rating_combo.setStyleSheet(custom_widget_style)
        self.rating_combo.addItems(["Рейтинг", "1.0", "2.0", "3.0", "4.0", "5.0"])
        self.rating_combo.activated.connect(self.filter_restaurants)
        filter_layout.addWidget(self.rating_label, 0, 0)
        filter_layout.addWidget(self.rating_combo, 0, 1)

        # Тип кухни
        self.cuisine_type_label = QLabel("Тип кухни:")
        self.cuisine_type_label.setStyleSheet("color: #009900;")
        self.cuisine_type_combo = QComboBox()
        self.cuisine_type_combo.setStyleSheet(custom_widget_style)
        self.cuisine_type_combo.addItems(["Тип кухни", "Итальянская", "Японская", "Китайская", "Русская", "Другая"])
        self.cuisine_type_combo.activated.connect(self.filter_restaurants)
        filter_layout.addWidget(self.cuisine_type_label, 1, 0)
        filter_layout.addWidget(self.cuisine_type_combo, 1, 1)

        # Средний чек
        self.average_bill_label = QLabel("Средний чек:")
        self.average_bill_label.setStyleSheet("color: #009900;")
        self.average_bill_combo = QComboBox()
        self.average_bill_combo.setStyleSheet(custom_widget_style)
        self.average_bill_combo.addItems(["Средний чек", "От 0 до 1000", "От 1000 до 2000", "От 2000 до 3000"])
        self.average_bill_combo.activated.connect(self.filter_restaurants)
        filter_layout.addWidget(self.average_bill_label, 2, 0)
        filter_layout.addWidget(self.average_bill_combo, 2, 1)

        # Город
        self.city_label = QLabel("Город:")
        self.city_label.setStyleSheet("color: #009900;")
        self.city_input = QLineEdit()
        self.city_input.setStyleSheet(custom_widget_style)
        self.city_input.textChanged.connect(self.filter_restaurants)
        filter_layout.addWidget(self.city_label, 3, 0)
        filter_layout.addWidget(self.city_input, 3, 1)

        self.filter_menu.setLayout(filter_layout)

        # Анимация фильтра
        self.filter_animation = QPropertyAnimation(self.filter_menu, b"geometry")
        self.filter_animation.setDuration(600)
        self.filter_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def toggle_filter_menu(self):
        if self.filter_menu.isVisible():
            self.filter_animation.setStartValue(self.filter_menu.geometry())
            self.filter_animation.setEndValue(QRect(
                self.filter_menu.x(),
                self.filter_menu.y(),
                self.filter_menu.width(),
                0
            ))
            self.filter_animation.start()
            QTimer.singleShot(600, self.filter_menu.hide)
        else:
            self.filter_menu.show()
            self.filter_menu.raise_()  # Убедиться, что меню отображается поверх

            start_y = self.filter_button.geometry().bottom()  # Позиция под кнопкой
            filter_height = int(self.height() * 0.6)  # Высота меню фильтров

            self.filter_animation.setStartValue(QRect(
                0,
                start_y,
                self.width(),
                0  # Начальная высота
            ))

            self.filter_animation.setEndValue(QRect(
                0,
                start_y,
                self.width(),
                filter_height  # Конечная высота
            ))
            self.filter_animation.start()

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
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить данные о ресторанах.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def display_restaurants(self, restaurants):
        self.restaurant_list.clear()
        for restaurant in restaurants:
            item = QListWidgetItem(f"{restaurant['name']} - {restaurant['cuisine_type']} - {restaurant['city']}")
            self.restaurant_list.addItem(item)

