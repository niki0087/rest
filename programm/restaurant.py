from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QTextEdit, QFileDialog)
from PyQt5.QtGui import QPalette, QColor, QFont
import requests
from menu_editor import MenuEditorWindow  # Импорт нового класса

class RestaurantWindow(QWidget):
    def __init__(self, user_email):
        super().__init__()
        self.setWindowTitle("Окно ресторана")
        self.setGeometry(100, 100, 800, 600)
        self.user_email = user_email

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        self.name_label = QLabel("Название ресторана:")
        self.name_label.setStyleSheet("color: #009900;")
        self.name_input = self.create_custom_widget(QLineEdit(self))

        self.address_label = QLabel("Адрес ресторана:")
        self.address_label.setStyleSheet("color: #009900;")
        self.address_input = self.create_custom_widget(QLineEdit(self))

        self.city_label = QLabel("Город:")
        self.city_label.setStyleSheet("color: #009900;")
        self.city_input = self.create_custom_widget(QLineEdit(self))

        self.cuisine_label = QLabel("Вид кухни:")
        self.cuisine_label.setStyleSheet("color: #009900;")
        self.cuisine_combo = self.create_custom_widget(QComboBox(self))
        self.cuisine_combo.addItems(["Итальянская", "Японская", "Китайская", "Русская", "Другая"])

        self.description_label = QLabel("Описание ресторана:")
        self.description_label.setStyleSheet("color: #009900;")
        self.description_input = self.create_custom_widget(QTextEdit(self))

        self.photo_label = QLabel("Фотография ресторана:")
        self.photo_label.setStyleSheet("color: #009900;")
        self.photo_input = self.create_custom_widget(QLineEdit(self))
        self.photo_button = self.create_custom_widget(QPushButton("Выбрать фото", self))
        self.photo_button.clicked.connect(self.select_photo)

        self.save_button = self.create_custom_widget(QPushButton("Сохранить", self))
        self.save_button.clicked.connect(self.save_restaurant)

        self.menu_button = self.create_custom_widget(QPushButton("Редактировать меню", self))
        self.menu_button.clicked.connect(self.open_menu_editor)

        self.home_button = QPushButton("На главную")
        self.home_button.clicked.connect(self.go_to_home)
        layout.addWidget(self.home_button)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        layout.addWidget(self.address_label)
        layout.addWidget(self.address_input)

        layout.addWidget(self.city_label)
        layout.addWidget(self.city_input)

        layout.addWidget(self.cuisine_label)
        layout.addWidget(self.cuisine_combo)

        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)

        layout.addWidget(self.photo_label)
        layout.addWidget(self.photo_input)
        layout.addWidget(self.photo_button)

        layout.addWidget(self.save_button)
        layout.addWidget(self.menu_button)

        self.setLayout(layout)

        self.load_restaurant()

    def create_custom_widget(self, widget):
        widget.setStyleSheet("""
            background-color: #001100;
            color: #009900;
            padding: 10px;
            border: 2px solid #009900;
            border-radius: 20px;
        """)
        widget.setFont(QFont("Arial", 12))
        widget.setFixedHeight(40)
        return widget

    def select_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбрать фото", "", "Images (*.png *.xpm *.jpg)")
        if file_name:
            self.photo_input.setText(file_name)

    def load_restaurant(self):
        url = f"http://localhost:8000/restaurant/{self.user_email}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                restaurant = response.json()
                self.name_input.setText(restaurant.get("name", ""))
                self.address_input.setText(restaurant.get("address", ""))
                self.city_input.setText(restaurant.get("city", ""))
                self.cuisine_combo.setCurrentText(restaurant.get("cuisine_type", ""))
                self.description_input.setPlainText(restaurant.get("description", ""))
                self.photo_input.setText(restaurant.get("restaurant_image", ""))
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные ресторана.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def save_restaurant(self):
        name = self.name_input.text()
        address = self.address_input.text()
        city = self.city_input.text()
        cuisine_type = self.cuisine_combo.currentText()
        description = self.description_input.toPlainText()
        restaurant_image = self.photo_input.text()

        if not name or not address or not city or not cuisine_type:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните обязательные поля.")
            return

        data = {
            "name": name,
            "address": address,
            "city": city,
            "cuisine_type": cuisine_type,
            "description": description,
            "restaurant_image": restaurant_image
        }

        url = f"http://localhost:8000/restaurant/{self.user_email}/"
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Данные ресторана успешно сохранены.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить данные ресторана: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def open_menu_editor(self):
        # Загрузка данных ресторана
        restaurant_id = self.get_restaurant_id()
        if not restaurant_id:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить идентификатор ресторана.")
            return

        # Загрузка меню ресторана
        menu = self.load_menu(restaurant_id)

        # Открытие окна редактора меню
        self.menu_editor_window = MenuEditorWindow(self.user_email, menu)
        self.menu_editor_window.show()

    def get_restaurant_id(self):
        url = f"http://localhost:8000/restaurant/{self.user_email}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                restaurant = response.json()
                return restaurant.get("restaurant_id")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные ресторана.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")
        return None

    def load_menu(self, restaurant_id):
        url = f"http://localhost:8000/menu/{restaurant_id}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                menu = response.json()
                return menu
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить меню ресторана.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")
        return []

    def go_to_home(self):
        from auth import AuthWindow
        self.auth_window = AuthWindow()
        self.auth_window.show()
        self.close()