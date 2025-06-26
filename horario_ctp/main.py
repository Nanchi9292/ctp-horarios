import streamlit as st

# Configuración de la página (DEBE ser el primer comando de Streamlit)
st.set_page_config(
    page_title="Student Calendar (Fase Beta)",
    page_icon="🏫",
    layout="wide"
)

from modules.schedule import generate_schedule_view
from modules.teachers import TeacherView
from modules.classrooms import ClassroomManager
from modules.grades import GradeManager
from modules.communication import generate_communication_view
from modules.manual import generate_manual_view
from modules.database import init_db, get_db # type: ignore
from modules.google_login import hybrid_login, get_registered_users

class MainApp:
    """Aplicación principal"""
    def __init__(self):
        self.teacher_view = TeacherView()
        self.classroom_manager = ClassroomManager()
        self.grade_manager = GradeManager()

        # Inicializar base de datos
        init_db()

    def run(self):
        """Ejecuta la aplicación"""
        # Verificar autenticación
        if "auth" not in st.session_state or not st.session_state["auth"]:
            hybrid_login()
            return

        # Barra lateral principal
        with st.sidebar:
            if "user" in st.session_state:
                user = st.session_state["user"]
                auth_type = user.get("auth_type", "local")
                auth_icon = "🌐" if auth_type == "google" else "👤"

                st.markdown(f"{auth_icon} <b>{user['name']}</b><br>{user['email']}", unsafe_allow_html=True)

            st.markdown("""
            <div style='color: #e67e22; font-size: 1.1rem; font-weight: bold; text-align: center;'>
            🚧 Student Calendar en fase beta: Puede contener errores o cambios frecuentes. 🚧
            </div>
            """, unsafe_allow_html=True)
            st.title(f"👋 ¡Hola, {st.session_state['user']['name']}!")
            st.markdown(f"**Email:** {st.session_state['user']['email']}")

            # Menú de navegación
            nav_options = {
                "📅 Horarios": "schedule",
                "👨‍🏫 Profesores": "teachers",
                "🏫 Aulas": "classrooms",
                "📊 Notas": "grades",
                "📱 Comunicación": "communication",
                "📚 Manual": "manual"
            }

            # Agregar panel de admin si el usuario es admin
            if st.session_state['user'].get('role') == 'admin':
                nav_options["⚙️ Administración"] = "admin"

            selected = st.radio("Navegación", list(nav_options.keys()))

            if st.button("🚪 Cerrar sesión"):
                for key in ["user", "auth"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        # Mostrar vista seleccionada
        if nav_options[selected] == "schedule":
            generate_schedule_view("11-1")
        elif nav_options[selected] == "teachers":
            self.teacher_view.show_view()
        elif nav_options[selected] == "classrooms":
            self.classroom_manager.show_view()
        elif nav_options[selected] == "grades":
            self.grade_manager.show_view()
        elif nav_options[selected] == "communication":
            generate_communication_view()
        elif nav_options[selected] == "manual":
            generate_manual_view()
        elif nav_options[selected] == "admin":
            self.show_admin_panel()

    def show_admin_panel(self):
        """Panel de administración"""
        if st.session_state['user'].get("role") != "admin":
            st.error("Acceso restringido a administradores")
            return

        st.title("⚙️ Panel de Administración")

        # Mostrar usuarios registrados
        st.subheader("👥 Usuarios Registrados")
        users = get_registered_users()

        if users:
            # Crear DataFrame para mostrar usuarios
            import pandas as pd
            df_data = []
            for user in users:
                df_data.append({
                    "Usuario": user["username"],
                    "Nombre": user["name"],
                    "Email": user["email"],
                    "Rol": user["role"],
                    "Tipo": user["type"],
                    "Creado": user["created"],
                    "Último Login": user["last_login"] or "Nunca"
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)

            # Estadísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Usuarios", len(users))
            with col2:
                google_users = len([u for u in users if u["type"] == "Google"])
                st.metric("Usuarios Google", google_users)
            with col3:
                local_users = len([u for u in users if u["type"] == "Local"])
                st.metric("Usuarios Locales", local_users)
        else:
            st.info("No hay usuarios registrados aún.")

if __name__ == "__main__":
    app = MainApp()
    app.run()
