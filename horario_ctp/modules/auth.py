import streamlit as st
import hashlib
from core.exceptions import AuthError
from modules.database import get_db

def hash_password(password: str) -> str:
    """Encripta la contraseña con SHA-256 y salting"""
    salt = "ctp_las_palmitas_salt_2023"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def register_user(username: str, password: str, full_name: str, role: str = "student", email: str = None):
    """Registra un nuevo usuario en la base de datos"""
    if not username or not password:
        raise AuthError("Usuario y contraseña son obligatorios")

    if len(password) < 6:
        raise AuthError("La contraseña debe tener al menos 6 caracteres")

    with get_db() as conn:
        cursor = conn.cursor()

        # Verificar si el usuario ya existe
        if cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
            raise AuthError("El usuario ya existe")

        # Insertar nuevo usuario
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, role, email) VALUES (?, ?, ?, ?, ?)",
            (username, hash_password(password), full_name, role, email)
        )
        conn.commit()

def verify_user(username: str, password: str) -> dict:
    """Autentica al usuario"""
    with get_db() as conn:
        user = conn.execute(
            "SELECT username, password_hash, role, full_name FROM users WHERE username = ?",
            (username,)
        ).fetchone()

    if not user or user["password_hash"] != hash_password(password):
        raise AuthError("Usuario o contraseña incorrectos")

    # Actualizar último login
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?",
            (username,)
        )
        conn.commit()

    return {
        "username": user["username"],
        "role": user["role"],
        "full_name": user["full_name"]
    }

def logout():
    """Cierra la sesión del usuario"""
    if "user" in st.session_state:
        del st.session_state.user
    if "auth" in st.session_state:
        del st.session_state.auth

def show_auth_form():
    """Muestra el formulario de autenticación/registro"""
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Usuario", key="login_user")
            password = st.text_input("Contraseña", type="password", key="login_pass")

            if st.form_submit_button("Ingresar"):
                try:
                    user = verify_user(username, password)
                    st.session_state.user = user
                    st.session_state.auth = True
                    st.rerun()
                except AuthError as e:
                    st.error(str(e))

    with tab2:
        with st.form("register_form"):
            st.subheader("Nuevo Registro")
            new_user = st.text_input("Nombre de usuario")
            new_pass = st.text_input("Contraseña", type="password")
            confirm_pass = st.text_input("Confirmar contraseña", type="password")
            full_name = st.text_input("Nombre completo")
            email = st.text_input("Email (opcional)")
            role = st.selectbox("Tipo de usuario", ["student", "teacher"])

            if st.form_submit_button("Registrarse"):
                try:
                    if new_pass != confirm_pass:
                        raise AuthError("Las contraseñas no coinciden")

                    register_user(new_user, new_pass, full_name, role, email)
                    st.success("¡Registro exitoso! Por favor inicia sesión")

                except AuthError as e:
                    st.error(str(e))
