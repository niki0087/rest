from fastapi import FastAPI, HTTPException, Depends, Form, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List
import firebirdsql
import bcrypt
import logging
import base64
from datetime import datetime

# Настройки подключения к базе данных Firebird
DB_HOST = "localhost"
DB_PORT = "3050"
DB_PATH = "/opt/RedDatabase/ud_kp/rest.fdb"
DB_USER = "SYSDBA"
DB_PASSWORD = "masterkey"

# Инициализация FastAPI
app = FastAPI()

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Модели для приема данных от клиента
class User(BaseModel):
    name: str
    email: str
    password: str
    role: str = None

class LoginRequest(BaseModel):
    email: str
    password: str

class AssignRoleRequest(BaseModel):
    email: str
    new_role: str
    admin_email: str

class Restaurant(BaseModel):
    name: str = Field(..., description="Название ресторана")
    address: str = Field(..., description="Адрес ресторана")
    city: str = Field(..., description="Город")
    cuisine_type: str = Field(..., description="Вид кухни")
    phone_number: Optional[str] = Field(None, description="Номер телефона")
    email: Optional[str] = Field(None, description="Email ресторана")
    rating: Optional[float] = Field(None, description="Рейтинг ресторана")
    description: Optional[str] = Field(None, description="Описание ресторана")
    restaurant_image: Optional[str] = Field(None, description="Фотография ресторана")
    opening_hours: Optional[str] = Field(None, description="Часы работы")
    average_bill: Optional[float] = Field(None, description="Средний чек")

class MenuItem(BaseModel):
    name: str = Field(..., description="Название блюда")
    description: Optional[str] = Field(None, description="Описание блюда")
    price: float = Field(..., description="Цена блюда")
    photo: Optional[str] = Field(None, description="Фотография блюда")

class SeatingRequest(BaseModel):
    table_number: int = Field(..., description="Номер столика")
    capacity: int = Field(..., description="Количество мест")
    layout: str = Field(..., description="Расположение столика")

class ReservationRequest(BaseModel):
    reservation_time: str
    user_email: str
    table_number: int  # Добавляем поле table_number

def get_db_connection():
    """Функция для подключения к базе данных."""
    try:
        conn = firebirdsql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            database=DB_PATH,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='UTF8'
        )
        return conn
    except firebirdsql.Error as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        raise HTTPException(status_code=500, detail="Ошибка подключения к базе данных")

def hash_password(password: str) -> str:
    """Функция хеширования пароля."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Функция для проверки пароля."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def user_role_dependency(admin_email: str, required_role: str = "admin"):
    """Функция проверки роли администратора."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT role FROM users WHERE email = ?", (admin_email,))
        result = cursor.fetchone()
        if not result or result[0] != required_role:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    finally:
        cursor.close()
        conn.close()

def is_valid_iso_format(time_str: str) -> bool:
    """Проверяет, является ли строка валидным ISO 8601 форматом."""
    try:
        datetime.fromisoformat(time_str)
        return True
    except ValueError:
        return False

# Маршруты для работы с пользователями
@app.post("/register/")
async def register(user: User):
    """Маршрут для регистрации пользователя."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Проверка существования пользователя с тем же email
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (user.email,))
        count = cursor.fetchone()[0]
        if count > 0:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

        # Хеширование пароля
        password_hash = hash_password(user.password)

        # Создание нового пользователя с ролью user по умолчанию
        role = user.role if user.role else "user"
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       (user.name, user.email, password_hash, role))
        conn.commit()

        return {"message": "Регистрация прошла успешно!"}

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при регистрации пользователя")

    finally:
        cursor.close()
        conn.close()

@app.post("/login/")
async def login(login: LoginRequest):
    """Маршрут для входа пользователя."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Проверка наличия пользователя
        cursor.execute("SELECT password_hash, role FROM users WHERE email = ?", (login.email,))
        result = cursor.fetchone()
        if not result or not verify_password(login.password, result[0]):
            raise HTTPException(status_code=400, detail="Неправильные учетные данные")

        role = result[1]  # Получаем роль пользователя

        return {"message": "Вход выполнен успешно!", "role": role}  # Возвращаем роль пользователя

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при входе пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при входе пользователя")

    finally:
        cursor.close()
        conn.close()

