import streamlit as st
import pandas as pd
from modules.database import get_db

def detect_conflicts():
    conflicts = { # type: ignore
        "teachers": [],
        "classrooms": []
    }

    with get_db() as conn:
        # Conflictos de profesores
        teacher_conflicts = conn.execute('''
            SELECT teacher, day, time_slot, COUNT(*) as count
            FROM classes
            GROUP BY teacher, day, time_slot
            HAVING count > 1
        ''').fetchall()

        # Conflictos de aulas
        classroom_conflicts = conn.execute('''
            SELECT classroom, day, time_slot, COUNT(*) as count
            FROM classes
            WHERE classroom != ''
            GROUP BY classroom, day, time_slot
            HAVING count > 1
        ''').fetchall()

    return {
        "teachers": pd.DataFrame(teacher_conflicts),
        "classrooms": pd.DataFrame(classroom_conflicts)
    }

def show_conflicts_view():
    st.header("⚠️ Detección de Conflictos")

    conflicts = detect_conflicts()

    st.subheader("Profesores con clases superpuestas")
    if not conflicts["teachers"].empty:
        st.dataframe(conflicts["teachers"], use_container_width=True)
    else:
        st.success("✅ No hay conflictos con profesores")

    st.subheader("Aulas con clases superpuestas")
    if not conflicts["classrooms"].empty:
        st.dataframe(conflicts["classrooms"], use_container_width=True)
    else:
        st.success("✅ No hay conflictos con aulas")
