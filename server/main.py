from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import firebirdsql  # Убедитесь, что импортируете firebirdsql
import bcrypt

# Настройки подключения к базе данных Firebird
DB_HOST = "localhost"
DB_PORT = "3050"
DB_PATH = "/opt/RedDatabase/ud_kp/rest.fdb"
DB_USER = "SYSDBA"
DB_PASSWORD = "masterkey"

# Инициализация FastAPI
app = FastAPI()

# Модель для приема данных от клиента
class User(BaseModel):
    name: str
    email: str
    password: str
    phone_number: str = None
    role: str = None

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
        print(f"Ошибка подключения к базе данных: {e}")
        raise HTTPException(status_code=500, detail="Ошибка подключения к базе данных")

@app.post("/register/")
async def register(user: User):
    """Маршрут для регистрации пользователя."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Проверка существования пользователя
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (user.email,))
        count = cursor.fetchone()[0]
        if count > 0:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

        # Хеширование пароля
        password_hash = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Создание нового пользователя
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                       (user.name, user.email, password_hash))
        conn.commit()

        return {"message": "Регистрация прошла успешно!"}
    
    except firebirdsql.Error as e:
        print(f"Ошибка при регистрации пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при регистрации пользователя")
    
    finally:
        cursor.close()
        conn.close()

@app.post("/login/")
async def login(user: User):
    """Маршрут для входа пользователя."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Проверка наличия пользователя
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (user.email,))
        result = cursor.fetchone()
        if not result or not bcrypt.checkpw(user.password.encode('utf-8'), result[0].encode('utf-8')):  # Хеширование пароля
            raise HTTPException(status_code=400, detail="Неправильные учетные данные")

        return {"message": "Вход выполнен успешно!"}
    
    except firebirdsql.Error as e:
        print(f"Ошибка при входе пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при входе пользователя")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