@app.post("/assign-role/")
async def assign_role(request: AssignRoleRequest):
    """Маршрут для назначения роли пользователю администратором."""
    # Проверка, что запрос делает администратор
    user_role_dependency(request.admin_email, 'admin')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Проверка существования пользователя
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (request.email,))
        count = cursor.fetchone()[0]
        if count == 0:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обновление роли пользователя
        cursor.execute("UPDATE users SET role = ? WHERE email = ?", (request.new_role, request.email))

        # Если роль "ресторан", создаем запись в таблице ресторанов
        if request.new_role == "restaurant":
            # Проверка существования ресторана для данного пользователя
            cursor.execute("SELECT COUNT(*) FROM restaurants WHERE email = ?", (request.email,))
            restaurant_exists = cursor.fetchone()[0]
            if not restaurant_exists:
                # Генерация уникального идентификатора для ресторана
                cursor.execute("SELECT GEN_ID(restaurant_id_seq, 1) FROM RDB$DATABASE")
                restaurant_id = cursor.fetchone()[0]
                # Заполнение обязательных полей
                name = "Новый ресторан"
                address = "Адрес не указан"
                city = "Город не указан"
                cuisine_type = "Кухня не указана"
                cursor.execute("""
                    INSERT INTO restaurants (RESTAURANT_ID, name, address, city, cuisine_type, email)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (restaurant_id, name, address, city, cuisine_type, request.email))

        conn.commit()

        return {"message": f"Роль пользователя {request.email} успешно обновлена на {request.new_role}"}

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при назначении роли: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при назначении роли")

    finally:
        cursor.close()
        conn.close()

@app.get("/users/")
async def get_users(admin_email: str):
    """Маршрут для получения списка всех пользователей."""
    user_role_dependency(admin_email, 'admin')  # Проверка прав администратора

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name, email, role FROM users")
        users = cursor.fetchall()
        return [{"name": user[0], "email": user[1], "role": user[2]} for user in users]

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при получении списка пользователей: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении списка пользователей")

    finally:
        cursor.close()
        conn.close()

@app.delete("/users/{email}/")
async def delete_user(email: str, admin_email: str):
    """Маршрут для удаления пользователя администратором."""
    user_role_dependency(admin_email, 'admin')  # Проверка прав администратора

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Проверка существования пользователя
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
        count = cursor.fetchone()[0]
        if count == 0:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Удаление пользователя
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()

        return {"message": f"Пользователь {email} успешно удален"}

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при удалении пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при удалении пользователя")

    finally:
        cursor.close()
        conn.close()

# Маршруты для работы с ресторанами
@app.post("/restaurant/{email}/")
async def create_or_update_restaurant(
    email: str,
    name: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    cuisine_type: str = Form(...),
    phone_number: Optional[str] = Form(None),
    rating: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    restaurant_image: Optional[str] = Form(None),
    opening_hours: Optional[str] = Form(None),
    average_bill: Optional[float] = Form(None)
):
    """Маршрут для создания или обновления ресторана."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Проверка существования пользователя
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
        count = cursor.fetchone()[0]
        if count == 0:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Проверка существования ресторана
        cursor.execute("SELECT RESTAURANT_ID FROM restaurants WHERE email = ?", (email,))
        result = cursor.fetchone()
        restaurant_id = result[0] if result else None

        if restaurant_id:
            # Обновление ресторана
            cursor.execute("""
                UPDATE restaurants
                SET name = ?, address = ?, city = ?, cuisine_type = ?, phone_number = ?, rating = ?, description = ?, restaurant_image = ?, opening_hours = ?, average_bill = ?
                WHERE email = ?
            """, (name, address, city, cuisine_type, phone_number, rating, description, restaurant_image, opening_hours, average_bill, email))
        else:
            # Создание нового ресторана
            cursor.execute("SELECT GEN_ID(restaurant_id_seq, 1) FROM RDB$DATABASE")
            restaurant_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO restaurants (RESTAURANT_ID, name, address, city, cuisine_type, phone_number, email, rating, description, restaurant_image, opening_hours, average_bill)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (restaurant_id, name, address, city, cuisine_type, phone_number, email, rating, description, restaurant_image, opening_hours, average_bill))

        conn.commit()

        return {"message": "Данные ресторана успешно сохранены"}

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при сохранении данных ресторана: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении данных ресторана")

    finally:
        cursor.close()
        conn.close()

