from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QInputDialog, QCalendarWidget, QTimeEdit, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QDateTime, QDate, QTime
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
        self.selected_table_number = None  # Инициализация переменной для хранения номера столика
        self.table_buttons = {}  # Словарь для хранения кнопок столиков
        self.setWindowTitle(f"Свободные столики - {layout_name}")
        self.setGeometry(100, 100, 500, 600)  # Устанавливаем начальные размеры
        self.setMaximumWidth(500)  # Ограничиваем максимальную ширину   

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
        # Очищаем текущий макет
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Создаем словарь для хранения кнопок столиков
        self.table_buttons = {}

        for table in seating_data:
            table_number = table['table_number']
            capacity = table['capacity']

            # Проверяем, существует ли уже кнопка для этого столика
            if table_number not in self.table_buttons:
                # Создаем новую кнопку для столика
                table_button = QPushButton(f"Столик {table_number} ({capacity} мест)")
                table_button.setStyleSheet("background-color: green;")  # Все столики свободны
                table_button.clicked.connect(lambda _, t=table: self.reserve_table(t))
                self.table_buttons[table_number] = table_button
                self.layout.addWidget(table_button)
            else:
                # Обновляем текст и состояние существующей кнопки
                table_button = self.table_buttons[table_number]
                table_button.setText(f"Столик {table_number} ({capacity} мест)")
                table_button.setStyleSheet("background-color: green;")  # Все столики свободны

        # Добавляем кнопку "Назад"
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.close)
        self.layout.addWidget(back_button)

    def reserve_table(self, table):
        """Обработка бронирования столика."""
        self.selected_table_number = table['table_number']  # Сохраняем номер столика
        dialog = ReservationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            reservation_time = dialog.get_reservation_time()
            if reservation_time <= QDateTime.currentDateTime():
                QMessageBox.warning(self, "Ошибка", "Вы не можете забронировать столик на прошедшее время.")
                return
            self.send_reservation_request(table['seating_chart_id'], reservation_time)

    def send_reservation_request(self, seating_chart_id, reservation_time):
        """Отправка запроса на бронирование столика."""
        url = f"http://localhost:8000/seating/{self.restaurant_id}/reserve/"
        data = {
            "seating_chart_id": seating_chart_id,
            "reservation_time": reservation_time.toString(Qt.ISODate),  # ISO 8601
            "user_email": self.auth_window.login_email_input.text(),
            "table_number": self.selected_table_number  # Добавляем номер столика
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Столик успешно забронирован.")
                # Обновляем состояние кнопки для забронированного столика
                if self.selected_table_number in self.table_buttons:
                    table_button = self.table_buttons[self.selected_table_number]
                    table_button.setText(f"Столик {self.selected_table_number} (ЗАНЯТ)")
                    table_button.setStyleSheet("background-color: red;")  # Столик занят
                self.load_seating()
            else:
                # Извлекаем сообщение об ошибке из ответа сервера
                error_message = response.json().get("detail", "Неизвестная ошибка")
                QMessageBox.warning(self, "Ошибка", error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

class ReservationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Бронирование столика")
        self.setGeometry(100, 100, 500, 600)  # Устанавливаем начальные размеры
        self.setMaximumWidth(500)  # Ограничиваем максимальную ширину
        self.setMaximumHeight(600)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.calendar = QCalendarWidget(self)
        self.calendar.setMinimumDate(QDate.currentDate())  # Устанавливаем минимальную дату на текущую дату
        self.layout.addWidget(self.calendar)

        self.time_edit = QTimeEdit(self)
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setMinimumTime(QTime.currentTime().addSecs(60))  # Устанавливаем минимальное время на текущее время + 1 минута
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