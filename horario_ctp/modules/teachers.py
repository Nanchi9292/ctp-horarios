import streamlit as st
import pandas as pd
from modules.schedule import get_all_teachers, get_class_info, parse_class_info, TIME_SLOTS, DAYS, GROUPS
from modules.exports import export_teacher_schedule_to_pdf

class TeacherView:
    def __init__(self):
        pass

    def get_teacher_schedule(self, teacher: str) -> pd.DataFrame:
        data = []
        for group in GROUPS:
            for day in DAYS:
                for time_idx, time_slot in enumerate(TIME_SLOTS):
                    class_info = get_class_info(group, day, time_idx)
                    subject, current_teacher, room, _ = parse_class_info(class_info)
                    if current_teacher == teacher:
                        data.append({
                            "Grupo": group,
                            "Día": day,
                            "Hora": time_slot,
                            "Materia": subject,
                            "Aula": room
                        })
        return pd.DataFrame(data)

    def show_view(self):
        st.header("👨‍🏫 Panel de Profesores")

        # Lista de profesores
        teachers = get_all_teachers()
        selected = st.selectbox(
            "Seleccionar profesor",
            teachers
        )

        if selected:
            df = self.get_teacher_schedule(selected)
            if not df.empty:
                st.dataframe(df, use_container_width=True)

                # Estadísticas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de clases", len(df))
                with col2:
                    st.metric("Aulas distintas", df["Aula"].nunique())
                with col3:
                    st.metric("Grupos distintos", df["Grupo"].nunique())

                # Exportar a PDF
                pdf_link = export_teacher_schedule_to_pdf(df, selected)
                st.markdown(pdf_link, unsafe_allow_html=True)
            else:
                st.warning(f"El profesor {selected} no tiene clases asignadas")
