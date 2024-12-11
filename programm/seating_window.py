from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QInputDialog, QCalendarWidget, QTimeEdit, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QDateTime
import requests
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

class SeatingWindow(QWidget):
    def __init__(self, restaurant_id, layout_name, auth_window):
        super().__init__()
        self.restaurant_id = restaurant_id
        self.layout_name = layout_name
        self.auth_window = auth_window
        self.setWindowTitle(f"Свободные столики - {layout_name}")
        self.setGeometry(100, 100, 800, 600)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#CCFFCC"))
        self.setPalette(palette)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.load_seating()

    def load_seating(self):
        """Загрузка информации о столиках из базы данных."""
        url = f"http://localhost:8000/seating/{self.restaurant_id}/{self.layout_name}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                seating_data = response.json()
                self.display_seating(seating_data)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные о столиках.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def display_seating(self, seating_data):
        """Отображение столиков на экране."""
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        for table in seating_data:
            table_button = QPushButton(f"Столик {table['table_number']} ({table['capacity']} мест)")
            table_button.setStyleSheet(
                "background-color: green;" if table['status'] is None else "background-color: red;"
            )
            table_button.clicked.connect(lambda _, t=table: self.reserve_table(t))
            self.layout.addWidget(table_button)

        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.close)
        self.layout.addWidget(back_button)

    def reserve_table(self, table):
        """Обработка бронирования столика."""
        if table['status'] is not None:
            QMessageBox.warning(self, "Ошибка", "Этот столик уже забронирован.")
            return

        dialog = ReservationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            reservation_time = dialog.get_reservation_time()
            self.send_reservation_request(table['table_number'], reservation_time)

    def send_reservation_request(self, table_number, reservation_time):
        """Отправка запроса на бронирование столика."""
        url = f"http://localhost:8000/seating/{self.restaurant_id}/{table_number}/"
        data = {
            "reservation_time": reservation_time.toString(Qt.ISODate),  # ISO 8601
            "user_email": self.auth_window.login_email_input.text()
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Столик успешно забронирован.")
                self.load_seating()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось забронировать столик: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

class ReservationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Бронирование столика")
        self.setGeometry(200, 200, 400, 200)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.calendar = QCalendarWidget(self)
        self.layout.addWidget(self.calendar)

        self.time_edit = QTimeEdit(self)
        self.time_edit.setDisplayFormat("HH:mm")
        self.layout.addWidget(self.time_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)

    def get_reservation_time(self):
        """Получение выбранного времени бронирования."""
        date = self.calendar.selectedDate()
        time = self.time_edit.time()
        return QDateTime(date, time)