from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy, QStackedLayout, QMessageBox
)
from PyQt5.QtGui import QPalette, QColor, QFont
import requests
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        logger.debug("AuthWindow создан")  # Отладочное сообщение
        self.setWindowTitle("Аутентификация")
        self.setGeometry(100, 100, 500, 600)  # Устанавливаем начальные размеры
        self.setMaximumWidth(500)  # Ограничиваем максимальную ширину
        self.setMaximumHeight(600)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#CCFFCC"))
        self.setPalette(palette)

        self.layout = QStackedLayout(self)
        self.setLayout(self.layout)

        self.registration_form()
        self.login_form()

    def create_custom_widget(self, widget):
        widget.setStyleSheet("""
            background-color: #CCFFCC;
            color: #000000;
            padding: 10px;
            border: 2px solid #000000;
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
        self.name_label.setStyleSheet("color: #000000;")
        self.name_input = self.create_custom_widget(QLineEdit(self))

        self.email_label = QLabel("Email:")
        self.email_label.setStyleSheet("color: #000000;")
        self.email_input = self.create_custom_widget(QLineEdit(self))

        self.password_label = QLabel("Пароль:")
        self.password_label.setStyleSheet("color: #000000;")
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
        self.login_email_label.setStyleSheet("color: #000000;")
        self.login_email_input = self.create_custom_widget(QLineEdit(self))

        self.login_password_label = QLabel("Пароль:")
        self.login_password_label.setStyleSheet("color: #000000;")
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
        self.layout.setCurrentIndex(1)

    def register(self):
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

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
                response_data = response.json()
                error_message = response_data.get("detail", "Неизвестная ошибка")
                QMessageBox.warning(self, "Ошибка", error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def login(self):
        email = self.login_email_input.text()
        password = self.login_password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        url = "http://localhost:8000/login/"
        data = {"email": email, "password": password}

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                role = response.json().get("role", "user")
                QMessageBox.information(self, "Успех", f"Вы вошли как {role}!")

                # Проверяем роль пользователя
                if role == "admin":
                    from admin import AdminWindow  # Ленивый импорт
                    self.admin_window = AdminWindow(self)
                    self.admin_window.show()  # Показываем новое окно
                    self.hide()  # Скрываем окно аутентификации
                elif role == "restaurant":
                    from restaurant import RestaurantWindow  # Ленивый импорт
                    self.restaurant_window = RestaurantWindow(email, self)
                    self.restaurant_window.show()  # Показываем новое окно
                    self.hide()  # Скрываем окно аутентификации
                elif role == "user":
                    # Проверяем, есть ли у пользователя ресторан
                    restaurant_url = f"http://localhost:8000/restaurant/email/{email}/"
                    restaurant_response = requests.get(restaurant_url)
                    if restaurant_response.status_code == 200:
                        # Если ресторан существует, но роль не изменена, выводим сообщение об ошибке
                        QMessageBox.warning(self, "Ошибка", "Отсутствуют права доступа, обратитесь к администратору.")
                    else:
                        from main_menu import MainMenu  # Ленивый импорт
                        self.main_menu = MainMenu(self)
                        self.main_menu.show()  # Показываем новое окно
                        self.hide()  # Скрываем окно аутентификации
                else:
                    QMessageBox.warning(self, "Ошибка", "Неизвестная роль пользователя.")
            else:
                response_data = response.json()
                error_message = response_data.get("detail", "Неизвестная ошибка")
                QMessageBox.warning(self, "Ошибка", error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")