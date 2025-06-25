import streamlit as st
import pandas as pd
import json # type: ignore
from datetime import datetime # type: ignore
import pytz # type: ignore
import base64 # type: ignore
from io import BytesIO
import sqlite3
from streamlit_tags import st_tags # type: ignore
import extra_streamlit_components as stx
from modules.exports import export_schedule_to_pdf # type: ignore

# Configuración inicial
# st.set_page_config(
#     page_title="Horario 4.0 - CTP Las Palmitas",
#     page_icon="🏫",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Constantes
TIME_SLOTS = [
    "7:00 - 7:40", "7:40 - 8:20", "8:20 - 9:00",
    "9:20 - 10:00", "10:00 - 10:40", "10:40 - 11:20",
    "12:10 - 12:50", "12:50 - 13:30", "13:30 - 14:10",
    "14:30 - 15:10", "15:10 - 15:50", "15:50 - 16:30"
]

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
GROUPS = ["7-1", "7-4", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2", "11-1", "11-2"]
SUBJECT_COLORS = {
    "Matemática": "#FFD700", "Español": "#FF6347", "Ciencias": "#7CFC00",
    "Inglés": "#1E90FF", "Sociales": "#9370DB", "Francés": "#FF69B4",
    "Religión": "#A52A2A", "Música": "#FF8C00", "Educación Física": "#008080",
    "TIC": "#4682B4", "Talleres": "#32CD32", "ALMUERZO": "#696969"
}

# Sistema de login (simplificado)
def check_login():
    if 'login' not in st.session_state:
        st.session_state.login = False
    return st.session_state.login

# Base de datos SQLite
def init_db():
    conn = sqlite3.connect('horario.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS horarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 grupo TEXT NOT NULL,
                 dia TEXT NOT NULL,
                 hora TEXT NOT NULL,
                 materia TEXT NOT NULL,
                 profesor TEXT NOT NULL,
                 aula TEXT NOT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 rol TEXT NOT NULL)''')

    # Datos de ejemplo (en producción usaría autenticación real)
    try:
        c.execute("INSERT INTO usuarios (username, password, rol) VALUES (?,?,?)",
                  ("admin", "admin123", "admin"))
    except:
        pass

    conn.commit()
    conn.close()

init_db()

# =============================================
# FUNCIONES PRINCIPALES MEJORADAS
# =============================================

def parse_class_info(class_str):
    """Analiza la información de la clase con manejo de errores"""
    if class_str in ["---", "ALMUERZO"]:
        return class_str, "", "", ""

    parts = [p.strip() for p in class_str.split(" - ")]
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2], class_str
    elif len(parts) == 2:
        return parts[0], parts[1], "", class_str
    return class_str, "", "", class_str

def get_color_for_subject(subject):
    """Asigna colores basados en la materia"""
    for key in SUBJECT_COLORS:
        if key in subject:
            return SUBJECT_COLORS[key]
    return "#F0F2F6"  # Color por defecto

def display_class_box(content, is_edit=False, key=None):
    """Muestra una caja de clase con estilo mejorado"""
    if content == "---":
        return st.markdown("<div style='border:1px dashed #ccc; padding:8px; border-radius:5px;'>Libre</div>",
                          unsafe_allow_html=True)
    elif content == "ALMUERZO":
        return st.markdown("""<div style='background-color:#696969; color:white; padding:8px;
                           border-radius:5px; text-align:center;'>🍽️ ALMUERZO</div>""",
                         unsafe_allow_html=True)

    subject, teacher, classroom, _ = parse_class_info(content)
    color = get_color_for_subject(subject)

    if is_edit:
        return st.text_area("", value=content, height=100, key=key)
    else:
        html = f"""
        <div style='background-color:{color}; padding:8px; border-radius:5px; margin:2px;'>
            <b>{subject}</b><br>
            👨‍🏫 {teacher}<br>
            🏫 {classroom}
        </div>
        """
        return st.markdown(html, unsafe_allow_html=True)

def get_all_teachers(group=None):
    """Obtiene todos los profesores"""
    if 'teachers' not in st.session_state:
        st.session_state.teachers = ["DANNY LOBO", "ERLIN CASTRO", "HAZEL CERDAS", "ERIC RODRIGUEZ"]
    return st.session_state.teachers

def add_teacher(teacher_name):
    """Agrega un nuevo profesor a la lista"""
    if teacher_name and teacher_name not in st.session_state.teachers:
        st.session_state.teachers.append(teacher_name)
        st.session_state.teachers.sort()
        return True
    return False

def remove_teacher(teacher_name):
    """Elimina un profesor de la lista"""
    if teacher_name in st.session_state.teachers:
        st.session_state.teachers.remove(teacher_name)
        return True
    return False

def get_all_groups():
    """Obtiene todos los grupos"""
    if 'groups' not in st.session_state:
        st.session_state.groups = GROUPS.copy()
    return st.session_state.groups

def add_group(group_name):
    """Agrega un nuevo grupo a la lista"""
    if group_name and group_name not in st.session_state.groups:
        st.session_state.groups.append(group_name)
        st.session_state.groups.sort()
        return True
    return False

def remove_group(group_name):
    """Elimina un grupo de la lista"""
    if group_name in st.session_state.groups:
        st.session_state.groups.remove(group_name)
        return True
    return False

def generate_schedule_view(group, edit_mode=False):
    """Genera la vista principal del horario"""
    # Inicializar el estado de edición si no existe
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # Inicializar el grupo seleccionado en el estado de la sesión
    if 'selected_group' not in st.session_state:
        st.session_state.selected_group = group

    # Selector de grupo en la parte superior
    selected_group = st.selectbox(
        "Seleccionar Grupo",
        get_all_groups(),
        index=get_all_groups().index(st.session_state.selected_group) if st.session_state.selected_group in get_all_groups() else 0
    )

    # Actualizar el grupo seleccionado en el estado de la sesión
    if selected_group != st.session_state.selected_group:
        st.session_state.selected_group = selected_group
        st.rerun()

    # Encabezado con botón de edición
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"📅 Horario Grupo {st.session_state.selected_group}")
    with col2:
        if st.button("✏️ Modo Edición" if not st.session_state.edit_mode else "👁️ Modo Visualización"):
            st.session_state.edit_mode = not st.session_state.edit_mode
            st.rerun()

    # Instrucciones para modo edición
    if st.session_state.edit_mode:
        st.info("""
        💡 **Instrucciones de Edición:**
        - Haz clic en cualquier celda para editar
        - Escribe la información en formato: **MATERIA - PROFESOR - AULA**
        - Ejemplo: `MATEMÁTICA - JUAN PÉREZ - AULA 15`
        - Los cambios se guardan automáticamente al salir del campo
        - Usa **Ctrl+Enter** para guardar rápidamente
        """)

    # Gestión de profesores y grupos
    with st.expander("👨‍🏫 Gestión de Profesores"):
        col1, col2 = st.columns(2)
        with col1:
            new_teacher = st.text_input("Nuevo profesor")
            if st.button("➕ Agregar Profesor"):
                if add_teacher(new_teacher):
                    st.success(f"✅ Profesor {new_teacher} agregado")
                    st.rerun()
                else:
                    st.error("❌ El profesor ya existe o el nombre está vacío")

        with col2:
            teacher_to_remove = st.selectbox("Seleccionar profesor a eliminar", get_all_teachers())
            if st.button("🗑️ Eliminar Profesor"):
                if remove_teacher(teacher_to_remove):
                    st.success(f"✅ Profesor {teacher_to_remove} eliminado")
                    st.rerun()
                else:
                    st.error("❌ No se pudo eliminar el profesor")

    with st.expander("👥 Gestión de Grupos"):
        col1, col2 = st.columns(2)
        with col1:
            new_group = st.text_input("Nuevo grupo")
            if st.button("➕ Agregar Grupo"):
                if add_group(new_group):
                    st.success(f"✅ Grupo {new_group} agregado")
                    st.rerun()
                else:
                    st.error("❌ El grupo ya existe o el nombre está vacío")

        with col2:
            group_to_remove = st.selectbox("Seleccionar grupo a eliminar", get_all_groups())
            if st.button("🗑️ Eliminar Grupo"):
                if remove_group(group_to_remove):
                    st.success(f"✅ Grupo {group_to_remove} eliminado")
                    st.rerun()
                else:
                    st.error("❌ No se pudo eliminar el grupo")

    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_teacher = st.selectbox("Filtrar por profesor", ["Todos"] + list(get_all_teachers()))
    with col2:
        filter_room = st.selectbox("Filtrar por aula", ["Todas"] + list(get_all_classrooms()))
    with col3:
        filter_subject = st.selectbox("Filtrar por materia", ["Todas"] + list(get_all_subjects()))

    # Crear DataFrame para exportación
    export_data = []

    # Tabla de horario
    cols = st.columns([1.2] + [1.5] * len(DAYS))

    # Mostrar mensaje de guardado si corresponde
    if st.session_state.get('horario_guardado', False):
        st.success('✅ Cambios guardados correctamente')
        del st.session_state['horario_guardado']

    # Encabezados
    with cols[0]:
        st.markdown("**⏰ Horario**")
    for i, day in enumerate(DAYS):
        with cols[i+1]:
            st.markdown(f"**{day}**")

    # Filas
    for time_idx, time_slot in enumerate(TIME_SLOTS):
        cols = st.columns([1.2] + [1.5] * len(DAYS))
        row_data = {"Hora": time_slot}

        # Columna de tiempo
        with cols[0]:
            st.markdown(f"**{time_slot}**")

        # Columnas de días
        for day_idx, day in enumerate(DAYS):
            with cols[day_idx+1]:
                class_info = get_class_info(st.session_state.selected_group, day, time_idx)
                subject, teacher, room, _ = parse_class_info(class_info)
                row_data[day] = f"{subject}\n{teacher}\n{room}"

                # Aplicar filtros
                show = True
                if filter_teacher != "Todos" and teacher != filter_teacher:
                    show = False
                if filter_room != "Todas" and room != filter_room:
                    show = False
                if filter_subject != "Todas" and subject != filter_subject:
                    show = False

                if show:
                    if st.session_state.edit_mode:
                        # Crear clave única para cada campo de edición
                        edit_key = f"edit_{st.session_state.selected_group}_{day}_{time_idx}"

                        # Campo de texto con botón de guardado rápido
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            new_value = st.text_area(
                                f"{st.session_state.selected_group}_{day}_{time_idx}",
                                value=class_info,
                                height=100,
                                key=edit_key,
                                label_visibility="collapsed",
                                placeholder="MATERIA - PROFESOR - AULA"
                            )
                        with col2:
                            if st.button("💾", key=f"save_{edit_key}", help="Guardar cambios"):
                                if new_value != class_info:
                                    update_class_info(st.session_state.selected_group, day, time_idx, new_value)
                                    st.success("✅ Cambios guardados")
                                    st.rerun()
                    else:
                        display_class_box(class_info)
                else:
                    st.empty()

        export_data.append(row_data)

    # Exportar a Excel
    if st.button("📥 Exportar a Excel"):
        df = pd.DataFrame(export_data)
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        excel_data = buffer.getvalue()
        st.download_button(
            "📥 Descargar Excel",
            excel_data,
            f"horario_{st.session_state.selected_group}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# =============================================
# NUEVAS FUNCIONALIDADES IMPLEMENTADAS
# =============================================

def teacher_view():
    """Vista especial para profesores (datos reales)"""
    import sqlite3
    st.header("👨‍🏫 Vista de Profesor")

    # Obtener todos los profesores únicos de la base de datos
    conn = sqlite3.connect('horario.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT profesor FROM horarios WHERE profesor != ''")
    all_teachers = sorted([row[0] for row in c.fetchall()])
    conn.close()

    if not all_teachers:
        st.warning("No hay profesores registrados en el horario.")
        return

    selected_teacher = st.selectbox("Seleccionar profesor", all_teachers)

    st.subheader(f"Horario de {selected_teacher}")

    # Consultar todas las clases asignadas a ese profesor
    conn = sqlite3.connect('horario.db')
    c = conn.cursor()
    c.execute("""
        SELECT grupo, dia, hora, materia, aula
        FROM horarios
        WHERE profesor = ?
        ORDER BY dia, hora
    """, (selected_teacher,))
    data = c.fetchall()
    conn.close()

    if data:
        import pandas as pd
        df = pd.DataFrame(data, columns=["Grupo", "Día", "Hora", "Materia", "Aula"])
        st.dataframe(df, use_container_width=True)

        # Exportar a CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📤 Exportar a CSV",
            csv,
            f"horario_{selected_teacher}.csv",
            "text/csv"
        )
    else:
        st.warning("Este profesor no tiene clases asignadas.")

def room_occupancy_view():
    """Muestra la ocupación de aulas y permite buscar el número de aula (datos reales)"""
    import sqlite3
    st.header("🏫 Ocupación de Aulas")

    # Obtener todas las aulas únicas de la base de datos
    conn = sqlite3.connect('horario.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT aula FROM horarios WHERE aula != ''")
    all_rooms = sorted([row[0] for row in c.fetchall()])
    conn.close()

    if not all_rooms:
        st.warning("No hay aulas registradas en el horario.")
        return

    # Campo de búsqueda de aula
    search_room = st.text_input("Buscar número o nombre de aula")
    filtered_rooms = [room for room in all_rooms if search_room.strip().lower() in room.lower()] if search_room else all_rooms

    if not filtered_rooms:
        st.warning("No se encontraron aulas que coincidan con la búsqueda.")
        return

    for selected_room in filtered_rooms:
        st.markdown(f"---")
        st.subheader(f"Aula: {selected_room}")
        # Permitir editar el nombre del aula
        new_room_name = st.text_input(f"Nuevo nombre para el aula {selected_room}", value=selected_room, key=f"edit_{selected_room}")
        if st.button(f"Actualizar nombre de aula {selected_room}", key=f"btn_{selected_room}"):
            if new_room_name and new_room_name != selected_room:
                conn = sqlite3.connect('horario.db')
                c = conn.cursor()
                c.execute("UPDATE horarios SET aula = ? WHERE aula = ?", (new_room_name, selected_room))
                conn.commit()
                conn.close()
                st.success(f"Nombre de aula actualizado a '{new_room_name}'")
                st.rerun()
            else:
                st.info("No hay cambios en el nombre del aula.")

        st.markdown(f"**Clases asignadas al aula '{selected_room}':**")
        # Consultar todas las clases asignadas a esa aula
        conn = sqlite3.connect('horario.db')
        c = conn.cursor()
        c.execute("""
            SELECT grupo, dia, hora, materia, profesor
            FROM horarios
            WHERE aula = ?
            ORDER BY dia, hora
        """, (selected_room,))
        data = c.fetchall()
        conn.close()

        if data:
            import pandas as pd
            df = pd.DataFrame(data, columns=["Grupo", "Día", "Hora", "Materia", "Profesor"])
            st.dataframe(df, use_container_width=True)
            # Exportar a CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                f"📤 Exportar a CSV {selected_room}",
                csv,
                f"aula_{selected_room}.csv",
                "text/csv"
            )
        else:
            st.warning(f"Esta aula no tiene clases asignadas.")

def conflict_detector():
    """Detector de conflictos en el horario"""
    st.header("⚠️ Detector de Conflictos")

    # Conflictos de profesores
    st.subheader("Profesores con clases superpuestas")

    teacher_conflicts = {}
    for teacher in get_all_teachers():
        schedule = []
        for day in DAYS:
            for time_idx, time_slot in enumerate(TIME_SLOTS):
                for group in GROUPS:
                    class_info = get_class_info(group, day, time_idx)
                    current_teacher = parse_class_info(class_info)[1]
                    if teacher in current_teacher:
                        schedule.append({
                            "Día": day,
                            "Hora": time_slot,
                            "Grupo": group,
                            "Materia": parse_class_info(class_info)[0],
                            "Aula": parse_class_info(class_info)[2]
                        })

        # Verificar superposiciones
        df = pd.DataFrame(schedule)
        if not df.empty:
            duplicates = df[df.duplicated(['Día', 'Hora'], keep=False)]
            if not duplicates.empty:
                teacher_conflicts[teacher] = duplicates

    if teacher_conflicts:
        for teacher, conflicts in teacher_conflicts.items():
            with st.expander(f"Conflictos de {teacher}"):
                st.dataframe(conflicts, use_container_width=True)
    else:
        st.success("✅ No hay conflictos de profesores")

    # Conflictos de aulas
    st.subheader("Aulas con clases superpuestas")

    room_conflicts = {}
    for room in get_all_classrooms():
        schedule = []
        for day in DAYS:
            for time_idx, time_slot in enumerate(TIME_SLOTS):
                for group in GROUPS:
                    class_info = get_class_info(group, day, time_idx)
                    current_room = parse_class_info(class_info)[2]
                    if room == current_room:
                        schedule.append({
                            "Día": day,
                            "Hora": time_slot,
                            "Grupo": group,
                            "Materia": parse_class_info(class_info)[0],
                            "Profesor": parse_class_info(class_info)[1]
                        })

        # Verificar superposiciones
        df = pd.DataFrame(schedule)
        if not df.empty:
            duplicates = df[df.duplicated(['Día', 'Hora'], keep=False)]
            if not duplicates.empty:
                room_conflicts[room] = duplicates

    if room_conflicts:
        for room, conflicts in room_conflicts.items():
            with st.expander(f"Conflictos en {room}"):
                st.dataframe(conflicts, use_container_width=True)
    else:
        st.success("✅ No hay conflictos de aulas")

# =============================================
# FUNCIONES DE DATOS (SIMULADAS PARA EL EJEMPLO)
# =============================================

def get_class_info(group, day, time_idx):
    """Obtiene información de clase desde la base de datos real"""
    time_slot = TIME_SLOTS[time_idx]
    conn = sqlite3.connect('horario.db')
    c = conn.cursor()
    c.execute("SELECT materia, profesor, aula FROM horarios WHERE grupo=? AND dia=? AND hora=?", (group, day, time_slot))
    result = c.fetchone()
    conn.close()
    if result:
        materia, profesor, aula = result
        return f"{materia} - {profesor} - {aula}"
    else:
        return "---"

def update_class_info(group, day, time_idx, new_value):
    """Actualiza información de clase en la base de datos real"""
    # Parsear la información de la clase
    subject, teacher, room, _ = parse_class_info(new_value)
    time_slot = TIME_SLOTS[time_idx]

    conn = sqlite3.connect('horario.db')
    c = conn.cursor()
    # Verificar si ya existe un registro para ese grupo, día y hora
    c.execute("SELECT id FROM horarios WHERE grupo=? AND dia=? AND hora=?", (group, day, time_slot))
    result = c.fetchone()
    if result:
        # Actualizar registro existente
        c.execute("""
            UPDATE horarios SET materia=?, profesor=?, aula=?, timestamp=CURRENT_TIMESTAMP
            WHERE id=?
        """, (subject, teacher, room, result[0]))
    else:
        # Insertar nuevo registro
        c.execute("""
            INSERT INTO horarios (grupo, dia, hora, materia, profesor, aula)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (group, day, time_slot, subject, teacher, room))
    conn.commit()
    conn.close()
    # Guardar bandera para mostrar mensaje de éxito fuera de la celda
    st.session_state['horario_guardado'] = True

def get_all_classrooms(group=None):
    """Obtiene todas las aulas (simulado)"""
    return ["AULA 26", "AULA 17", "LAB 8", "AULA 12"]

def get_all_subjects(group=None):
    """Obtiene todas las materias (simulado)"""
    return ["FRANCÉS", "RELIGIÓN", "CIENCIAS", "INGLÉS"]

def auto_save_changes(group, day, time_idx, new_value, old_value):
    """Función para guardar cambios automáticamente"""
    if new_value != old_value:
        update_class_info(group, day, time_idx, new_value)
        st.success("✅ Cambios guardados automáticamente")

# =============================================
# INTERFAZ PRINCIPAL
# =============================================

def main():
    # Barra lateral (sidebar)
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=CTP+Las+Palmitas", width=150)

        # Selector de vista
        view_options = { # type: ignore
            "📅 Vista de Horario": "schedule",
            "👨‍🏫 Vista de Profesor": "teacher",
            "🏫 Ocupación de Aulas": "rooms",
            "⚠️ Detector de Conflictos": "conflicts"
        }

        selected_view = stx.tab_bar([
            stx.TabBarItemData(id="schedule", title="📅 Horario", description="Vista principal"),
            stx.TabBarItemData(id="teacher", title="👨‍🏫 Profesor", description="Horario por docente"),
            stx.TabBarItemData(id="rooms", title="🏫 Aulas", description="Disponibilidad"),
            stx.TabBarItemData(id="conflicts", title="⚠️ Conflictos", description="Detectar problemas")
        ], default="schedule")

        st.markdown("---")

        # Selector de grupo (solo para vista de horario)
        if selected_view == "schedule":
            selected_group = st.selectbox("Seleccionar Grupo", GROUPS)
            edit_mode = st.toggle("Modo Edición", False)

        st.markdown("---")

        # Acciones rápidas
        if st.button("🔄 Actualizar Datos"):
            st.rerun()

        if st.button("📤 Exportar Todo"):
            # En una implementación real, exportaría toda la base de datos
            st.success("Datos exportados correctamente")

        st.markdown("---")
        st.markdown("**Sistema Horario 4.0**")
        st.markdown("© 2023 CTP Las Palmitas")

    # Contenido principal según vista seleccionada
    if selected_view == "schedule":
        generate_schedule_view(selected_group, edit_mode)
    elif selected_view == "teacher":
        teacher_view()
    elif selected_view == "rooms":
        room_occupancy_view()
    elif selected_view == "conflicts":
        conflict_detector()

if __name__ == "__main__":
    main()
