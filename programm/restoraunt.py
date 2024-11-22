import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QInputDialog,
                             QMessageBox, QStackedLayout, QSpacerItem, QSizePolicy, QListWidget, QHBoxLayout, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Основное меню")
        self.setGeometry(100, 100, 800, 600)

        # Устанавливаем фон окна
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Добавление метки для основного меню
        self.menu_label = QLabel("Добро пожаловать в основное меню!")
        self.menu_label.setStyleSheet("color: #009900; font-size: 24px;")
        layout.addWidget(self.menu_label)

        self.setLayout(layout)

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно администратора")
        self.setGeometry(100, 100, 800, 600)

        # Устанавливаем фон окна
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        layout = QVBoxLayout()
        self.user_list = QListWidget()
        layout.addWidget(self.user_list)

        # Добавляем кнопки для удаления и изменения роли пользователя
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Удалить пользователя")
        self.change_role_button = QPushButton("Изменить роль")
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.change_role_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Загрузка списка пользователей
        self.load_users()

        # Подключаем кнопки к функциям
        self.delete_button.clicked.connect(self.delete_user)
        self.change_role_button.clicked.connect(self.change_user_role)

    def load_users(self):
        url = "http://localhost:8000/users/"
        admin_email = "bogatovnikita04@gmail.com"  # Замените на email администратора
        params = {"admin_email": admin_email}
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                users = response.json()
                for user in users:
                    # Отображаем пользователей в QListWidget, кроме администратора
                    if user["role"] != "admin":
                        self.user_list.addItem(f"{user['name']} ({user['email']}) - {user['role']}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить список пользователей.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def delete_user(self):
        selected_user = self.user_list.currentItem()
        if selected_user:
            user_info = selected_user.text()
            user_email = user_info.split('(')[1].split(')')[0]
            url = f"http://localhost:8000/users/{user_email}/"
            admin_email = "bogatovnikita04@gmail.com"  # Замените на email администратора
            params = {"admin_email": admin_email}
            try:
                response = requests.delete(url, params=params)
                if response.status_code == 200:
                    QMessageBox.information(self, "Успех", "Пользователь успешно удален.")
                    self.user_list.takeItem(self.user_list.currentRow())
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить пользователя.")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления.")

    def change_user_role(self):
        selected_user = self.user_list.currentItem()
        if selected_user:
            user_info = selected_user.text()
            user_email = user_info.split('(')[1].split(')')[0]

            # Создаем диалог для выбора новой роли
            new_role, ok = QInputDialog.getText(self, "Изменение роли", "Введите новую роль (user/restaurant):")
            if ok and new_role:
                url = f"http://localhost:8000/assign-role/"
                data = {"email": user_email, "new_role": new_role, "admin_email": "bogatovnikita04@gmail.com"}
                try:
                    response = requests.post(url, json=data)
                    if response.status_code == 200:
                        QMessageBox.information(self, "Успех", "Роль пользователя изменена.")
                        self.load_users()  # Обновляем список пользователей
                    else:
                        QMessageBox.warning(self, "Ошибка", "Не удалось изменить роль пользователя.")
                except requests.exceptions.RequestException as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для изменения роли.")

