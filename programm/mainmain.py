import sys
from PyQt5.QtWidgets import QApplication
from auth import AuthWindow
import logging

# Настройка логгера
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Создаем AuthWindow
    auth_window = AuthWindow()
    auth_window.show()  # Показываем окно аутентификации
    logger.debug("Приложение запущено")

    # Запускаем главный цикл приложения
    sys.exit(app.exec_())