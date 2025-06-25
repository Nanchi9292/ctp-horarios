import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date # type: ignore
import io
from typing import Dict, Optional # type: ignore
import sqlite3
from pathlib import Path
import calendar
from io import BytesIO
import xlsxwriter # type: ignore
# import plotly.express as px # type: ignore
# import plotly.graph_objects as go # type: ignore
# from plotly.subplots import make_subplots # type: ignore

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-container {
        padding: 1rem;
        background-color: #f8f9fa;
    }

    .section-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }

    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }

    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 0 16px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }

    .grade-bar {
        height: 20px;
        border-radius: 10px;
        background: linear-gradient(90deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%);
    }
</style>
""", unsafe_allow_html=True)

class GradeManager:
    def __init__(self):
        self.db_path = Path("data/grades.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self.meses = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        self.init_db()
        self.initialize_data()

    def init_db(self):
        """Inicializa la base de datos con las tablas necesarias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Tabla de estudiantes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS estudiantes (
                    id TEXT PRIMARY KEY,
                    cedula TEXT UNIQUE,
                    nombre_completo TEXT,
                    grupo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabla de asistencia
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asistencia (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estudiante_id TEXT,
                    fecha DATE,
                    estado TEXT CHECK(estado IN ('P', 'A', 'J')),
                    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
                )
            """)

            # Tabla de evaluaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estudiante_id TEXT,
                    tipo TEXT,
                    nombre TEXT,
                    fecha DATE,
                    puntuacion REAL,
                    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
                )
            """)

            # Tabla de ponderaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ponderaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT UNIQUE,
                    valor REAL
                )
            """)

            # Insertar ponderaciones por defecto si no existen
            cursor.execute("SELECT COUNT(*) FROM ponderaciones")
            if cursor.fetchone()[0] == 0:
                ponderaciones = [
                    ('Asistencia', 0.10),
                    ('Tareas', 0.10),
                    ('Proyecto', 0.15),
                    ('Prueba', 0.20),
                    ('Portafolio', 0.10),
                    ('Trabajo_Cotidiano', 0.35)
                ]
                cursor.executemany(
                    "INSERT INTO ponderaciones (tipo, valor) VALUES (?, ?)",
                    ponderaciones
                )

            conn.commit()

    def initialize_data(self):
        """Inicializa los DataFrames en session_state"""
        if 'estudiantes_df' not in st.session_state:
            st.session_state.estudiantes_df = self.get_estudiantes()

        if 'asistencia_df' not in st.session_state:
            st.session_state.asistencia_df = self.get_asistencia()

        if 'evaluaciones_df' not in st.session_state:
            st.session_state.evaluaciones_df = self.get_evaluaciones()

        if 'ponderaciones' not in st.session_state:
            st.session_state.ponderaciones = self.get_ponderaciones()

    def get_estudiantes(self) -> pd.DataFrame:
        """Obtiene la lista de estudiantes de la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(
                "SELECT * FROM estudiantes",
                conn,
                index_col=None,
                parse_dates=['created_at']
            )

    def get_asistencia(self) -> pd.DataFrame:
        """Obtiene los registros de asistencia"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(
                """
                SELECT a.*, e.nombre_completo
                FROM asistencia a
                JOIN estudiantes e ON a.estudiante_id = e.id
                """,
                conn,
                index_col=None,
                parse_dates=['fecha']
            )

    def get_evaluaciones(self) -> pd.DataFrame:
        """Obtiene los registros de evaluaciones"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(
                """
                SELECT e.*, est.nombre_completo
                FROM evaluaciones e
                JOIN estudiantes est ON e.estudiante_id = est.id
                """,
                conn,
                index_col=None,
                parse_dates=['fecha']
            )

    def get_ponderaciones(self) -> Dict[str, float]:
        """Obtiene las ponderaciones de la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query("SELECT tipo, valor FROM ponderaciones", conn)
            return dict(zip(df['tipo'], df['valor']))

    def agregar_estudiante(self, id: str, cedula: str, nombre: str, grupo: str):
        """Agrega un nuevo estudiante a la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO estudiantes (id, cedula, nombre_completo, grupo)
                    VALUES (?, ?, ?, ?)
                """, (id, cedula, nombre, grupo))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def actualizar_asistencia(self, estudiante_id: str, fecha: str, estado: str):
        """Actualiza el registro de asistencia de un estudiante"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO asistencia (estudiante_id, fecha, estado)
                VALUES (?, ?, ?)
            """, (estudiante_id, fecha, estado))
            conn.commit()

    def actualizar_evaluacion(self, estudiante_id: int, tipo: str, nombre: str, fecha: datetime, puntuacion: float):
        """Actualiza o inserta una evaluación en la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Convertir fecha a string en formato YYYY-MM-DD
            fecha_str = fecha.strftime('%Y-%m-%d')
            cursor.execute("""
                INSERT OR REPLACE INTO evaluaciones
                (estudiante_id, tipo, nombre, fecha, puntuacion)
                VALUES (?, ?, ?, ?, ?)
            """, (estudiante_id, tipo, nombre, fecha_str, puntuacion))
            conn.commit()

    def actualizar_ponderaciones(self, ponderaciones: Dict[str, float]):
        """Actualiza las ponderaciones en la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for tipo, valor in ponderaciones.items():
                cursor.execute("""
                    UPDATE ponderaciones SET valor = ? WHERE tipo = ?
                """, (valor, tipo))
            conn.commit()

    def calcular_asistencia_porcentaje(self, estudiante_id: str) -> float:
        """Calcula el porcentaje de asistencia de un estudiante"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN estado IN ('P', 'J') THEN 1 ELSE 0 END) as presentes
                FROM asistencia
                WHERE estudiante_id = ?
            """, (estudiante_id,))
            total, presentes = cursor.fetchone()
            return (presentes / total * 100) if total > 0 else 0.0

    def calcular_promedio_evaluaciones(self, estudiante_id: str, tipo: str) -> float:
        """Calcula el promedio de un tipo específico de evaluación"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AVG(puntuacion)
                FROM evaluaciones
                WHERE estudiante_id = ? AND tipo = ?
            """, (estudiante_id, tipo))
            return cursor.fetchone()[0] or 0.0

    def calcular_calificaciones_finales(self) -> pd.DataFrame:
        """Calcula las calificaciones finales para todos los estudiantes"""
        calificaciones = []

        for _, estudiante in st.session_state.estudiantes_df.iterrows():
            estudiante_id = estudiante['id']
            nombre = estudiante['nombre_completo']

            # Calcular componentes individuales
            asistencia_pct = self.calcular_asistencia_porcentaje(estudiante_id)
            asistencia_nota = (asistencia_pct / 100) * 100

            tareas = self.calcular_promedio_evaluaciones(estudiante_id, 'Tareas')
            proyecto = self.calcular_promedio_evaluaciones(estudiante_id, 'Proyecto')
            prueba = self.calcular_promedio_evaluaciones(estudiante_id, 'Prueba')
            portafolio = self.calcular_promedio_evaluaciones(estudiante_id, 'Portafolio')
            trabajo_cotidiano = self.calcular_promedio_evaluaciones(estudiante_id, 'Trabajo_Cotidiano')

            # Aplicar ponderaciones
            nota_final = (
                asistencia_nota * st.session_state.ponderaciones['Asistencia'] +
                tareas * st.session_state.ponderaciones['Tareas'] +
                proyecto * st.session_state.ponderaciones['Proyecto'] +
                prueba * st.session_state.ponderaciones['Prueba'] +
                portafolio * st.session_state.ponderaciones['Portafolio'] +
                trabajo_cotidiano * st.session_state.ponderaciones['Trabajo_Cotidiano']
            )

            calificaciones.append({
                'ID': estudiante_id,
                'Nombre': nombre,
                'Asistencia': f"{asistencia_pct:.1f}%",
                'Asistencia_Nota': asistencia_nota,
                'Tareas': tareas,
                'Proyecto': proyecto,
                'Prueba': prueba,
                'Portafolio': portafolio,
                'Trabajo_Cotidiano': trabajo_cotidiano,
                'Nota_Final': nota_final
            })

        return pd.DataFrame(calificaciones)

    def exportar_a_excel(self) -> bytes:
        """Exporta todos los datos a un archivo Excel"""
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Exportar estudiantes
            if not st.session_state.estudiantes_df.empty:
                st.session_state.estudiantes_df.to_excel(writer, sheet_name='Estudiantes', index=False)

            # Exportar calificaciones finales
            calificaciones_df = self.calcular_calificaciones_finales()
            if not calificaciones_df.empty:
                calificaciones_df.to_excel(writer, sheet_name='Calificaciones_Finales', index=False)

            # Exportar asistencia
            if not st.session_state.asistencia_df.empty:
                st.session_state.asistencia_df.to_excel(writer, sheet_name='Asistencia', index=False)

            # Exportar evaluaciones
            if not st.session_state.evaluaciones_df.empty:
                st.session_state.evaluaciones_df.to_excel(writer, sheet_name='Evaluaciones', index=False)

        output.seek(0)
        return output.getvalue()

    def show_view(self):
        """Muestra la interfaz principal del módulo de notas"""
        # Header principal
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='color: #667eea; font-size: 3rem; margin-bottom: 0.5rem;'>
                🎓 Sistema de Gestión Académica
            </h1>
            <p style='color: #666; font-size: 1.2rem;'>
                Gestión integral de calificaciones y asistencia estudiantil
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Configuración de ponderaciones
        with st.expander("⚙️ Configuración de Ponderaciones", expanded=False):
            st.write("**Configurar pesos para el cálculo de calificaciones finales:**")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.session_state.ponderaciones['Asistencia'] = st.slider(
                    "Asistencia", 0.0, 1.0, st.session_state.ponderaciones['Asistencia'], 0.01
                )
                st.session_state.ponderaciones['Tareas'] = st.slider(
                    "Tareas", 0.0, 1.0, st.session_state.ponderaciones['Tareas'], 0.01
                )

            with col2:
                st.session_state.ponderaciones['Proyecto'] = st.slider(
                    "Proyecto", 0.0, 1.0, st.session_state.ponderaciones['Proyecto'], 0.01
                )
                st.session_state.ponderaciones['Prueba'] = st.slider(
                    "Prueba", 0.0, 1.0, st.session_state.ponderaciones['Prueba'], 0.01
                )

            with col3:
                st.session_state.ponderaciones['Portafolio'] = st.slider(
                    "Portafolio", 0.0, 1.0, st.session_state.ponderaciones['Portafolio'], 0.01
                )
                st.session_state.ponderaciones['Trabajo_Cotidiano'] = st.slider(
                    "Trabajo Cotidiano", 0.0, 1.0, st.session_state.ponderaciones['Trabajo_Cotidiano'], 0.01
                )

            # Verificar que sumen 100%
            suma_ponderaciones = sum(st.session_state.ponderaciones.values())
            if abs(suma_ponderaciones - 1.0) > 0.01:
                st.warning(f"⚠️ Las ponderaciones deben sumar 100%. Actual: {suma_ponderaciones*100:.1f}%")
            else:
                st.success("✅ Ponderaciones configuradas correctamente (100%)")
                self.actualizar_ponderaciones(st.session_state.ponderaciones)

        # Pestañas principales
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👥 Estudiantes",
            "📅 Asistencia",
            "📝 Evaluaciones",
            "📊 Calificaciones",
            "📈 Estadísticas"
        ])

        with tab1:
            self.show_estudiantes_tab()

        with tab2:
            self.show_asistencia_tab()

        with tab3:
            self.show_evaluaciones_tab()

        with tab4:
            self.show_calificaciones_tab()

        with tab5:
            self.show_estadisticas_tab()

    def show_estudiantes_tab(self):
        """Muestra la pestaña de gestión de estudiantes"""
        st.header("👥 Gestión de Estudiantes")

        # Formulario para agregar estudiantes
        with st.container():
            st.subheader("➕ Agregar Nuevo Estudiante")

            col1, col2, col3, col4 = st.columns([2, 2, 3, 1])

            with col1:
                nuevo_id = st.text_input("ID Estudiante", placeholder="Ej: EST001")

            with col2:
                nueva_cedula = st.text_input("Cédula", placeholder="Ej: 123456789")

            with col3:
                nuevo_nombre = st.text_input("Nombre Completo", placeholder="Ej: Juan Pérez García")

            with col4:
                if st.button("Agregar", type="primary"):
                    if nuevo_id and nueva_cedula and nuevo_nombre:
                        if self.agregar_estudiante(nuevo_id, nueva_cedula, nuevo_nombre, ""):
                            st.session_state.estudiantes_df = self.get_estudiantes()
                            st.success(f"✅ Estudiante {nuevo_nombre} agregado exitosamente!")
                            st.rerun()
                        else:
                            st.error("❌ El ID o cédula ya existe. Use valores diferentes.")
                    else:
                        st.error("❌ Complete todos los campos.")

        st.divider()

        # Lista de estudiantes
        if not st.session_state.estudiantes_df.empty:
            st.subheader("📋 Lista de Estudiantes")

            # Editor de estudiantes
            st.data_editor(
                st.session_state.estudiantes_df,
                column_config={
                    "id": st.column_config.TextColumn("ID", width="small"),
                    "cedula": st.column_config.TextColumn("Cédula", width="medium"),
                    "nombre_completo": st.column_config.TextColumn("Nombre Completo", width="large")
                },
                hide_index=True,
                use_container_width=True,
                key="editor_estudiantes"
            )

            st.info(f"📊 Total de estudiantes registrados: {len(st.session_state.estudiantes_df)}")
        else:
            st.info("📝 No hay estudiantes registrados aún.")

    def show_asistencia_tab(self):
        """Muestra la pestaña de asistencia"""
        st.header("📅 Registro de Asistencia")

        # Sub-pestañas por meses
        tabs_meses = st.tabs(self.meses)

        for i, mes in enumerate(self.meses):
            with tabs_meses[i]:
                self.show_asistencia_mes(mes)

    def show_asistencia_mes(self, mes: str):
        """Muestra la asistencia para un mes específico"""
        st.subheader(f"Asistencia - {mes}")

        # Obtener el año actual
        año_actual = datetime.now().year

        # Crear fechas del mes
        fechas_mes = pd.date_range(
            start=f"{año_actual}-{self.meses.index(mes)+1:02d}-01",
            end=f"{año_actual}-{self.meses.index(mes)+1:02d}-{calendar.monthrange(año_actual, self.meses.index(mes)+1)[1]}",
            freq='D'
        )

        # Filtrar asistencia del mes
        asistencia_mes = st.session_state.asistencia_df[
            st.session_state.asistencia_df['fecha'].dt.strftime('%Y-%m') == f"{año_actual}-{self.meses.index(mes)+1:02d}"
        ]

        # Crear DataFrame base con todos los estudiantes y fechas
        estudiantes = st.session_state.estudiantes_df['nombre_completo'].tolist()
        df_base = pd.DataFrame(index=estudiantes, columns=fechas_mes.strftime('%Y-%m-%d'))
        df_base.fillna('', inplace=True)

        # Llenar con datos existentes
        for _, row in asistencia_mes.iterrows():
            fecha_str = row['fecha'].strftime('%Y-%m-%d')
            if fecha_str in df_base.columns:
                estado = row['estado']
                if estado == 'P':
                    df_base.loc[row['nombre_completo'], fecha_str] = '✅'
                elif estado == 'A':
                    df_base.loc[row['nombre_completo'], fecha_str] = '❌'
                elif estado == 'J':
                    df_base.loc[row['nombre_completo'], fecha_str] = '⚠️'

        # Configurar el editor de datos
        column_config = {}
        for fecha in fechas_mes.strftime('%Y-%m-%d'):
            column_config[fecha] = st.column_config.SelectboxColumn(
                fecha,
                options=['', '✅', '❌', '⚠️'],
                required=False
            )

        # Mostrar tabla de asistencia editable
        edited_df = st.data_editor(
            df_base,
            column_config=column_config,
            use_container_width=True,
            height=400,
            key=f"editor_asistencia_{mes}"
        )

        # Botón para guardar cambios
        if st.button("💾 Guardar Cambios", key=f"guardar_{mes}"):
            for estudiante in estudiantes:
                for fecha in fechas_mes:
                    fecha_str = fecha.strftime('%Y-%m-%d')
                    estado = edited_df.loc[estudiante, fecha_str]
                    if estado:
                        # Guardar con los valores correctos para la base de datos
                        if estado == '✅':
                            estado_db = 'P'
                        elif estado == '❌':
                            estado_db = 'A'
                        elif estado == '⚠️':
                            estado_db = 'J'
                        else:
                            continue
                        estudiante_id = st.session_state.estudiantes_df[
                            st.session_state.estudiantes_df['nombre_completo'] == estudiante
                        ]['id'].iloc[0]
                        self.actualizar_asistencia(estudiante_id, fecha_str, estado_db)
            st.success("✅ Cambios guardados correctamente")
            st.rerun()

        # Visualización coloreada (no editable, pero en tiempo real)
        def valor_asistencia(val):
            if val == '✅':
                return '✅ Asistió'
            elif val == '❌':
                return '❌ No asistió'
            elif val == '⚠️':
                return '⚠️ Tardía'
            else:
                return ''
        df_coloreada = edited_df.applymap(valor_asistencia) # type: ignore
        def color_asistencia(val):
            if 'Asistió' in val:
                return 'background-color: #d4edda; color: #000; font-weight: bold;'
            elif 'No asistió' in val:
                return 'background-color: #f8d7da; color: #000; font-weight: bold;'
            elif 'Tardía' in val:
                return 'background-color: #fff3cd; color: #000; font-weight: bold;'
            else:
                return ''
        st.markdown('<b>Vista de colores de asistencia:</b>', unsafe_allow_html=True)
        st.write(df_coloreada.style.applymap(color_asistencia))

    def show_evaluaciones_tab(self):
        """Muestra la pestaña de evaluaciones"""
        st.header("📝 Evaluaciones")

        # Sub-pestañas por tipo de evaluación
        tipos_evaluacion = ['Tareas', 'Proyecto', 'Prueba', 'Portafolio', 'Trabajo_Cotidiano']
        tabs_evaluaciones = st.tabs(tipos_evaluacion)

        for i, tipo in enumerate(tipos_evaluacion):
            with tabs_evaluaciones[i]:
                self.show_evaluaciones_tipo(tipo)

    def show_evaluaciones_tipo(self, tipo: str):
        """Muestra las evaluaciones de un tipo específico con interfaz tipo Excel"""
        st.subheader(f"📝 {tipo}")

        # Obtener evaluaciones del tipo seleccionado
        evaluaciones = st.session_state.evaluaciones_df[
            st.session_state.evaluaciones_df['tipo'] == tipo
        ]

        # Crear DataFrame para edición
        df_edicion = pd.DataFrame()

        # Agregar columna de estudiantes
        df_edicion['Estudiante'] = st.session_state.estudiantes_df['nombre_completo']

        # Agregar columnas para cada evaluación
        evaluaciones_unicas = evaluaciones['nombre'].unique()
        for eval_nombre in evaluaciones_unicas:
            df_edicion[eval_nombre] = ''

        # Llenar con datos existentes
        for _, row in evaluaciones.iterrows():
            estudiante = st.session_state.estudiantes_df[
                st.session_state.estudiantes_df['id'] == row['estudiante_id']
            ]['nombre_completo'].iloc[0]
            df_edicion.loc[df_edicion['Estudiante'] == estudiante, row['nombre']] = row['puntuacion']

        # Agregar columna de total
        df_edicion['Total'] = 0

        # Barra de herramientas mejorada
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.markdown("### 📝 Nueva Evaluación")
            nombre = st.text_input("Nombre de la evaluación", key=f"nombre_{tipo}")
            fecha = st.date_input("Fecha", key=f"fecha_{tipo}") # type: ignore
            if st.button("➕ Agregar", key=f"add_{tipo}"):
                if nombre:
                    df_edicion[nombre] = ''
                    st.success(f"✅ Evaluación '{nombre}' agregada")
                    st.rerun()
                else:
                    st.error("❌ Por favor ingrese un nombre para la evaluación")

        with col2:
            st.markdown("### 💾 Guardar Cambios")
            if st.button("💾 Guardar", key=f"save_{tipo}"):
                self.guardar_cambios_evaluaciones(tipo, df_edicion)

        with col3:
            st.markdown("### 📊 Resumen")
            if not df_edicion.empty:
                promedio = df_edicion['Total'].mean()
                st.metric("Promedio General", f"{promedio:.1f}")

        # Editor de datos estilo Excel con mejoras visuales
        st.markdown("### 📋 Calificaciones")

        # Configurar columnas para el editor
        column_config = {
            "Estudiante": st.column_config.TextColumn(
                "Estudiante",
                help="Nombre del estudiante",
                disabled=True
            ),
            "Total": st.column_config.ProgressColumn(
                "Total",
                help="Promedio",
                min_value=0,
                max_value=100,
                format="%.1f"
            )
        }

        # Agregar configuración para columnas de evaluaciones
        for col in df_edicion.columns:
            if col not in ['Estudiante', 'Total']:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    help=f"Nota de {col}",
                    min_value=0,
                    max_value=100,
                    step=1,
                    format="%d"
                )

        # Crear editor de datos con estilo Excel
        edited_df = st.data_editor(
            df_edicion,
            use_container_width=True,
            height=400,
            num_rows="dynamic",
            column_config=column_config,
            hide_index=True,
            key=f"editor_{tipo}"
        )

        # Calcular totales y mostrar retroalimentación
        for idx, row in edited_df.iterrows():
            # Calcular promedio
            total = 0
            count = 0
            notas = []
            for col in edited_df.columns:
                if col not in ['Estudiante', 'Total']:
                    try:
                        valor = float(row[col])
                        if not pd.isna(valor):
                            total += valor
                            count += 1
                            notas.append(valor)
                    except (ValueError, TypeError):
                        continue

            # Calcular promedio si hay evaluaciones
            if count > 0:
                promedio = total / count
                edited_df.at[idx, 'Total'] = promedio

                # Mostrar retroalimentación si hay notas
                if notas:
                    estudiante = row['Estudiante']
                    st.markdown(f"#### 📊 Análisis para {estudiante}")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Promedio", f"{promedio:.1f}")
                    with col2:
                        st.metric("Nota más alta", f"{max(notas):.1f}")
                    with col3:
                        st.metric("Nota más baja", f"{min(notas):.1f}")

                    # Mostrar notas en formato de texto mientras plotly no esté disponible
                    st.write(f"**Notas de {estudiante}:**")
                    estudiante_data = edited_df[edited_df['Estudiante'] == estudiante]
                    if not estudiante_data.empty:
                        for col in estudiante_data.columns:
                            if col not in ['Estudiante', 'Total']:
                                try:
                                    nota = estudiante_data[col].values[0]
                                    st.write(f"- {col}: {nota:.1f}")
                                except:
                                    st.write(f"- {col}: N/A")
                    else:
                        st.write("No se encontraron datos para este estudiante")

        # Botón para exportar
        if st.button("📥 Exportar a Excel", key=f"export_{tipo}"):
            self.exportar_evaluaciones(tipo, edited_df)

    def guardar_cambios_evaluaciones(self, tipo: str, df: pd.DataFrame):
        """Guarda los cambios realizados en las evaluaciones"""
        try:
            # Convertir DataFrame a formato largo
            df_melted = df.melt(
                id_vars=['Estudiante', 'Total'],
                var_name='nombre',
                value_name='puntuacion'
            )

            # Actualizar base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for _, row in df_melted.iterrows():
                # Obtener ID del estudiante
                estudiante_id = st.session_state.estudiantes_df[
                    st.session_state.estudiantes_df['nombre_completo'] == row['Estudiante']
                ]['id'].iloc[0]

                cursor.execute("""
                    UPDATE evaluaciones
                    SET puntuacion = ?
                    WHERE estudiante_id = ? AND nombre = ? AND tipo = ?
                """, (row['puntuacion'], estudiante_id, row['nombre'], tipo))

            conn.commit()
            conn.close()

            st.success("✅ Cambios guardados correctamente")
        except Exception as e:
            st.error(f"❌ Error al guardar cambios: {str(e)}")

    def exportar_evaluaciones(self, tipo: str, df: pd.DataFrame):
        """Exporta las evaluaciones a Excel"""
        try:
            # Crear archivo Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Escribir DataFrame
                df.to_excel(writer, sheet_name=tipo, index=False)

                # Obtener la hoja de trabajo
                worksheet = writer.sheets[tipo]

                # Configurar formato de encabezados
                for col_num, value in enumerate(df.columns.values):
                    # Escribir encabezado con formato
                    worksheet.write(0, col_num, value, {
                        'bold': True,
                        'bg_color': '#4CAF50',
                        'font_color': 'white',
                        'border': 1
                    })
                    # Ajustar ancho de columna
                    worksheet.set_column(col_num, col_num, 15)

            # Preparar archivo para descarga
            output.seek(0)
            st.download_button(
                label="📥 Descargar Excel",
                data=output,
                file_name=f"evaluaciones_{tipo.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"❌ Error al exportar: {str(e)}")

    def show_calificaciones_tab(self):
        """Muestra la pestaña de calificaciones"""
        st.header("📊 Calificaciones Finales")

        # Calcular calificaciones
        calificaciones_df = self.calcular_calificaciones_finales()

        if not calificaciones_df.empty:
            # Mostrar tabla de calificaciones
            st.subheader("📋 Tabla de Calificaciones")

            # Preparar datos para mostrar
            display_df = calificaciones_df[[
                'Nombre', 'Asistencia', 'Tareas', 'Proyecto',
                'Prueba', 'Portafolio', 'Trabajo_Cotidiano', 'Nota_Final'
            ]].copy()

            # Configurar editor de calificaciones (solo lectura)
            st.dataframe(
                display_df,
                column_config={
                    "Nombre": st.column_config.TextColumn("Estudiante", width="medium"),
                    "Asistencia": st.column_config.TextColumn("Asistencia", width="small"),
                    "Tareas": st.column_config.NumberColumn("Tareas", format="%.1f"),
                    "Proyecto": st.column_config.NumberColumn("Proyecto", format="%.1f"),
                    "Prueba": st.column_config.NumberColumn("Prueba", format="%.1f"),
                    "Portafolio": st.column_config.NumberColumn("Portafolio", format="%.1f"),
                    "Trabajo_Cotidiano": st.column_config.NumberColumn("T. Cotidiano", format="%.1f"),
                    "Nota_Final": st.column_config.ProgressColumn(
                        "Nota Final",
                        min_value=0,
                        max_value=100,
                        format="%.1f"
                    )
                },
                hide_index=True,
                use_container_width=True
            )

            # Estadísticas de calificaciones
            st.subheader("📈 Resumen de Calificaciones")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                promedio_general = calificaciones_df['Nota_Final'].mean()
                st.metric(
                    "Promedio General",
                    f"{promedio_general:.1f}",
                    delta=None
                )

            with col2:
                nota_maxima = calificaciones_df['Nota_Final'].max()
                st.metric(
                    "Nota Máxima",
                    f"{nota_maxima:.1f}",
                    delta=None
                )

            with col3:
                nota_minima = calificaciones_df['Nota_Final'].min()
                st.metric(
                    "Nota Mínima",
                    f"{nota_minima:.1f}",
                    delta=None
                )

            with col4:
                aprobados = len(calificaciones_df[calificaciones_df['Nota_Final'] >= 70])
                st.metric(
                    "Estudiantes Aprobados",
                    f"{aprobados}",
                    delta=f"{(aprobados/len(calificaciones_df)*100):.1f}%"
                )

        else:
            st.info("📝 No hay datos suficientes para calcular calificaciones.")

    def show_estadisticas_tab(self):
        """Muestra la pestaña de estadísticas"""
        st.header("📈 Estadísticas y Análisis")

        if not st.session_state.estudiantes_df.empty:
            # Métricas generales
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                total_estudiantes = len(st.session_state.estudiantes_df)
                st.metric("👥 Total Estudiantes", total_estudiantes)

            with col2:
                total_evaluaciones = len(st.session_state.evaluaciones_df) if not st.session_state.evaluaciones_df.empty else 0
                st.metric("📝 Total Evaluaciones", total_evaluaciones)

            with col3:
                # Calcular promedio de asistencia
                if not st.session_state.asistencia_df.empty:
                    asistencias = []
                    for _, estudiante in st.session_state.estudiantes_df.iterrows():
                        asistencias.append(self.calcular_asistencia_porcentaje(estudiante['id']))
                    promedio_asistencia = np.mean(asistencias) if asistencias else 0
                else:
                    promedio_asistencia = 0

                st.metric("📅 Asistencia Promedio", f"{promedio_asistencia:.1f}%")

            with col4:
                calificaciones_df = self.calcular_calificaciones_finales()
                if not calificaciones_df.empty:
                    promedio_notas = calificaciones_df['Nota_Final'].mean()
                    st.metric("📊 Promedio General", f"{promedio_notas:.1f}")
                else:
                    st.metric("📊 Promedio General", "N/A")

            # Gráfico de distribución de calificaciones
            if not calificaciones_df.empty:
                st.subheader("📊 Distribución de Calificaciones")

                # Categorizar calificaciones
                excelente = len(calificaciones_df[calificaciones_df['Nota_Final'] >= 90])
                bueno = len(calificaciones_df[(calificaciones_df['Nota_Final'] >= 80) & (calificaciones_df['Nota_Final'] < 90)])
                regular = len(calificaciones_df[(calificaciones_df['Nota_Final'] >= 70) & (calificaciones_df['Nota_Final'] < 80)])
                deficiente = len(calificaciones_df[calificaciones_df['Nota_Final'] < 70])

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f"""
                    <div class="metric-container" style="background: linear-gradient(90deg, #00b894, #00a085);">
                        <h3>🏆 Excelente</h3>
                        <h2>{excelente}</h2>
                        <p>90-100 puntos</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="metric-container" style="background: linear-gradient(90deg, #0984e3, #74b9ff);">
                        <h3>👍 Bueno</h3>
                        <h2>{bueno}</h2>
                        <p>80-89 puntos</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="metric-container" style="background: linear-gradient(90deg, #fdcb6e, #e17055);">
                        <h3>⚠️ Regular</h3>
                        <h2>{regular}</h2>
                        <p>70-79 puntos</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    st.markdown(f"""
                    <div class="metric-container" style="background: linear-gradient(90deg, #d63031, #e84393);">
                        <h3>❌ Deficiente</h3>
                        <h2>{deficiente}</h2>
                        <p>0-69 puntos</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Análisis por componente
                st.subheader("📋 Análisis por Componente")

                if not calificaciones_df.empty:
                    componentes = ['Tareas', 'Proyecto', 'Prueba', 'Portafolio', 'Trabajo_Cotidiano']

                    for componente in componentes:
                        if componente in calificaciones_df.columns:
                            promedio_comp = calificaciones_df[componente].mean()
                            max_comp = calificaciones_df[componente].max()
                            min_comp = calificaciones_df[componente].min()

                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric(f"{componente} - Promedio", f"{promedio_comp:.1f}")
                            with col2:
                                st.metric(f"{componente} - Máximo", f"{max_comp:.1f}")
                            with col3:
                                st.metric(f"{componente} - Mínimo", f"{min_comp:.1f}")

                    st.divider()

        else:
            st.info("📝 Agregue estudiantes para ver estadísticas detalladas.")

        # Botón de exportación
        st.divider()

        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            if st.button("📥 Exportar a Excel", type="primary", use_container_width=True):
                excel_data = self.exportar_a_excel()

                if excel_data:
                    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombre_archivo = f"Gestion_Academica_{fecha_actual}.xlsx"

                    st.download_button(
                        label="⬇️ Descargar Archivo Excel",
                        data=excel_data,
                        file_name=nombre_archivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

                    st.success("✅ Archivo Excel generado exitosamente!")
                else:
                    st.error("❌ Error al generar el archivo Excel.")

        # Footer
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0; color: #666; border-top: 1px solid #eee; margin-top: 2rem;'>
            <p>🎓 Sistema de Gestión Académica - Desarrollado con Streamlit</p>
            <p><small>© 2025 - Gestión integral de calificaciones y asistencia</small></p>
        </div>
        """, unsafe_allow_html=True)

def generate_grades_view():
    """Genera la vista principal del módulo de notas"""
    grade_manager = GradeManager()
    grade_manager.show_view()
