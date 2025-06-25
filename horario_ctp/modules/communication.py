import streamlit as st
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta # type: ignore
import requests
import json # type: ignore

# Configuración de la base de datos
DB_PATH = Path("data/communication.db")

def init_db():
    """Inicializa la base de datos para el módulo de comunicación"""
    os.makedirs(DB_PATH.parent, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabla de contactos
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabla de recordatorios
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            message TEXT NOT NULL,
            scheduled_time TIMESTAMP,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        )
    ''')

    conn.commit()
    conn.close()

def show_whatsapp_setup_guide():
    """Muestra la guía de configuración de WhatsApp Business API"""
    st.markdown("""
    ## 📱 Guía de Configuración de WhatsApp Business API

    ### 1. Crear cuenta en Meta Business Suite
    1. Ve a [business.facebook.com](https://business.facebook.com)
    2. Haz clic en "Crear cuenta"
    3. Sigue el proceso de verificación de tu negocio
    4. Acepta los términos y condiciones

    ### 2. Configurar WhatsApp Business
    1. En Meta Business Suite, ve a "Configuración" > "WhatsApp"
    2. Haz clic en "Configurar WhatsApp"
    3. Selecciona "WhatsApp Business API"
    4. Sigue el proceso de verificación del número de teléfono

    ### 3. Obtener credenciales
    1. Ve a [developers.facebook.com](https://developers.facebook.com)
    2. Crea una nueva aplicación
    3. En la sección "WhatsApp", obtén:
       - Token de acceso (API Token)
       - ID del número de teléfono (Phone Number ID)

    ### 4. Configurar el archivo secrets.toml
    1. Crea el archivo `.streamlit/secrets.toml`
    2. Agrega las siguientes líneas:
    ```toml
    [whatsapp]
    api_token = "tu_token_aqui"
    phone_number_id = "tu_phone_number_id"
    ```

    ### 5. Verificar la configuración
    1. Reinicia la aplicación
    2. Ve a la sección de WhatsApp
    3. Intenta enviar un mensaje de prueba

    ### 📝 Notas importantes:
    - El número de teléfono debe estar en formato internacional sin el "+" (ej: 506xxxxxxxx)
    - Los mensajes deben cumplir con las políticas de WhatsApp
    - Hay límites en el número de mensajes que puedes enviar
    - Los usuarios deben optar por recibir mensajes

    ### 🔒 Seguridad
    - Nunca compartas tu API Token
    - Mantén actualizado el archivo secrets.toml
    - Usa variables de entorno en producción
    """)

def send_whatsapp_message(phone, message):
    """Envía un mensaje usando la API de WhatsApp Business"""
    try:
        # Obtener credenciales de la API
        api_token = st.secrets["whatsapp"]["api_token"]
        phone_number_id = st.secrets["whatsapp"]["phone_number_id"]

        # URL de la API de WhatsApp
        url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"

        # Headers para la petición
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        # Datos del mensaje
        data = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message}
        }

        # Enviar mensaje
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return True, "Mensaje enviado correctamente"
        else:
            return False, f"Error al enviar mensaje: {response.text}"

    except Exception as e:
        return False, f"Error al enviar mensaje: {str(e)}"

def add_contact(name, phone, role):
    """Agrega un nuevo contacto a la base de datos"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO contacts (name, phone, role) VALUES (?, ?, ?)",
            (name, phone, role)
        )
        conn.commit()
        conn.close()
        return True, "Contacto agregado correctamente"
    except sqlite3.IntegrityError:
        return False, "El número de teléfono ya existe"
    except Exception as e:
        return False, f"Error al agregar contacto: {str(e)}"

def schedule_reminder(contact_id, message, scheduled_time):
    """Programa un recordatorio"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO reminders (contact_id, message, scheduled_time) VALUES (?, ?, ?)",
            (contact_id, message, scheduled_time)
        )
        conn.commit()
        conn.close()
        return True, "Recordatorio programado correctamente"
    except Exception as e:
        return False, f"Error al programar recordatorio: {str(e)}"

def get_contacts():
    """Obtiene la lista de contactos de la base de datos"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, name, phone, role FROM contacts")
        contacts = c.fetchall()
        conn.close()
        return contacts
    except Exception as e:
        st.error(f"Error al obtener contactos: {str(e)}")
        return []

def show_messages_tab():
    """Muestra la pestaña de envío de mensajes"""
    # Verificar configuración
    if "whatsapp" not in st.secrets:
        st.error("⚠️ Configuración de WhatsApp no encontrada")
        st.info("Por favor, ve a la pestaña 'Configuración' para configurar WhatsApp Business API")
        return

    # Inicializar la base de datos
    init_db()

    # Gestión de contactos
    with st.expander("👥 Gestión de Contactos"):
        st.subheader("Agregar nuevo contacto")
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Nombre")
        with col2:
            phone = st.text_input("Teléfono (formato: 506xxxxxxxx)")
        with col3:
            role = st.selectbox("Rol", ["Estudiante", "Padre", "Profesor"])

        if st.button("➕ Agregar Contacto"):
            if name and phone and role:
                success, message = add_contact(name, phone, role)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Por favor complete todos los campos")

    # Envío de mensajes
    st.subheader("Enviar mensaje")
    contact = st.selectbox(
        "Seleccionar contacto",
        ["Nuevo número"] + [f"{row[1]} ({row[2]})" for row in get_contacts()]
    )

    if contact == "Nuevo número":
        phone = st.text_input("Número de teléfono (formato: 506xxxxxxxx)")
    else:
        phone = contact.split("(")[1].strip(")")

    message_type = st.selectbox(
        "Tipo de mensaje",
        [
            "Tarea pendiente",
            "Recordatorio de ruta",
            "Recordatorio médico",
            "Mensaje personalizado"
        ]
    )

    if message_type == "Tarea pendiente":
        col1, col2 = st.columns(2)
        with col1:
            subject = st.text_input("Materia")
        with col2:
            due_date = st.date_input("Fecha de entrega")
        message = f"📌 Tarea pendiente: {subject}, para el {due_date.strftime('%d/%m/%Y')}"

    elif message_type == "Recordatorio de ruta":
        col1, col2 = st.columns(2)
        with col1:
            route = st.text_input("Número de ruta")
        with col2:
            time = st.time_input("Hora")
        message = f"🚌 Ruta #{route} pasará a las {time.strftime('%H:%M')}"

    elif message_type == "Recordatorio médico":
        col1, col2 = st.columns(2)
        with col1:
            medicine = st.text_input("Medicamento")
        with col2:
            time = st.time_input("Hora")
        message = f"💊 Recuerda tomar {medicine} a las {time.strftime('%H:%M')}"

    else:
        message = st.text_area("Mensaje personalizado")

    # Mostrar vista previa del mensaje
    st.subheader("Vista previa del mensaje")
    st.info(message)

    # Programar o enviar inmediatamente
    send_option = st.radio(
        "¿Cuándo enviar el mensaje?",
        ["Enviar ahora", "Programar para más tarde"]
    )

    if send_option == "Programar para más tarde":
        date = st.date_input("Fecha de envío")
        time = st.time_input("Hora de envío")
        scheduled_time = datetime.combine(date, time)

        if st.button("📅 Programar mensaje"):
            success, msg = schedule_reminder(1, message, scheduled_time)
            if success:
                st.success(msg)
            else:
                st.error(msg)
    else:
        if st.button("📤 Enviar mensaje"):
            success, msg = send_whatsapp_message(phone, message)
            if success:
                st.success(msg)
            else:
                st.error(msg)

def show_config_tab():
    """Muestra la pestaña de configuración"""
    st.subheader("Configuración de WhatsApp Business API")

    # Sección de credenciales
    st.markdown("### 🔑 Credenciales de WhatsApp")
    st.markdown("Ingresa tus credenciales de WhatsApp Business API:")

    # Campos para las credenciales
    api_token = st.text_input("API Token", type="password", help="Token de acceso de WhatsApp Business API")
    phone_number_id = st.text_input("Phone Number ID", help="ID del número de teléfono de WhatsApp Business")

    # Botón para guardar configuración
    if st.button("💾 Guardar Configuración"):
        if api_token and phone_number_id:
            # Crear el directorio .streamlit si no existe
            os.makedirs(".streamlit", exist_ok=True)

            # Crear o actualizar el archivo secrets.toml
            secrets_content = f"""[whatsapp]
api_token = "{api_token}"
phone_number_id = "{phone_number_id}"
"""
            try:
                with open(".streamlit/secrets.toml", "w") as f:
                    f.write(secrets_content)
                st.success("✅ Configuración guardada correctamente")
                st.info("Por favor, reinicia la aplicación para que los cambios surtan efecto")
            except Exception as e:
                st.error(f"❌ Error al guardar la configuración: {str(e)}")
        else:
            st.warning("⚠️ Por favor, completa todos los campos")

    # Separador
    st.markdown("---")

    # Guía de configuración
    st.markdown("### 📱 Guía de Configuración")
    st.markdown("""
    #### 1. Crear cuenta en Meta Business Suite
    1. Ve a [business.facebook.com](https://business.facebook.com)
    2. Haz clic en "Crear cuenta"
    3. Sigue el proceso de verificación de tu negocio
    4. Acepta los términos y condiciones

    #### 2. Configurar WhatsApp Business
    1. En Meta Business Suite, ve a "Configuración" > "WhatsApp"
    2. Haz clic en "Configurar WhatsApp"
    3. Selecciona "WhatsApp Business API"
    4. Sigue el proceso de verificación del número de teléfono

    #### 3. Obtener credenciales
    1. Ve a [developers.facebook.com](https://developers.facebook.com)
    2. Crea una nueva aplicación
    3. En la sección "WhatsApp", obtén:
       - Token de acceso (API Token)
       - ID del número de teléfono (Phone Number ID)

    #### 📝 Notas importantes:
    - El número de teléfono debe estar en formato internacional sin el "+" (ej: 506xxxxxxxx)
    - Los mensajes deben cumplir con las políticas de WhatsApp
    - Hay límites en el número de mensajes que puedes enviar
    - Los usuarios deben optar por recibir mensajes

    #### 🔒 Seguridad
    - Nunca compartas tu API Token
    - Mantén tus credenciales seguras
    - Usa variables de entorno en producción
    """)

def generate_communication_view():
    """Genera la vista principal del módulo de comunicación"""
    st.title("🤖 Bot de WhatsApp")

    # Pestañas para diferentes secciones
    tab1, tab2 = st.tabs(["📤 Enviar Mensajes", "⚙️ Configuración"])

    with tab1:
        show_messages_tab()

    with tab2:
        show_config_tab()
