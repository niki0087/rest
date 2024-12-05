from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, QTextEdit, QScrollArea)
from PyQt5.QtGui import QPalette, QColor, QFont, QPixmap
from PyQt5.QtCore import Qt

class RestaurantDetailsWindow(QWidget):
    def __init__(self, restaurant_info):
        super().__init__()
        self.setWindowTitle(f"Детали ресторана: {restaurant_info.get('name', 'Неизвестный ресторан')}")
        self.setGeometry(100, 100, 800, 600)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#001100"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Фотография ресторана
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.set_background_image(restaurant_info.get("restaurant_image", ""))
        layout.addWidget(self.photo_label)

        # Описание ресторана
        self.description_label = QLabel("Описание:")
        self.description_label.setStyleSheet("color: #009900; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.description_label)

        self.description_text = QTextEdit()
        self.description_text.setPlainText(restaurant_info.get("description", "Описание отсутствует"))
        self.description_text.setReadOnly(True)
        self.description_text.setStyleSheet("background-color: #001100; color: #009900; border: 2px solid #009900; border-radius: 10px; padding: 10px;")
        layout.addWidget(self.description_text)

        # Средний чек
        self.average_bill_label = QLabel(f"Средний чек: {restaurant_info.get('average_bill', 'Не указан')}")
        self.average_bill_label.setStyleSheet("color: #009900; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.average_bill_label)

        # Кнопки
        button_layout = QHBoxLayout()

        self.menu_button = QPushButton("Меню")
        self.menu_button.setStyleSheet("""
            background-color: #001100;
            color: #009900;
            border: 2px solid #009900;
            border-radius: 10px;
            padding: 10px;
        """)
        self.menu_button.clicked.connect(self.open_menu)
        button_layout.addWidget(self.menu_button)

        self.tables_button = QPushButton("Свободные столики")
        self.tables_button.setStyleSheet("""
            background-color: #001100;
            color: #009900;
            border: 2px solid #009900;
            border-radius: 10px;
            padding: 10px;
        """)
        self.tables_button.clicked.connect(self.open_tables)
        button_layout.addWidget(self.tables_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def set_background_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.photo_label.setPixmap(pixmap.scaled(self.photo_label.width(), 300, Qt.KeepAspectRatio))

    def open_menu(self):
        # Логика открытия меню ресторана
        QMessageBox.information(self, "Меню", "Функционал меню будет реализован позже.")

    def open_tables(self):
        # Логика открытия свободных столиков
        QMessageBox.information(self, "Свободные столики", "Функционал свободных столиков будет реализован позже.")