from fastapi import FastAPI, HTTPException, Depends, Form, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import firebirdsql
import bcrypt
import logging

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

# Модель для приема данных от клиента
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
    description: Optional[str] = Field(None, description="Описание ресторана")
    restaurant_image: Optional[str] = Field(None, description="Фотография ресторана")

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

        # Проверка существования администратора
        cursor.execute("SELECT COUNT(*) FROM users WHERE LOWER(name) = 'admin' AND role = 'admin'")
        admin_count = cursor.fetchone()[0]
        if user.name.lower() == "admin" and admin_count > 0:
            raise HTTPException(status_code=400, detail="Пользователь с ролью admin уже существует")

        # Хеширование пароля
        password_hash = hash_password(user.password)

        # Создание нового пользователя с ролью user по умолчанию
        role = user.role if user.role else "user"
        if user.name.lower() == "admin":
            role = "admin"  # Присваиваем роль admin, если имя admin

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

@app.post("/restaurant/{email}/")
async def create_or_update_restaurant(
    email: str,
    name: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    cuisine_type: str = Form(...),
    description: Optional[str] = Form(None),
    restaurant_image: Optional[str] = Form(None)
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
                SET name = ?, address = ?, city = ?, cuisine_type = ?, description = ?, restaurant_image = ?
                WHERE email = ?
            """, (name, address, city, cuisine_type, description, restaurant_image, email))
        else:
            # Создание нового ресторана
            cursor.execute("SELECT GEN_ID(restaurant_id_seq, 1) FROM RDB$DATABASE")
            restaurant_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO restaurants (RESTAURANT_ID, name, address, city, cuisine_type, description, restaurant_image, email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (restaurant_id, name, address, city, cuisine_type, description, restaurant_image, email))

        conn.commit()

        return {"message": "Данные ресторана успешно сохранены"}

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при сохранении данных ресторана: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении данных ресторана")

    finally:
        cursor.close()
        conn.close()

@app.get("/restaurant/{email}/")
async def get_restaurant(email: str):
    """Маршрут для получения данных о ресторане."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Проверка существования ресторана
        cursor.execute("""
            SELECT name, address, city, cuisine_type, description, restaurant_image
            FROM restaurants
            WHERE email = ?
        """, (email,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Данные о ресторане не найдены")

        return {
            "name": result[0],
            "address": result[1],
            "city": result[2],
            "cuisine_type": result[3],
            "description": result[4],
            "restaurant_image": result[5]
        }

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при получении данных о ресторане: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении данных о ресторане")

    finally:
        cursor.close()
        conn.close()

@app.post("/restaurant/{email}/")
async def create_or_update_restaurant(
    email: str,
    name: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    cuisine_type: str = Form(...),
    description: Optional[str] = Form(None),
    restaurant_image: Optional[str] = Form(None)
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
                SET name = ?, address = ?, city = ?, cuisine_type = ?, description = ?, restaurant_image = ?
                WHERE email = ?
            """, (name, address, city, cuisine_type, description, restaurant_image, email))
        else:
            # Создание нового ресторана
            cursor.execute("SELECT GEN_ID(restaurant_id_seq, 1) FROM RDB$DATABASE")
            restaurant_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO restaurants (RESTAURANT_ID, name, address, city, cuisine_type, description, restaurant_image, email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (restaurant_id, name, address, city, cuisine_type, description, restaurant_image, email))

        conn.commit()

        return {"message": "Данные ресторана успешно сохранены"}

    except firebirdsql.Error as e:
        logger.error(f"Ошибка при сохранении данных ресторана: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении данных ресторана")

    finally:
        cursor.close()
        conn.close()
        
@app.get("/filter-restaurants/")
async def filter_restaurants(
    rating: Optional[float] = Query(None, description="Рейтинг ресторана"),
    cuisine_type: Optional[str] = Query(None, description="Тип кухни"),
    average_bill_min: Optional[float] = Query(None, description="Минимальный средний чек"),
    average_bill_max: Optional[float] = Query(None, description="Максимальный средний чек"),
    opening_hours: Optional[str] = Query(None, description="Часы работы"),
    city: Optional[str] = Query(None, description="Город")
):
    """Маршрут для фильтрации ресторанов по различным параметрам."""
    logger.debug(f"Фильтрация ресторанов с параметрами: {locals()}")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT r.name, r.address, r.city, r.cuisine_type, r.rating, r.restaurant_image, rs.opening_hours, r.description, rs.average_bill
            FROM restaurants r
            LEFT JOIN restaurant_settings rs ON r.RESTAURANT_ID = rs.restaurant_id
            WHERE 1=1
        """
        params = []

        if rating is not None:
            query += " AND r.rating = ?"
            params.append(rating)

        if cuisine_type is not None:
            query += " AND r.cuisine_type = ?"
            params.append(cuisine_type)

        if average_bill_min is not None:
            query += " AND rs.average_bill >= ?"
            params.append(average_bill_min)

        if average_bill_max is not None:
            query += " AND rs.average_bill <= ?"
            params.append(average_bill_max)

        if opening_hours is not None:
            query += " AND rs.opening_hours = ?"
            params.append(opening_hours)

        if city is not None:
            query += " AND UPPER(r.city) = ?"
            params.append(city.upper())

        cursor.execute(query, params)
        restaurants = cursor.fetchall()

        return [
            {
                "name": restaurant[0],
                "address": restaurant[1],
                "city": restaurant[2],
                "cuisine_type": restaurant[3],
                "rating": restaurant[4],
                "restaurant_image": restaurant[5],
                "opening_hours": restaurant[6],
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
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)