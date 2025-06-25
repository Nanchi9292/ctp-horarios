import sqlite3
from datetime import datetime
from contextlib import contextmanager
import hashlib
from core.exceptions import AuthError
from config import Config

@contextmanager
def get_db():
    """Conexión segura a la base de datos con manejo de contexto"""
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
    try:
        yield conn
    except sqlite3.Error as e:
        conn.rollback()
        raise AuthError(f"Error de base de datos: {str(e)}")
    finally:
        conn.close()

def init_db():
    """Inicializa la base de datos con tablas necesarias"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student')),
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')

        # Tabla de clases
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                day TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                subject TEXT NOT NULL,
                teacher TEXT NOT NULL,
                classroom TEXT NOT NULL,
                created_by TEXT,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(username)
            )
        ''')

        # Insertar usuario admin por defecto (si no existe)
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                ("admin", hash_password("admin123"), "Administrador Principal", "admin")
            )
        except sqlite3.IntegrityError:
            pass

        conn.commit()

def hash_password(password: str, salt: str = "ctp_salt_2023") -> str:
    """Encripta la contraseña con SHA-256 y salt"""
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_user(username: str, password: str) -> dict:
    """Verifica las credenciales del usuario"""
    with get_db() as conn:
        user = conn.execute(
            "SELECT username, password_hash, role, full_name FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if not user or user["password_hash"] != hash_password(password):
            raise AuthError("Credenciales inválidas")

        # Actualizar último login
        conn.execute(
            "UPDATE users SET last_login = ? WHERE username = ?",
            (datetime.now(), username)
        )
        conn.commit()

        return dict(user)

def register_user(username: str, password: str, full_name: str, role: str = "student", email: str = None):
    """Registra un nuevo usuario en el sistema"""
    if len(password) < 6:
        raise AuthError("La contraseña debe tener al menos 6 caracteres")

    with get_db() as conn: # type: ignore
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, full_name, role, email) VALUES (?, ?, ?, ?, ?)",
                (username, hash_password(password), full_name, role, email)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise AuthError("El nombre de usuario ya existe")
