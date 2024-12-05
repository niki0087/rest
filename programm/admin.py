from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QMessageBox, QInputDialog)
from PyQt5.QtGui import QPalette, QColor
import requests

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно администратора")
        self.setGeometry(100, 100, 800, 600)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        layout = QVBoxLayout()
        self.user_list = QListWidget()
        layout.addWidget(self.user_list)

        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Удалить пользователя")
        self.change_role_button = QPushButton("Изменить роль")
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.change_role_button)

        layout.addLayout(button_layout)

        self.home_button = QPushButton("На главную")
        self.home_button.clicked.connect(self.go_to_home)
        layout.addWidget(self.home_button)

        self.setLayout(layout)

        self.load_users()

        self.delete_button.clicked.connect(self.delete_user)
        self.change_role_button.clicked.connect(self.change_user_role)

    def load_users(self):
        url = "http://localhost:8000/users/"
        admin_email = "bogatovnikita04@gmail.com"
        params = {"admin_email": admin_email}
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                users = response.json()
                for user in users:
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
            admin_email = "bogatovnikita04@gmail.com"
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

            new_role, ok = QInputDialog.getText(self, "Изменение роли", "Введите новую роль (user/restaurant):")
            if ok and new_role:
                url = f"http://localhost:8000/assign-role/"
                data = {"email": user_email, "new_role": new_role, "admin_email": "bogatovnikita04@gmail.com"}
                try:
                    response = requests.post(url, json=data)
                    if response.status_code == 200:
                        QMessageBox.information(self, "Успех", "Роль пользователя изменена.")
                        self.load_users()
                    else:
                        QMessageBox.warning(self, "Ошибка", "Не удалось изменить роль пользователя.")
                except requests.exceptions.RequestException as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для изменения роли.")

    def go_to_home(self):
        from auth import AuthWindow
        self.auth_window = AuthWindow()
        self.auth_window.show()
        self.close()