from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox, QListWidget, QListWidgetItem, QHBoxLayout, QComboBox
)
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QDateTime
import requests
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

class ReviewWindow(QWidget):
    def __init__(self, restaurant_id, auth_window):
        super().__init__()
        self.restaurant_id = restaurant_id
        self.auth_window = auth_window
        logger.debug("ReviewWindow создан")
        self.setWindowTitle("Отзывы и рейтинг")
        self.setGeometry(100, 100, 800, 600)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#CCFFCC"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Рейтинг
        self.rating_label = QLabel("Рейтинг (от 1 до 5):")
        self.rating_label.setStyleSheet("color: #000000;")
        self.rating_combo = QComboBox()
        self.rating_combo.addItems(["1", "2", "3", "4", "5"])
        layout.addWidget(self.rating_label)
        layout.addWidget(self.rating_combo)

        # Комментарий
        self.comment_label = QLabel("Комментарий:")
        self.comment_label.setStyleSheet("color: #000000;")
        self.comment_input = QTextEdit()
        layout.addWidget(self.comment_label)
        layout.addWidget(self.comment_input)

        # Кнопка для отправки отзыва
        self.submit_button = QPushButton("Отправить отзыв")
        self.submit_button.clicked.connect(self.submit_review)
        layout.addWidget(self.submit_button)

        # Список отзывов
        self.reviews_label = QLabel("Отзывы:")
        self.reviews_label.setStyleSheet("color: #000000;")
        self.reviews_list = QListWidget()
        self.reviews_list.itemClicked.connect(self.show_delete_button)  # Подключаем обработчик клика
        layout.addWidget(self.reviews_label)
        layout.addWidget(self.reviews_list)

        # Кнопка "На главную"
        self.home_button = QPushButton("На главную")
        self.home_button.clicked.connect(self.go_to_home)
        layout.addWidget(self.home_button)

        self.setLayout(layout)

        self.load_reviews()

    def submit_review(self):
        rating = self.rating_combo.currentText()
        comment = self.comment_input.toPlainText()

        if not comment:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните комментарий.")
            return

        url = f"http://localhost:8000/reviews/{self.restaurant_id}/"
        data = {
            "rating": int(rating),
            "comment": comment,
            "user_email": self.auth_window.login_email_input.text(),
            "created_at": QDateTime.currentDateTime().toString(Qt.ISODate)
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Отзыв успешно добавлен.")
                self.load_reviews()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить отзыв.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def load_reviews(self):
        url = f"http://localhost:8000/reviews/{self.restaurant_id}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                reviews = response.json()
                self.display_reviews(reviews)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить отзывы.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def display_reviews(self, reviews):
        self.reviews_list.clear()
        for review in reviews:
            item = QListWidgetItem(f"Рейтинг: {review['rating']} | {review['comment']} | {review['created_at']}")
            item.setData(Qt.UserRole, review['review_id'])  # Сохраняем review_id в данных элемента
            self.reviews_list.addItem(item)

    def show_delete_button(self, item):
        """Показывает кнопку удаления для выбранного отзыва."""
        self.delete_button = QPushButton("Удалить отзыв")
        self.delete_button.clicked.connect(lambda: self.delete_review(item))
        self.layout().addWidget(self.delete_button)

    def delete_review(self, item):
        """Удаляет выбранный отзыв."""
        review_id = item.data(Qt.UserRole)  # Получаем review_id из данных элемента
        user_email = self.auth_window.login_email_input.text()

        url = f"http://localhost:8000/reviews/{review_id}/"
        try:
            response = requests.delete(url, params={"user_email": user_email})
            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Отзыв успешно удален.")
                self.load_reviews()  # Обновляем список отзывов
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить отзыв.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def go_to_home(self):
        if self.auth_window:
            self.auth_window.show()
            self.hide()
        else:
            logger.error("self.auth_window не существует")
            QMessageBox.warning(self, "Ошибка", "Окно аутентификации не найдено.")