from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QTextEdit, QFileDialog,
    QHBoxLayout, QListWidget, QListWidgetItem, QInputDialog, QStackedWidget
)
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt
import requests
import logging
from menu_editor import MenuEditorScreen  # Импорт нового класса
from auth import AuthWindow  # Импорт класса AuthWindow

# Настройка логгера
logger = logging.getLogger(__name__)

class RestaurantWindow(QWidget):
    def __init__(self, user_email, auth_window):
        super().__init__()
        self.auth_window = auth_window  # Сохраняем ссылку на окно аутентификации
        logger.debug("RestaurantWindow создан")
        self.setWindowTitle("Окно ресторана")
        self.setGeometry(100, 100, 500, 600)  # Устанавливаем начальные размеры
        self.setMaximumWidth(500)  # Ограничиваем максимальную ширину        
        
        self.user_email = user_email

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#CCFFCC"))
        self.setPalette(palette)

        # Основной макет
        self.layout = QVBoxLayout()

        # Создаем QStackedWidget для переключения между экранами
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Добавляем главный экран
        self.main_screen = self.create_main_screen()
        self.stacked_widget.addWidget(self.main_screen)

        # Добавляем экран редактирования посадки
        self.seating_editor_screen = self.create_seating_editor_screen()
        self.stacked_widget.addWidget(self.seating_editor_screen)

        # Добавляем экран редактирования столиков
        self.table_editor_screen = self.create_table_editor_screen()
        self.stacked_widget.addWidget(self.table_editor_screen)

        # Добавляем экран броней
        self.reservations_screen = self.create_reservations_screen()
        self.stacked_widget.addWidget(self.reservations_screen)

        # Добавляем экран редактора меню
        self.menu_editor_screen = MenuEditorScreen(self.user_email, parent=self)
        self.stacked_widget.addWidget(self.menu_editor_screen)

        self.setLayout(self.layout)

        self.load_restaurant()

    def create_custom_widget(self, widget):
        """Создает виджет с единообразным стилем."""
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

    def create_main_screen(self):
        """Создает главный экран с информацией о ресторане."""
        screen = QWidget()
        layout = QVBoxLayout()

        self.name_label = QLabel("Название ресторана:")
        self.name_label.setStyleSheet("color: #000000;")
        self.name_input = self.create_custom_widget(QLineEdit(self))

        self.address_label = QLabel("Адрес ресторана:")
        self.address_label.setStyleSheet("color: #000000;")
        self.address_input = self.create_custom_widget(QLineEdit(self))

        self.city_label = QLabel("Город:")
        self.city_label.setStyleSheet("color: #000000;")
        self.city_input = self.create_custom_widget(QLineEdit(self))

        self.cuisine_label = QLabel("Вид кухни:")
        self.cuisine_label.setStyleSheet("color: #000000;")
        self.cuisine_combo = self.create_custom_widget(QComboBox(self))
        self.cuisine_combo.addItems(["Итальянская", "Японская", "Китайская", "Русская", "Другая"])

        self.description_label = QLabel("Описание ресторана:")
        self.description_label.setStyleSheet("color: #000000;")
        self.description_input = self.create_custom_widget(QTextEdit(self))

        self.photo_label = QLabel("Фотография ресторана:")
        self.photo_label.setStyleSheet("color: #000000;")
        self.photo_input = self.create_custom_widget(QLineEdit(self))
        self.photo_button = self.create_custom_widget(QPushButton("Выбрать фото", self))
        self.photo_button.clicked.connect(self.select_photo)  # Подключаем метод select_photo

        self.average_bill_label = QLabel("Средний чек:")
        self.average_bill_label.setStyleSheet("color: #000000;")
        self.average_bill_input = self.create_custom_widget(QLineEdit(self))

        self.phone_number_label = QLabel("Номер телефона:")
        self.phone_number_label.setStyleSheet("color: #000000;")
        self.phone_number_input = self.create_custom_widget(QLineEdit(self))

        self.opening_hours_label = QLabel("Часы работы:")
        self.opening_hours_label.setStyleSheet("color: #000000;")
        self.opening_hours_input = self.create_custom_widget(QLineEdit(self))

        self.save_button = self.create_custom_widget(QPushButton("Сохранить", self))
        self.save_button.clicked.connect(self.save_restaurant)

        self.menu_button = self.create_custom_widget(QPushButton("Редактировать меню", self))
        self.menu_button.clicked.connect(self.open_menu_editor)

        self.seating_button = self.create_custom_widget(QPushButton("Редактировать посадку", self))
        self.seating_button.clicked.connect(self.open_seating_editor)

        # Кнопка "Посмотреть брони"
        self.reservations_button = self.create_custom_widget(QPushButton("Посмотреть брони", self))
        self.reservations_button.clicked.connect(self.open_reservations_screen)
        layout.addWidget(self.reservations_button)

        # Кнопка "На главную"
        self.home_button = self.create_custom_widget(QPushButton("На главную", self))
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

        layout.addWidget(self.average_bill_label)
        layout.addWidget(self.average_bill_input)

        layout.addWidget(self.phone_number_label)
        layout.addWidget(self.phone_number_input)

        layout.addWidget(self.opening_hours_label)
        layout.addWidget(self.opening_hours_input)

        layout.addWidget(self.save_button)
        layout.addWidget(self.menu_button)
        layout.addWidget(self.seating_button)

        screen.setLayout(layout)
        return screen

    def create_seating_editor_screen(self):
        """Создает экран редактирования посадки."""
        screen = QWidget()
        layout = QVBoxLayout()

        self.main_hall_button = self.create_custom_widget(QPushButton("Основной зал", self))
        self.main_hall_button.clicked.connect(lambda: self.open_table_editor("Основной зал"))
        layout.addWidget(self.main_hall_button)

        self.veranda_button = self.create_custom_widget(QPushButton("Веранда", self))
        self.veranda_button.clicked.connect(lambda: self.open_table_editor("Веранда"))
        layout.addWidget(self.veranda_button)

        self.second_hall_button = self.create_custom_widget(QPushButton("Второй зал", self))
        self.second_hall_button.clicked.connect(lambda: self.open_table_editor("Второй зал"))
        layout.addWidget(self.second_hall_button)

        self.back_button = self.create_custom_widget(QPushButton("Назад", self))
        self.back_button.clicked.connect(self.go_back_to_main)
        layout.addWidget(self.back_button)

        screen.setLayout(layout)
        return screen

    def create_table_editor_screen(self):
        """Создает экран редактирования столиков."""
        screen = QWidget()
        layout = QVBoxLayout()

        self.add_table_button = self.create_custom_widget(QPushButton("Добавить столик", self))
        self.add_table_button.clicked.connect(self.add_table)
        layout.addWidget(self.add_table_button)

        self.save_button = self.create_custom_widget(QPushButton("Сохранить", self))
        self.save_button.clicked.connect(self.save_tables)
        layout.addWidget(self.save_button)

        self.delete_table_button = self.create_custom_widget(QPushButton("Удалить столик", self))
        self.delete_table_button.clicked.connect(self.delete_table)
        layout.addWidget(self.delete_table_button)

        self.back_button = self.create_custom_widget(QPushButton("Назад", self))
        self.back_button.clicked.connect(self.go_back_to_seating)
        layout.addWidget(self.back_button)

        screen.setLayout(layout)
        return screen

    def create_reservations_screen(self):
        """Создает экран для отображения всех броней ресторана."""
        screen = QWidget()
        layout = QVBoxLayout()

        self.reservations_list = QListWidget()
        self.reservations_list.itemClicked.connect(self.enable_delete_button)  # Подключаем обработчик выбора брони
        layout.addWidget(self.reservations_list)

        self.load_reservations_button = self.create_custom_widget(QPushButton("Загрузить брони", self))
        self.load_reservations_button.clicked.connect(self.load_restaurant_reservations)
        layout.addWidget(self.load_reservations_button)

        # Кнопка "Удалить бронь"
        self.delete_reservation_button = self.create_custom_widget(QPushButton("Удалить бронь", self))
        self.delete_reservation_button.setEnabled(False)  # Кнопка изначально отключена
        self.delete_reservation_button.clicked.connect(self.delete_selected_reservation)
        layout.addWidget(self.delete_reservation_button)

        self.back_button = self.create_custom_widget(QPushButton("Назад", self))
        self.back_button.clicked.connect(self.go_back_to_main)
        layout.addWidget(self.back_button)

        screen.setLayout(layout)
        return screen

    def select_photo(self):
        """Открывает диалоговое окно для выбора файла изображения."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбрать фото", "", "Images (*.png *.xpm *.jpg)")
        if file_name:
            self.photo_input.setText(file_name)

    def load_restaurant(self):
        url = f"http://localhost:8000/restaurant/email/{self.user_email}/"
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
                self.average_bill_input.setText(str(restaurant.get("average_bill", "")))
                self.phone_number_input.setText(restaurant.get("phone_number", ""))
                self.opening_hours_input.setText(restaurant.get("opening_hours", ""))
            else:
                response_data = response.json()
                error_message = response_data.get("detail", "Не удалось загрузить данные ресторана.")
                QMessageBox.warning(self, "Ошибка", error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def save_restaurant(self):
        name = self.name_input.text()
        address = self.address_input.text()
        city = self.city_input.text()
        cuisine_type = self.cuisine_combo.currentText()
        description = self.description_input.toPlainText()
        restaurant_image = self.photo_input.text()
        average_bill = self.average_bill_input.text()
        phone_number = self.phone_number_input.text()
        opening_hours = self.opening_hours_input.text()

        if not name or not address or not city or not cuisine_type:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните обязательные поля.")
            return

        data = {
            "name": name,
            "address": address,
            "city": city,
            "cuisine_type": cuisine_type,
            "description": description,
            "restaurant_image": restaurant_image,
            "average_bill": float(average_bill) if average_bill else None,
            "phone_number": phone_number,
            "opening_hours": opening_hours
        }

        url = f"http://localhost:8000/restaurant/{self.user_email}/"
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Данные ресторана успешно сохранены.")
            else:
                response_data = response.json()
                error_message = response_data.get("detail", "Не удалось сохранить данные ресторана.")
                QMessageBox.warning(self, "Ошибка", error_message)
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

        # Переключение на экран редактора меню
        self.menu_editor_screen.menu = menu
        self.menu_editor_screen.display_menu()
        self.stacked_widget.setCurrentWidget(self.menu_editor_screen)

    def open_seating_editor(self):
        """Переключает на экран редактирования посадки."""
        self.stacked_widget.setCurrentWidget(self.seating_editor_screen)

    def open_table_editor(self, layout_name):
        """Переключает на экран редактирования столиков."""
        self.current_layout = layout_name
        self.stacked_widget.setCurrentWidget(self.table_editor_screen)

    def open_reservations_screen(self):
        """Переключает на экран броней."""
        self.stacked_widget.setCurrentWidget(self.reservations_screen)

    def add_table(self):
        table_number, ok = QInputDialog.getInt(self, "Добавить столик", "Номер столика:")
        if ok:
            capacity, ok = QInputDialog.getInt(self, "Добавить столик", "Количество мест:")
            if ok:
                self.save_table(table_number, capacity)

    def save_table(self, table_number, capacity):
        url = f"http://localhost:8000/seating/{self.user_email}/"
        data = {
            "table_number": table_number,
            "capacity": capacity,
            "layout": self.current_layout
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Столик успешно добавлен.")
            else:
                response_data = response.json()
                error_message = response_data.get("detail", "Не удалось добавить столик.")
                QMessageBox.warning(self, "Ошибка", error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def delete_table(self):
        table_number, ok = QInputDialog.getInt(self, "Удалить столик", "Номер столика:")
        if ok:
            url = f"http://localhost:8000/seating/{self.user_email}/{table_number}/"
            try:
                response = requests.delete(url)
                if response.status_code == 200:
                    QMessageBox.information(self, "Успех", "Столик успешно удален.")
                else:
                    response_data = response.json()
                    error_message = response_data.get("detail", "Не удалось удалить столик.")
                    QMessageBox.warning(self, "Ошибка", error_message)
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def save_tables(self):
        QMessageBox.information(self, "Успех", "Изменения сохранены.")

    def go_back_to_main(self):
        """Возвращает на главный экран."""
        self.stacked_widget.setCurrentWidget(self.main_screen)

    def go_back_to_seating(self):
        """Возвращает на экран редактирования посадки."""
        self.stacked_widget.setCurrentWidget(self.seating_editor_screen)

    def go_to_home(self):
        if self.auth_window:
            logger.debug(f"Состояние окна аутентификации: isVisible={self.auth_window.isVisible()}, isWidgetType={self.auth_window.isWidgetType()}, parent={self.auth_window.parent()}")
            if not self.auth_window.isVisible():
                logger.debug("Окно аутентификации было скрыто, показываем его снова.")
                self.auth_window.show()
            else:
                logger.debug("Окно аутентификации уже видимо.")
            self.hide()
        else:
            logger.error("self.auth_window не существует")
            QMessageBox.warning(self, "Ошибка", "Окно аутентификации не найдено.")
            # Создаем новое окно аутентификации
            self.auth_window = AuthWindow()
            self.auth_window.show()

    def get_restaurant_id(self):
        url = f"http://localhost:8000/restaurant/email/{self.user_email}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                restaurant = response.json()
                return restaurant.get("restaurant_id")
            else:
                response_data = response.json()
                error_message = response_data.get("detail", "Не удалось загрузить данные ресторана.")
                QMessageBox.warning(self, "Ошибка", error_message)
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
                response_data = response.json()
                error_message = response_data.get("detail", "Не удалось загрузить меню ресторана.")
                QMessageBox.warning(self, "Ошибка", error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")
        return []

    def load_restaurant_reservations(self):
        """Загружает все брони для текущего ресторана."""
        restaurant_id = self.get_restaurant_id()  # Получаем restaurant_id по email
        if not restaurant_id:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить идентификатор ресторана.")
            return

        url = f"http://localhost:8000/restaurant/{restaurant_id}/reservations/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                reservations = response.json()
                self.display_reservations(reservations)
            else:
                response_data = response.json()
                error_message = response_data.get("detail", "Не удалось загрузить брони.")
                QMessageBox.warning(self, "Ошибка", error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")

    def display_reservations(self, reservations):
        """Отображает список броней в интерфейсе."""
        self.reservations_list.clear()
        for reservation in reservations:
            item = QListWidgetItem(f"Столик {reservation['table_number']} на {reservation['reservation_time']}")
            item.setData(Qt.UserRole, reservation['seating_chart_id'])  # Сохраняем seating_chart_id в данных элемента
            self.reservations_list.addItem(item)

    def enable_delete_button(self, item):
        """Активирует кнопку 'Удалить бронь' после выбора брони."""
        self.delete_reservation_button.setEnabled(True)

    def delete_selected_reservation(self):
        """Удаляет выбранную бронь."""
        selected_item = self.reservations_list.currentItem()
        if selected_item:
            seating_chart_id = selected_item.data(Qt.UserRole)  # Получаем seating_chart_id из данных элемента
            restaurant_id = self.get_restaurant_id()

            if not restaurant_id:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить идентификатор ресторана.")
                return

            url = f"http://localhost:8000/restaurant/{restaurant_id}/reservations/{seating_chart_id}/"
            try:
                response = requests.delete(url, params={"user_email": self.user_email})
                if response.status_code == 200:
                    QMessageBox.information(self, "Успех", "Бронь успешно удалена.")
                    self.load_restaurant_reservations()  # Обновляем список бронирований
                else:
                    response_data = response.json()
                    error_message = response_data.get("detail", "Не удалось удалить бронь.")
                    QMessageBox.warning(self, "Ошибка", error_message)
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка соединения: {e}")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите бронь для удаления.")