class RestaurantWindow(QWidget):
    def __init__(self, user_email):
        super().__init__()
        self.setWindowTitle("Окно ресторана")
        self.setGeometry(100, 100, 800, 600)
        self.user_email = user_email

        # Устанавливаем фон окна
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Название ресторана
        self.name_label = QLabel("Название ресторана:")
        self.name_label.setStyleSheet("color: #009900;")
        self.name_input = self.create_custom_widget(QLineEdit(self))

        # Адрес ресторана
        self.address_label = QLabel("Адрес ресторана:")
        self.address_label.setStyleSheet("color: #009900;")
        self.address_input = self.create_custom_widget(QLineEdit(self))

        # Город
        self.city_label = QLabel("Город:")
        self.city_label.setStyleSheet("color: #009900;")
        self.city_input = self.create_custom_widget(QLineEdit(self))

        # Вид кухни
        self.cuisine_label = QLabel("Вид кухни:")
        self.cuisine_label.setStyleSheet("color: #009900;")
        self.cuisine_combo = self.create_custom_widget(QComboBox(self))
        self.cuisine_combo.addItems(["Итальянская", "Японская", "Китайская", "Русская", "Другая"])

        # Кнопка сохранения
        self.save_button = self.create_custom_widget(QPushButton("Сохранить", self))
        self.save_button.clicked.connect(self.save_restaurant)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        layout.addWidget(self.address_label)
        layout.addWidget(self.address_input)

        layout.addWidget(self.city_label)
        layout.addWidget(self.city_input)

        layout.addWidget(self.cuisine_label)
        layout.addWidget(self.cuisine_combo)

        layout.addWidget(self.save_button)

        self.setLayout(layout)

        # Загрузка данных ресторана, если он уже существует
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
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные ресторана.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def save_restaurant(self):
        name = self.name_input.text()
        address = self.address_input.text()
        city = self.city_input.text()
        cuisine_type = self.cuisine_combo.currentText()

        # Проверка на заполненность полей
        if not name or not address or not city or not cuisine_type:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните обязательные поля.")
            return

        data = {
            "name": name,
            "address": address,
            "city": city,
            "cuisine_type": cuisine_type
        }

        # Отладочный вывод для проверки данных
        print(f"Отправляем данные: {data}")

        url = f"http://localhost:8000/restaurant/{self.user_email}/"
        try:
            response = requests.post(url, data=data)

            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Данные ресторана успешно сохранены.")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить данные ресторана: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Аутентификация")
        self.setGeometry(100, 100, 800, 600)

        # Устанавливаем фон окна
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        # Используем QStackedLayout для переключения между окнами
        self.layout = QStackedLayout(self)
        self.setLayout(self.layout)

        self.registration_form()

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

    def registration_form(self):
        registration_widget = QWidget()
        layout = QVBoxLayout()

        layout.setContentsMargins(0, 75, 0, 50)

        self.name_label = QLabel("Имя:")
        self.name_label.setStyleSheet("color: #009900;")
        self.name_input = self.create_custom_widget(QLineEdit(self))

        self.email_label = QLabel("Email:")
        self.email_label.setStyleSheet("color: #009900;")
        self.email_input = self.create_custom_widget(QLineEdit(self))

        self.password_label = QLabel("Пароль:")
        self.password_label.setStyleSheet("color: #009900;")
        self.password_input = self.create_custom_widget(QLineEdit(self))
        self.password_input.setEchoMode(QLineEdit.Password)

        spacer = QSpacerItem(20, 75, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.register_button = self.create_custom_widget(QPushButton("Зарегистрироваться", self))
        self.register_button.clicked.connect(self.register)

        self.login_button = self.create_custom_widget(QPushButton("Войти", self))
        self.login_button.clicked.connect(self.show_login_form)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        layout.addItem(spacer)

        layout.addWidget(self.register_button)
        layout.addWidget(self.login_button)

        registration_widget.setLayout(layout)
        self.layout.addWidget(registration_widget)

    def login_form(self):
        login_widget = QWidget()
        layout = QVBoxLayout()

        layout.setContentsMargins(0, 75, 0, 50)

        self.login_email_label = QLabel("Email:")
        self.login_email_label.setStyleSheet("color: #009900;")
        self.login_email_input = self.create_custom_widget(QLineEdit(self))

        self.login_password_label = QLabel("Пароль:")
        self.login_password_label.setStyleSheet("color: #009900;")
        self.login_password_input = self.create_custom_widget(QLineEdit(self))
        self.login_password_input.setEchoMode(QLineEdit.Password)

        spacer = QSpacerItem(20, 75, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.login_button = self.create_custom_widget(QPushButton("Войти", self))
        self.login_button.clicked.connect(self.login)

        self.register_button = self.create_custom_widget(QPushButton("Зарегистрироваться", self))
        self.register_button.clicked.connect(self.show_registration_form)

        layout.addWidget(self.login_email_label)
        layout.addWidget(self.login_email_input)

        layout.addWidget(self.login_password_label)
        layout.addWidget(self.login_password_input)

        layout.addItem(spacer)

        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        login_widget.setLayout(layout)
        self.layout.addWidget(login_widget)

    def show_registration_form(self):
        self.layout.setCurrentIndex(0)

    def show_login_form(self):
        if not hasattr(self, 'login_email_input'):
            self.login_form()
        self.layout.setCurrentIndex(1)

    def register(self):
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

        # Проверка на заполненность полей
        if not name or not email or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        url = "http://localhost:8000/register/"
        data = {"name": name, "email": email, "password": password}

        try:
            response = requests.post(url, json=data)
            if response.status_code == 201:
                QMessageBox.information(self, "Успех", "Регистрация прошла успешно. Пожалуйста, войдите.")
                self.show_login_form()
            else:
                QMessageBox.warning(self, "Ошибка", response.text)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def login(self):
        email = self.login_email_input.text()
        password = self.login_password_input.text()

        # Проверка на заполненность полей
        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        url = "http://localhost:8000/login/"
        data = {"email": email, "password": password}

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                role = response.json().get("role", "user")  # Предполагаем, что роль пользователя возвращается в ответе
                QMessageBox.information(self, "Успех", f"Вы вошли как {role}!")
                if role == "admin":
                    self.admin_window = AdminWindow()
                    self.admin_window.show()
                elif role == "restaurant":
                    self.restaurant_window = RestaurantWindow(email)
                    self.restaurant_window.show()
                else:
                    self.main_menu = MainMenu()
                    self.main_menu.show()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", response.text)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth_window = AuthWindow()
    auth_window.show()
    sys.exit(app.exec_())