import streamlit as st
import pandas as pd
from modules.schedule import get_all_classrooms, get_class_info, parse_class_info, TIME_SLOTS, DAYS, GROUPS # type: ignore
from modules.exports import export_classroom_schedule_to_pdf # type: ignore
import sqlite3
import unicodedata

class ClassroomManager:
    def __init__(self):
        pass

    def get_classroom_schedule(self, classroom: str, day: str) -> pd.DataFrame:
        data = []
        for time_idx, time_slot in enumerate(TIME_SLOTS):
            classes = []
            for group in GROUPS:
                class_info = get_class_info(group, day, time_idx)
                subject, teacher, room, _ = parse_class_info(class_info)
                if room == classroom:
                    classes.append(f"{group}: {subject} ({teacher})")

            data.append({
                "Hora": time_slot,
                "Ocupación": "\n".join(classes) if classes else "Libre"
            })
        return pd.DataFrame(data)

    def show_view(self):
        st.title("🏫 Gestión de Aulas")

        # Función para normalizar texto (ignorar tildes, mayúsculas y espacios)
        def normalizar(texto):
            return ''.join(c for c in unicodedata.normalize('NFD', texto.lower().replace(' ', '')) if unicodedata.category(c) != 'Mn')

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
        if search_room:
            search_norm = normalizar(search_room)
            filtered_rooms = [room for room in all_rooms if search_norm in normalizar(room)]
        else:
            filtered_rooms = all_rooms

        if not filtered_rooms:
            st.warning("No se encontraron aulas que coincidan con la búsqueda.")
            return

        # Si hay más de una coincidencia, mostrar lista para seleccionar una sola aula
        if len(filtered_rooms) > 1:
            selected_room = st.selectbox("Selecciona un aula para ver el detalle:", filtered_rooms)
        else:
            selected_room = filtered_rooms[0]

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
