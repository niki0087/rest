from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QHBoxLayout)
from PyQt5.QtGui import QPalette, QColor, QFont, QPixmap
from PyQt5.QtCore import Qt
import requests
import base64

class MenuEditorWindow(QWidget):
    def __init__(self, restaurant_email, menu=None):
        super().__init__()
        self.setWindowTitle("Редактор меню")
        self.setGeometry(100, 100, 800, 600)
        self.restaurant_email = restaurant_email
        self.menu = menu if menu else []

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        self.menu_list = QListWidget()
        layout.addWidget(self.menu_list)

        self.name_label = QLabel("Название блюда:")
        self.name_label.setStyleSheet("color: #009900;")
        self.name_input = self.create_custom_widget(QLineEdit(self))

        self.description_label = QLabel("Описание блюда:")
        self.description_label.setStyleSheet("color: #009900;")
        self.description_input = self.create_custom_widget(QTextEdit(self))

        self.price_label = QLabel("Цена блюда:")
        self.price_label.setStyleSheet("color: #009900;")
        self.price_input = self.create_custom_widget(QLineEdit(self))

        self.photo_label = QLabel("Фотография блюда:")
        self.photo_label.setStyleSheet("color: #009900;")
        self.photo_input = self.create_custom_widget(QLineEdit(self))
        self.photo_button = self.create_custom_widget(QPushButton("Выбрать фото", self))
        self.photo_button.clicked.connect(self.select_photo)

        button_layout = QHBoxLayout()

        self.add_button = self.create_custom_widget(QPushButton("Добавить блюдо", self))
        self.add_button.clicked.connect(self.add_dish)
        button_layout.addWidget(self.add_button)

        self.delete_button = self.create_custom_widget(QPushButton("Удалить блюдо", self))
        self.delete_button.clicked.connect(self.delete_dish)
        button_layout.addWidget(self.delete_button)

        self.save_button = self.create_custom_widget(QPushButton("Сохранить изменения", self))
        self.save_button.clicked.connect(self.save_menu)
        button_layout.addWidget(self.save_button)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)

        layout.addWidget(self.price_label)
        layout.addWidget(self.price_input)

        layout.addWidget(self.photo_label)
        layout.addWidget(self.photo_input)
        layout.addWidget(self.photo_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.display_menu()  # Отображение меню при инициализации окна

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

    def display_menu(self):
        self.menu_list.clear()
        for dish in self.menu:
            item = QListWidgetItem(f"{dish['name']} - {dish['price']} руб.")
            self.menu_list.addItem(item)

    def add_dish(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        price = self.price_input.text()
        photo_path = self.photo_input.text()

        if not name or not price:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните обязательные поля.")
            return

        # Кодирование фотографии в Base64
        photo = self.encode_photo(photo_path) if photo_path else None

        data = {
            "name": name,
            "description": description,
            "price": float(price),  # Преобразуем цену в число
            "photo": photo
        }

        url = f"http://localhost:8000/menu/{self.restaurant_email}/"
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Блюдо успешно добавлено.")
                self.load_menu()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить блюдо.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def delete_dish(self):
        selected_item = self.menu_list.currentItem()
        if selected_item:
            dish_name = selected_item.text().split(' - ')[0]
            url = f"http://localhost:8000/menu/{self.restaurant_email}/{dish_name}/"
            try:
                response = requests.delete(url)
                if response.status_code == 200:
                    QMessageBox.information(self, "Успех", "Блюдо успешно удалено.")
                    self.load_menu()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить блюдо.")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите блюдо для удаления.")

    def save_menu(self):
        QMessageBox.information(self, "Успех", "Изменения сохранены.")
        self.load_menu()  # Перезагрузка меню после сохранения

    def encode_photo(self, file_path):
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string

    def load_menu(self):
        url = f"http://localhost:8000/menu/{self.restaurant_email}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.menu = response.json()
                self.display_menu()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить меню.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")