@app.get("/restaurant/{restaurant_id}/")
async def get_restaurant(restaurant_id: int):
    """Маршрут для получения данных о ресторане по его ID."""
    if not restaurant_id:  # Проверяем, что restaurant_id не пустой
        raise HTTPException(status_code=400, detail="ID ресторана не указан.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Проверка существования ресторана
        cursor.execute("""
            SELECT RESTAURANT_ID, NAME, ADDRESS, CITY, CUISINE_TYPE, PHONE_NUMBER, EMAIL, RATING, DESCRIPTION, RESTAURANT_IMAGE, OPENING_HOURS, AVERAGE_BILL
            FROM restaurants
            WHERE RESTAURANT_ID = ?
        """, (restaurant_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Данные о ресторане не найдены")

        # Логируем данные из таблицы restaurants
        logger.debug(f"Fetched restaurant data: {result}")

        return {
            "restaurant_id": result[0],
            "name": result[1],
            "address": result[2],
            "city": result[3],
            "cuisine_type": result[4],
            "phone_number": result[5],
            "email": result[6],
            "rating": result[7],
            "description": result[8],
            "restaurant_image": result[9],
            "opening_hours": result[10],
            "average_bill": result[11]
        }

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при получении данных о ресторане: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении данных о ресторане")

    finally:
        cursor.close()
        conn.close()
                        
@app.get("/filter-restaurants/")
async def filter_restaurants(
    rating: Optional[float] = Query(None, description="Рейтинг ресторана"),
    cuisine_type: Optional[str] = Query(None, description="Тип кухни"),
    average_bill_min: Optional[float] = Query(None, description="Минимальный средний чек"),
    average_bill_max: Optional[float] = Query(None, description="Максимальный средний чек"),
    city: Optional[str] = Query(None, description="Город")
):
    """Маршрут для фильтрации ресторанов по различным параметрам."""
    logger.debug(f"Фильтрация ресторанов с параметрами: {locals()}")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT RESTAURANT_ID, NAME, ADDRESS, CITY, CUISINE_TYPE, RATING, RESTAURANT_IMAGE, DESCRIPTION, AVERAGE_BILL
            FROM RESTAURANTS
            WHERE 1=1
        """
        params = []

        if rating is not None:
            query += " AND RATING = ?"
            params.append(rating)

        if cuisine_type is not None:
            query += " AND CUISINE_TYPE = ?"
            params.append(cuisine_type)

        if average_bill_min is not None:
            query += " AND AVERAGE_BILL >= ?"
            params.append(average_bill_min)

        if average_bill_max is not None:
            query += " AND AVERAGE_BILL <= ?"
            params.append(average_bill_max)

        if city is not None:
            query += " AND UPPER(CITY) = ?"
            params.append(city.upper())

        cursor.execute(query, params)
        restaurants = cursor.fetchall()

        return [
            {
                "restaurant_id": restaurant[0],
                "name": restaurant[1],
                "address": restaurant[2],
                "city": restaurant[3],
                "cuisine_type": restaurant[4],
                "rating": restaurant[5],
                "restaurant_image": restaurant[6],
                "description": restaurant[7],
                "average_bill": restaurant[8]
            }
            for restaurant in restaurants
        ]

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при фильтрации ресторанов: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при фильтрации ресторанов")

    finally:
        cursor.close()
        conn.close()

# Маршруты для работы с меню ресторана
@app.get("/menu/{restaurant_id}/")
async def get_menu(restaurant_id: int):
    """Маршрут для получения меню ресторана."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Проверка существования ресторана
        cursor.execute("SELECT RESTAURANT_ID FROM restaurants WHERE RESTAURANT_ID = ?", (restaurant_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Ресторан не найден")

        # Получение меню ресторана
        cursor.execute("""
            SELECT name, description, price, photo_menu_blob
            FROM menu
            WHERE RESTAURANT_ID = ?
        """, (restaurant_id,))
        menu = cursor.fetchall()

        return [
            {
                "name": dish[0],
                "description": dish[1],
                "price": dish[2],
                "photo": base64.b64encode(dish[3]).decode('utf-8') if dish[3] else None
            }
            for dish in menu
        ]

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при получении меню: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении меню")

    finally:
        cursor.close()
        conn.close()

@app.post("/menu/{email}/")
async def create_or_update_menu(
    email: str,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    photo: Optional[str] = Form(None)
):
    """Маршрут для создания или обновления меню ресторана."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Проверка существования ресторана
        cursor.execute("SELECT RESTAURANT_ID FROM restaurants WHERE email = ?", (email,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Ресторан не найден")

        restaurant_id = result[0]

        # Проверка существования блюда
        cursor.execute("SELECT MENU_ITEM_ID FROM menu WHERE RESTAURANT_ID = ? AND name = ?", (restaurant_id, name))
        result = cursor.fetchone()
        menu_item_id = result[0] if result else None

        if menu_item_id:
            # Обновление блюда
            cursor.execute("""
                UPDATE menu
                SET description = ?, price = ?, photo_menu_blob = ?
                WHERE MENU_ITEM_ID = ?
            """, (description, price, base64.b64decode(photo) if photo else None, menu_item_id))
        else:
            # Создание нового блюда
            cursor.execute("SELECT GEN_ID(menu_item_id_seq, 1) FROM RDB$DATABASE")
            menu_item_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO menu (MENU_ITEM_ID, RESTAURANT_ID, name, description, price, photo_menu_blob)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (menu_item_id, restaurant_id, name, description, price, base64.b64decode(photo) if photo else None))

        conn.commit()

        return {"message": "Данные меню успешно сохранены"}

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при сохранении данных меню: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении данных меню")

    finally:
        cursor.close()
        conn.close()

@app.delete("/menu/{email}/{dish_name}/")
async def delete_dish(email: str, dish_name: str):
    """Маршрут для удаления блюда из меню ресторана."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Проверка существования ресторана
        cursor.execute("SELECT RESTAURANT_ID FROM restaurants WHERE email = ?", (email,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Ресторан не найден")

        restaurant_id = result[0]

        # Удаление блюда из меню
        cursor.execute("""
            DELETE FROM menu
            WHERE RESTAURANT_ID = ? AND name = ?
        """, (restaurant_id, dish_name))
        conn.commit()

        return {"message": "Блюдо успешно удалено из меню"}

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при удалении блюда: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при удалении блюда")

    finally:
        cursor.close()
        conn.close()

# Маршруты для работы с бронированием столиков
@app.post("/seating/{email}/")
async def create_seating(email: str, seating: SeatingRequest):
    """Маршрут для добавления столика."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT RESTAURANT_ID FROM restaurants WHERE email = ?", (email,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Ресторан не найден")

        restaurant_id = result[0]

        # Проверка данных
        if seating.table_number <= 0 or seating.capacity <= 0:
            raise HTTPException(status_code=422, detail="Номер столика и количество мест должны быть положительными числами.")

        cursor.execute("SELECT GEN_ID(seating_chart_id_seq, 1) FROM RDB$DATABASE")
        seating_chart_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO SEATING_CHARTS (SEATING_CHART_ID, RESTAURANT_ID, TABLE_NUMBER, CAPACITY, LAYOUT)
            VALUES (?, ?, ?, ?, ?)
        """, (seating_chart_id, restaurant_id, seating.table_number, seating.capacity, seating.layout))

        conn.commit()

        return {"message": "Столик успешно добавлен"}

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при добавлении столика: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при добавлении столика")

    finally:
        cursor.close()
        conn.close()

@app.delete("/seating/{email}/{table_number}/")
async def delete_seating(email: str, table_number: int):
    """Маршрут для удаления столика."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT RESTAURANT_ID FROM restaurants WHERE email = ?", (email,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Ресторан не найден")

        restaurant_id = result[0]

        cursor.execute("""
            DELETE FROM SEATING_CHARTS
            WHERE RESTAURANT_ID = ? AND TABLE_NUMBER = ?
        """, (restaurant_id, table_number))

        conn.commit()

        return {"message": "Столик успешно удален"}

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при удалении столика: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при удалении столика")

    finally:
        cursor.close()
        conn.close()

@app.get("/seating/{restaurant_id}/{layout_name}/")
async def get_seating(restaurant_id: int, layout_name: str):
    """Маршрут для получения информации о столиках."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Запрос к базе данных для получения данных о столиках
        cursor.execute("""
            SELECT SEATING_CHART_ID, TABLE_NUMBER, CAPACITY
            FROM SEATING_CHARTS
            WHERE RESTAURANT_ID = ? AND LAYOUT = ?
        """, (restaurant_id, layout_name))
        seating_data = cursor.fetchall()

        # Преобразуем данные в формат JSON
        seating_list = [
            {
                "seating_chart_id": row[0],
                "table_number": row[1],
                "capacity": row[2]
            }
            for row in seating_data
        ]

        return seating_list
    except firebirdsql.Error as e:
        logger.error(f"Ошибка при получении данных о столиках: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении данных о столиках")
    finally:
        cursor.close()
        conn.close()

@app.post("/seating/{restaurant_id}/reserve/")
async def reserve_table(restaurant_id: int, request: ReservationRequest):
    """Маршрут для бронирования столика."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Проверка формата времени
        if not is_valid_iso_format(request.reservation_time):
            raise HTTPException(status_code=400, detail="Неверный формат времени бронирования. Ожидается ISO 8601.")

        # Получение ID пользователя
        cursor.execute("SELECT USER_ID FROM users WHERE email = ?", (request.user_email,))
        user_id = cursor.fetchone()
        if not user_id:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user_id = user_id[0]

        # Проверка наличия столика
        cursor.execute("""
            SELECT SEATING_CHART_ID, TABLE_NUMBER, CAPACITY, LAYOUT
            FROM SEATING_CHARTS
            WHERE RESTAURANT_ID = ? AND TABLE_NUMBER = ?
        """, (restaurant_id, request.table_number))
        table_data = cursor.fetchone()
        if not table_data:
            raise HTTPException(status_code=404, detail="Столик не найден")

        seating_chart_id, table_number, capacity, layout = table_data

        # Преобразуем время бронирования в объект datetime
        reservation_time = datetime.fromisoformat(request.reservation_time)

        # Проверка, что столик не забронирован на указанную дату
        cursor.execute("""
            SELECT COUNT(*) 
            FROM SEATING_CHARTS 
            WHERE RESTAURANT_ID = ? AND TABLE_NUMBER = ? AND CAST(RESERVATION_TIME AS DATE) = ?
        """, (restaurant_id, table_number, reservation_time.date()))
        count = cursor.fetchone()[0]
        if count > 0:
            raise HTTPException(status_code=400, detail="Столик уже забронирован на эту дату")

        # Генерация уникального идентификатора для брони
        cursor.execute("SELECT GEN_ID(seating_chart_id_seq, 1) FROM RDB$DATABASE")
        new_seating_chart_id = cursor.fetchone()[0]

        # Добавление записи о брони в таблицу SEATING_CHARTS
        cursor.execute("""
            INSERT INTO SEATING_CHARTS (SEATING_CHART_ID, RESTAURANT_ID, TABLE_NUMBER, CAPACITY, LAYOUT, USER_ID, RESERVATION_TIME)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (new_seating_chart_id, restaurant_id, table_number, capacity, layout, user_id, reservation_time))
        conn.commit()

        return {"message": "Столик успешно забронирован"}
    except HTTPException as http_exc:
        # Если ошибка уже обработана, просто пробрасываем её дальше
        raise http_exc
    except firebirdsql.Error as fb_error:
        # Обработка ошибок Firebird
        logger.error(f"Ошибка Firebird при бронировании столика: {fb_error}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных при бронировании столика")
    except Exception as e:
        # Обработка других исключений
        logger.error(f"Неизвестная ошибка при бронировании столика: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка при бронировании столика. Пожалуйста, попробуйте позже.")
    finally:
        cursor.close()
        conn.close()

@app.get("/reservations/")
async def get_reservations(user_email: str):
    """Маршрут для получения бронирований пользователя."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT TABLE_NUMBER, RESERVATION_TIME
            FROM SEATING_CHARTS
            WHERE USER_ID = (SELECT USER_ID FROM users WHERE email = ?)
        """, (user_email,))
        reservations = cursor.fetchall()
        return [{"table_number": res[0], "reservation_time": res[1].isoformat()} for res in reservations]
    except firebirdsql.Error as e:
        logger.error(f"Ошибка при получении бронирований: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении бронирований")
    finally:
        cursor.close()
        conn.close()

@app.post("/reviews/{restaurant_id}/")
async def create_review(restaurant_id: int, request: dict):
    """Маршрут для создания отзыва."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Получение обязательных полей
        rating = request.get("rating")
        comment = request.get("comment")
        created_at = request.get("created_at")
        user_email = request.get("user_email")

        # Проверка, что все обязательные поля переданы
        if not rating or not comment or not created_at or not user_email:
            raise HTTPException(status_code=400, detail="Не все обязательные поля переданы")

        # Проверка, что рейтинг находится в допустимом диапазоне (1-5)
        if not (1 <= rating <= 5):
            raise HTTPException(status_code=400, detail="Рейтинг должен быть в диапазоне от 1 до 5")

        # Проверка, что время в правильном формате
        try:
            created_at_datetime = datetime.fromisoformat(created_at)
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат времени. Ожидается ISO 8601")

        # Получение ID пользователя
        cursor.execute("SELECT USER_ID FROM users WHERE email = ?", (user_email,))
        user_id = cursor.fetchone()
        if not user_id:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user_id = user_id[0]

        # Генерация уникального идентификатора для отзыва
        cursor.execute("SELECT GEN_ID(review_id_seq, 1) FROM RDB$DATABASE")
        review_id = cursor.fetchone()[0]

        # Добавление отзыва в базу данных
        cursor.execute("""
            INSERT INTO REVIEWS (REVIEW_ID, USER_ID, RESTAURANT_ID, RATING, COMMENT, CREATED_AT)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (review_id, user_id, restaurant_id, rating, comment, created_at_datetime))

        # Расчет нового среднего рейтинга для ресторана
        cursor.execute("""
            SELECT AVG(RATING) FROM REVIEWS WHERE RESTAURANT_ID = ?
        """, (restaurant_id,))
        avg_rating = cursor.fetchone()[0]

        # Обновление рейтинга ресторана
        cursor.execute("""
            UPDATE RESTAURANTS SET RATING = ? WHERE RESTAURANT_ID = ?
        """, (avg_rating, restaurant_id))

        conn.commit()

        return {"message": "Отзыв успешно добавлен", "new_rating": avg_rating}
    except HTTPException as http_exc:
        # Если ошибка уже обработана, просто пробрасываем её дальше
        raise http_exc
    except firebirdsql.Error as fb_error:
        # Обработка ошибок Firebird
        logger.error(f"Ошибка Firebird при добавлении отзыва: {fb_error}")
        raise HTTPException(status_code=500, detail="Ошибка базы данных при добавлении отзыва")
    except Exception as e:
        # Обработка других исключений
        logger.error(f"Неизвестная ошибка при добавлении отзыва: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка при добавлении отзыва. Пожалуйста, попробуйте позже.")
    finally:
        cursor.close()
        conn.close()
                
@app.get("/reviews/{restaurant_id}/")
async def get_reviews(restaurant_id: int):
    """Маршрут для получения отзывов ресторана."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT RATING, COMMENT, CREATED_AT
            FROM REVIEWS
            WHERE RESTAURANT_ID = ?
        """, (restaurant_id,))
        reviews = cursor.fetchall()
        return [{"rating": review[0], "comment": review[1], "created_at": review[2].isoformat()} for review in reviews]
    except firebirdsql.Error as e:
        logger.error(f"Ошибка при получении отзывов: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении отзывов")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)