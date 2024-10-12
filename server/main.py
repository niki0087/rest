from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import firebirdsql
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

class LoginRequest(BaseModel):
    email: str
    password: str

class AssignRoleRequest(BaseModel):
    email: str
    new_role: str
    admin_email: str

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
        print(f"Ошибка при регистрации пользователя: {e}")
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
        print(f"Ошибка при входе пользователя: {e}")
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
        conn.commit()

        return {"message": f"Роль пользователя {request.email} успешно обновлена на {request.new_role}"}
    
    except firebirdsql.Error as e:
        print(f"Ошибка при назначении роли: {e}")
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
        print(f"Ошибка при получении списка пользователей: {e}")
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
        print(f"Ошибка при удалении пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при удалении пользователя")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
