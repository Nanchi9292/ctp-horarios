import streamlit as st
import sqlite3
from datetime import datetime
import streamlit_authenticator as stauth
import hashlib
from core.exceptions import AuthError

DB_PATH = "data/usuarios_google.db"
USERS_DB_PATH = "data/usuarios.db"

def init_users_db():
    """Inicializa la base de datos de usuarios locales"""
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios_locales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        role TEXT DEFAULT 'student',
        created_at TEXT NOT NULL,
        last_login TEXT
    )''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Genera hash de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_local_user(username, password):
    """Verifica usuario local"""
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios_locales WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    if user and user[2] == hash_password(password):
        # Actualizar último login
        conn = sqlite3.connect(USERS_DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE usuarios_locales SET last_login = ? WHERE username = ?",
                 (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
        conn.commit()
        conn.close()

        return {
            "name": user[3],  # full_name
            "email": user[4] or f"{username}@local",  # email o username@local
            "role": user[5],  # role
            "auth_type": "local"
        }
    return None

def register_local_user(username, password, full_name, email, role="student"):
    """Registra un nuevo usuario local"""
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()

    # Verificar si el usuario ya existe
    c.execute("SELECT id FROM usuarios_locales WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        raise AuthError("El nombre de usuario ya existe")

    # Crear nuevo usuario
    password_hash = hash_password(password)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("""
        INSERT INTO usuarios_locales (username, password_hash, full_name, email, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, password_hash, full_name, email, role, created_at))

    conn.commit()
    conn.close()

def guardar_usuario_google(nombre, correo):
    """Guarda usuario de Google en la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios_google (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT NOT NULL UNIQUE,
        ultimo_acceso TEXT NOT NULL
    )''')
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("SELECT id FROM usuarios_google WHERE correo = ?", (correo,))
    if c.fetchone():
        c.execute("UPDATE usuarios_google SET ultimo_acceso = ?, nombre = ? WHERE correo = ?", (ahora, nombre, correo))
    else:
        c.execute("INSERT INTO usuarios_google (nombre, correo, ultimo_acceso) VALUES (?, ?, ?)", (nombre, correo, ahora))
    conn.commit()
    conn.close()

def get_credentials_dict():
    """Obtiene diccionario de credenciales para streamlit-authenticator"""
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, password_hash, full_name, email, role FROM usuarios_locales")
    users = c.fetchall()
    conn.close()

    credentials = {"usernames": {}}
    for user in users:
        username, password_hash, full_name, email, role = user # type: ignore
        credentials["usernames"][username] = {
            "name": full_name,
            "password": password_hash,  # streamlit-authenticator espera el hash
            "email": email or f"{username}@local"
        }

    return credentials

def hybrid_login():
    """Sistema híbrido de login: Google + Local"""
    # Inicializar bases de datos
    init_users_db()

    st.markdown("## 🔐 Iniciar Sesión")

    # Crear pestañas para los diferentes métodos de login
    tab1, tab2 = st.tabs(["🌐 Con Google", "👤 Cuenta Local"])

    with tab1:
        st.markdown("### Iniciar sesión con Google")
        st.info("Haz clic en el botón para iniciar sesión con tu cuenta de Google.")

        try:
            authenticator = stauth.Authenticate(
                credentials=get_credentials_dict(),  # Usar credenciales locales
                cookie_name="streamlit_auth",
                key="auth_google",
                use_google=True,
                google_client_id="294083815787-69m15okn2ss113u0kdija3f2s6hc7hre.apps.googleusercontent.com",
                google_client_secret="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",
                google_redirect_uri="http://localhost:8501"
            )

            # Usar el método correcto sin parámetros adicionales
            login_result = authenticator.login()

            if login_result is not None:
                name, authentication_status, username = login_result
                if authentication_status:
                    guardar_usuario_google(name, username)
                    st.session_state["user"] = {
                        "name": name,
                        "email": username,
                        "role": "user",
                        "auth_type": "google"
                    }
                    st.session_state["auth"] = True
                    st.success(f"¡Bienvenido, {name}!")
                    st.rerun()
                elif authentication_status is False:
                    st.error("Acceso denegado.")
                else:
                    st.info("Por favor, inicia sesión con tu cuenta de Google.")

        except Exception as e:
            st.error(f"Error con Google Login: {str(e)}")
            st.info("Si tienes problemas con Google, usa el login local en la otra pestaña.")

    with tab2:
        st.markdown("### Iniciar sesión con cuenta local")

        # Pestañas para login y registro
        login_tab, register_tab = st.tabs(["Ingresar", "Registrarse"])

        with login_tab:
            with st.form("local_login_form"):
                username = st.text_input("Usuario")
                password = st.text_input("Contraseña", type="password")

                if st.form_submit_button("Ingresar"):
                    if username and password:
                        user = verify_local_user(username, password)
                        if user:
                            st.session_state["user"] = user
                            st.session_state["auth"] = True
                            st.success(f"¡Bienvenido, {user['name']}!")
                            st.rerun()
                        else:
                            st.error("Usuario o contraseña incorrectos.")
                    else:
                        st.error("Por favor completa todos los campos.")

        with register_tab:
            with st.form("local_register_form"):
                st.subheader("Crear nueva cuenta")
                new_user = st.text_input("Nombre de usuario*")
                new_pass = st.text_input("Contraseña*", type="password")
                confirm_pass = st.text_input("Confirmar contraseña*", type="password")
                full_name = st.text_input("Nombre completo*")
                email = st.text_input("Email")
                role = st.selectbox("Tipo de usuario", ["student", "teacher"])

                if st.form_submit_button("Registrarse"):
                    try:
                        if not all([new_user, new_pass, confirm_pass, full_name]):
                            raise AuthError("Todos los campos marcados con * son obligatorios")
                        if new_pass != confirm_pass:
                            raise AuthError("Las contraseñas no coinciden")
                        if len(new_pass) < 6:
                            raise AuthError("La contraseña debe tener al menos 6 caracteres")

                        register_local_user(new_user, new_pass, full_name, email, role)
                        st.success("¡Registro exitoso! Ahora puedes iniciar sesión en la pestaña 'Ingresar'")

                    except AuthError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Error en el registro: {str(e)}")

def get_registered_users():
    """Obtiene lista de usuarios registrados para mostrar en admin"""
    users = []

    # Usuarios locales
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username, full_name, email, role, created_at, last_login FROM usuarios_locales")
        local_users = c.fetchall()
        conn.close()

        for user in local_users:
            users.append({
                "username": user[0],
                "name": user[1],
                "email": user[2] or f"{user[0]}@local",
                "role": user[3],
                "created": user[4],
                "last_login": user[5],
                "type": "Local"
            })
    except Exception as e:
        print(f"Error leyendo usuarios locales: {e}")

    # Usuarios de Google
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT nombre, correo, ultimo_acceso FROM usuarios_google")
        google_users = c.fetchall()
        conn.close()

        for user in google_users:
            users.append({
                "username": user[1],  # email como username
                "name": user[0],
                "email": user[1],
                "role": "user",
                "created": "N/A",
                "last_login": user[2],
                "type": "Google"
            })
    except Exception as e:
        # Si la tabla no existe, no hay usuarios de Google aún
        pass

    return users
