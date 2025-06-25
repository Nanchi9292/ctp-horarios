import streamlit as st
import pandas as pd # type: ignore
from datetime import datetime # type: ignore

def generate_manual_view():
    """Genera la vista del manual de usuario"""

    # Header principal
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #667eea; font-size: 3rem; margin-bottom: 0.5rem;'>
            📚 Manual de Usuario
        </h1>
        <p style='color: #e67e22; font-size: 1.5rem; font-weight: bold;'>
            🚧 Sistema en fase beta 🚧
        </p>
        <p style='color: #666; font-size: 1.2rem;'>
            Guía completa del Sistema de Gestión CTP Las Palmitas
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Pestañas del manual
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 Inicio",
        "📅 Horarios",
        "👨‍🏫 Profesores",
        "🏫 Aulas",
        "📊 Notas",
        "📱 Comunicación",
        "❓ Preguntas Frecuentes"
    ])

    with tab1:
        show_welcome_section()

    with tab2:
        show_schedule_manual()

    with tab3:
        show_teachers_manual()

    with tab4:
        show_classrooms_manual()

    with tab5:
        show_grades_manual()

    with tab6:
        show_communication_manual()

    with tab7:
        show_faq_section()

def show_welcome_section():
    """Sección de bienvenida y descripción general"""
    st.header("🏠 Bienvenido al Sistema de Gestión CTP")

    st.markdown("""
    <div style='color: #e67e22; font-size: 1.3rem; font-weight: bold;'>
    🚧 Sistema en fase beta: Puede contener errores o cambios frecuentes. 🚧
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### ¿Qué es este sistema?

    El **Sistema de Gestión CTP Las Palmitas** es una plataforma integral diseñada para facilitar
    la administración académica del centro educativo. Este sistema combina múltiples funcionalidades
    en una sola aplicación web moderna y fácil de usar.

    ### 🎯 Objetivos del Sistema

    - **Automatizar** procesos administrativos repetitivos
    - **Centralizar** toda la información académica
    - **Facilitar** la comunicación entre docentes, estudiantes y padres
    - **Mejorar** el seguimiento del rendimiento académico
    - **Optimizar** la gestión de recursos educativos

    ### 🚀 Características Principales

    | Módulo | Descripción | Beneficios |
    |--------|-------------|------------|
    | 📅 **Horarios** | Gestión completa de horarios de clases | Organización eficiente del tiempo |
    | 👨‍🏫 **Profesores** | Administración del personal docente | Control de carga académica |
    | 🏫 **Aulas** | Gestión de espacios físicos | Optimización de recursos |
    | 📊 **Notas** | Sistema de calificaciones integral | Seguimiento académico detallado |
    | 📱 **Comunicación** | Bot de WhatsApp integrado | Comunicación directa y eficiente |

    ### 👥 Usuarios del Sistema

    **👨‍🏫 Docentes:**
    - Gestionar horarios de clases
    - Registrar calificaciones
    - Comunicarse con estudiantes y padres
    - Ver estadísticas de rendimiento

    **👨‍💼 Administradores:**
    - Gestión completa del sistema
    - Administración de usuarios
    - Configuración de parámetros
    - Generación de reportes

    **👨‍🎓 Estudiantes:**
    - Consultar horarios
    - Ver calificaciones
    - Recibir notificaciones

    ### 🔐 Seguridad y Acceso

    - **Autenticación segura** con usuario y contraseña
    - **Roles diferenciados** según el tipo de usuario
    - **Acceso restringido** a funciones según permisos
    - **Datos protegidos** en base de datos local

    ### 📱 Compatibilidad

    - ✅ **Navegadores web modernos** (Chrome, Firefox, Safari, Edge)
    - ✅ **Dispositivos móviles** (responsive design)
    - ✅ **Tablets y computadoras**
    - ✅ **Sistema operativo independiente**

    ---

    ### 🎓 CTP Las Palmitas

    Este sistema fue desarrollado específicamente para el **Colegio Técnico Profesional Las Palmitas**,
    con el objetivo de modernizar y optimizar todos los procesos administrativos y académicos
    de la institución.

    **📍 Ubicación:** Las Palmitas, Costa Rica
    **📞 Contacto:** [Información de contacto]
    **🌐 Sitio web:** [URL del colegio]
    """)

def show_schedule_manual():
    """Manual de la sección de horarios"""
    st.header("📅 Gestión de Horarios")

    st.markdown("""
    ### ¿Qué puedes hacer en esta sección?

    El módulo de **Horarios** te permite gestionar completamente los horarios de clases
    de todos los grupos del colegio, con herramientas avanzadas de visualización y edición.

    ### 🎯 Funcionalidades Principales

    #### 1. **Vista de Horario Principal**
    - Visualizar horarios por grupo (7-1, 7-4, 8-1, etc.)
    - Ver todas las materias y profesores asignados
    - Identificar horarios de almuerzo y recreos
    - Navegar entre diferentes grupos fácilmente

    #### 2. **Vista de Profesor**
    - Ver horarios específicos de cada docente
    - Identificar carga académica por profesor
    - Detectar conflictos de horarios
    - Optimizar distribución de clases

    #### 3. **Ocupación de Aulas**
    - Ver disponibilidad de espacios físicos
    - Identificar aulas disponibles en horarios específicos
    - Optimizar uso de recursos
    - Evitar conflictos de espacios

    #### 4. **Detector de Conflictos**
    - Identificar automáticamente problemas en horarios
    - Detectar profesores con doble asignación
    - Encontrar aulas con múltiples clases simultáneas
    - Sugerir correcciones automáticas

    ### 🛠️ Cómo usar el módulo

    #### **Paso 1: Seleccionar Vista**
    1. En la barra lateral, selecciona la vista deseada:
       - 📅 **Horario**: Vista principal por grupos
       - 👨‍🏫 **Profesor**: Horarios por docente
       - 🏫 **Aulas**: Disponibilidad de espacios
       - ⚠️ **Conflictos**: Detección de problemas

    #### **Paso 2: Configurar Parámetros**
    1. **Para vista de horario:**
       - Selecciona el grupo deseado
       - Activa/desactiva modo edición
       - Ajusta filtros si es necesario

    2. **Para vista de profesor:**
       - Selecciona el docente
       - Configura período académico
       - Aplica filtros de materias

    #### **Paso 3: Interactuar con los Datos**
    1. **Visualización:**
       - Los horarios se muestran en formato de tabla
       - Cada celda representa un período de clase
       - Los colores indican diferentes materias
       - Hover sobre celdas para más información

    2. **Edición (modo edición activado):**
       - Haz clic en cualquier celda para editar
       - Selecciona materia y profesor
       - Guarda cambios automáticamente

    ### 📊 Interpretación de Colores

    | Color | Significado |
    |-------|-------------|
    | 🟡 **Amarillo** | Matemática |
    | 🔴 **Rojo** | Español |
    | 🟢 **Verde** | Ciencias |
    | 🔵 **Azul** | Inglés |
    | 🟣 **Morado** | Sociales |
    | 🟠 **Naranja** | Educación Física |
    | ⚫ **Gris** | Almuerzo/Recreo |

    ### 💡 Consejos de Uso

    - **Planificación:** Usa la vista de conflictos antes de crear horarios
    - **Optimización:** Revisa la ocupación de aulas para mejor distribución
    - **Comunicación:** Comparte horarios con profesores y estudiantes
    - **Mantenimiento:** Actualiza horarios regularmente según necesidades

    ### 🔄 Exportación

    - **PDF:** Genera reportes en formato PDF
    - **Excel:** Exporta datos para análisis externo
    - **Impresión:** Imprime horarios para distribución física

    ### ⚠️ Consideraciones Importantes

    - Los cambios se guardan automáticamente
    - Verifica conflictos antes de hacer cambios
    - Respeta los horarios de almuerzo y recreos
    - Considera la carga académica de los profesores
    """)

def show_teachers_manual():
    """Manual de la sección de profesores"""
    st.header("👨‍🏫 Gestión de Profesores")

    st.markdown("""
    ### ¿Qué puedes hacer en esta sección?

    El módulo de **Profesores** te permite administrar toda la información relacionada
    con el personal docente, incluyendo datos personales, asignaciones académicas y
    seguimiento de carga de trabajo.

    ### 🎯 Funcionalidades Principales

    #### 1. **Gestión de Datos Personales**
    - Registrar información básica de profesores
    - Mantener datos de contacto actualizados
    - Gestionar especialidades y certificaciones
    - Seguimiento de información laboral

    #### 2. **Asignación de Materias**
    - Asignar materias a profesores
    - Gestionar carga académica
    - Distribuir grupos de estudiantes
    - Optimizar asignaciones

    #### 3. **Seguimiento de Carga**
    - Monitorear horas de clase por profesor
    - Identificar sobrecarga académica
    - Balancear distribución de trabajo
    - Generar reportes de carga

    #### 4. **Evaluación y Rendimiento**
    - Seguimiento de desempeño docente
    - Registro de evaluaciones
    - Análisis de estadísticas
    - Generación de reportes

    ### 🛠️ Cómo usar el módulo

    #### **Paso 1: Agregar Nuevo Profesor**
    1. Haz clic en "➕ Agregar Profesor"
    2. Completa todos los campos obligatorios:
       - **Nombre completo**
       - **Cédula** (única)
       - **Email** (opcional)
       - **Teléfono** (opcional)
       - **Especialidad**
    3. Haz clic en "Guardar"

    #### **Paso 2: Editar Información**
    1. En la tabla de profesores, haz clic en la fila del profesor
    2. Modifica los campos necesarios
    3. Los cambios se guardan automáticamente

    #### **Paso 3: Asignar Materias**
    1. Selecciona el profesor en la lista
    2. En la sección "Materias Asignadas":
       - Haz clic en "➕ Agregar Materia"
       - Selecciona la materia del menú desplegable
       - Asigna grupos si es necesario
       - Guarda la asignación

    #### **Paso 4: Ver Carga Académica**
    1. Selecciona un profesor
    2. Revisa la sección "Carga Académica"
    3. Analiza las estadísticas mostradas:
       - Total de horas por semana
       - Número de grupos
       - Materias asignadas

    ### 📊 Información Mostrada

    #### **Datos Personales:**
    - Nombre completo
    - Cédula de identidad
    - Información de contacto
    - Especialidad académica
    - Fecha de ingreso

    #### **Carga Académica:**
    - Materias asignadas
    - Grupos de estudiantes
    - Horas de clase por semana
    - Distribución de carga

    #### **Estadísticas:**
    - Total de estudiantes
    - Promedio de calificaciones
    - Asistencia promedio
    - Rendimiento general

    ### 💡 Consejos de Uso

    - **Mantenimiento:** Actualiza datos regularmente
    - **Balance:** Distribuye carga académica equitativamente
    - **Comunicación:** Mantén información de contacto actualizada
    - **Seguimiento:** Revisa estadísticas periódicamente

    ### 🔄 Exportación

    - **Lista de profesores** en Excel
    - **Reportes de carga** académica
    - **Estadísticas** de rendimiento
    - **Información** de contacto

    ### ⚠️ Consideraciones Importantes

    - La cédula debe ser única para cada profesor
    - Verifica la carga académica antes de asignar nuevas materias
    - Mantén información de contacto actualizada
    - Revisa regularmente las estadísticas de rendimiento
    """)

def show_classrooms_manual():
    """Manual de la sección de aulas"""
    st.header("🏫 Gestión de Aulas")

    st.markdown("""
    ### ¿Qué puedes hacer en esta sección?

    El módulo de **Aulas** te permite buscar, visualizar y editar la información de todos los espacios físicos del colegio, incluyendo aulas regulares, laboratorios, talleres y otros espacios educativos.

    ### 🎯 Funcionalidades Principales

    #### 1. **Búsqueda avanzada de aulas**
    - Busca cualquier aula por número o nombre (la búsqueda ignora tildes, mayúsculas y espacios)
    - Si hay varias coincidencias, selecciona una sola para ver el detalle
    - Si solo hay una coincidencia, se muestra directamente

    #### 2. **Visualización de clases asociadas**
    - Consulta todas las clases asignadas a un aula (grupo, día, hora, materia, profesor)
    - Visualización clara y exportación a CSV

    #### 3. **Edición de nombre de aula**
    - Cambia el nombre de cualquier aula y se actualizará en todo el sistema
    - Evita duplicados y mantiene la información sincronizada

    ### 🛠️ Cómo usar el módulo

    1. Escribe el número o nombre del aula en el campo de búsqueda
    2. Si hay varias coincidencias, selecciona el aula deseada de la lista
    3. Visualiza todas las clases asociadas a esa aula en una tabla
    4. Si lo deseas, cambia el nombre del aula y haz clic en "Actualizar nombre de aula"
    5. Puedes exportar la información de clases asociadas a CSV

    ### 💡 Consejos de Uso

    - Usa la búsqueda flexible para encontrar aulas rápidamente
    - Mantén los nombres de aula consistentes para evitar confusiones
    - Revisa las clases asociadas antes de cambiar el nombre de un aula
    - Exporta la información para reportes o planificación

    ### ⚠️ Consideraciones Importantes

    - Los cambios de nombre de aula afectan a todas las clases asociadas
    - Si no encuentras un aula, revisa la ortografía o usa solo parte del nombre
    - La búsqueda es insensible a tildes, mayúsculas y espacios
    """)

def show_grades_manual():
    """Manual de la sección de notas"""
    st.header("📊 Sistema de Gestión Académica")

    st.markdown("""
    ### ¿Qué puedes hacer en esta sección?

    El módulo de **Notas** es el corazón del sistema académico, permitiendo gestionar
    completamente las calificaciones, asistencia y evaluación del rendimiento estudiantil
    con herramientas avanzadas de análisis y reportes.

    ### 🎯 Funcionalidades Principales

    #### 1. **Gestión de Estudiantes**
    - Registrar estudiantes nuevos
    - Mantener datos actualizados
    - Gestionar grupos de estudiantes
    - Seguimiento de información personal

    #### 2. **Registro de Asistencia**
    - Marcar asistencia diaria
    - Registrar tardanzas
    - Calcular porcentajes de asistencia
    - Generar reportes de asistencia

    #### 3. **Sistema de Evaluaciones**
    - Crear diferentes tipos de evaluación
    - Registrar calificaciones
    - Calcular promedios automáticamente
    - Análisis detallado por estudiante

    #### 4. **Cálculo de Calificaciones**
    - Aplicar ponderaciones personalizables
    - Calcular notas finales automáticamente
    - Generar reportes de rendimiento
    - Análisis estadístico completo

    ### 🛠️ Cómo usar el módulo

    #### **Paso 1: Configurar Ponderaciones**
    1. En la sección "⚙️ Configuración de Ponderaciones":
       - Ajusta los porcentajes para cada componente
       - Asegúrate de que sumen 100%
       - Guarda la configuración

    #### **Paso 2: Agregar Estudiantes**
    1. Ve a la pestaña "👥 Estudiantes"
    2. Completa el formulario:
       - **ID Estudiante** (único)
       - **Cédula** (única)
       - **Nombre Completo**
    3. Haz clic en "Agregar"

    #### **Paso 3: Registrar Asistencia**
    1. Ve a la pestaña "📅 Asistencia"
    2. Selecciona el mes deseado
    3. Para cada estudiante y fecha:
       - ✅ **Asistió**
       - ❌ **No Asistió**
       - ⚠️ **Tardanza**
    4. Haz clic en "💾 Guardar Cambios"

    #### **Paso 4: Gestionar Evaluaciones**
    1. Ve a la pestaña "📝 Evaluaciones"
    2. Selecciona el tipo de evaluación:
       - **Tareas**
       - **Proyecto**
       - **Prueba**
       - **Portafolio**
       - **Trabajo Cotidiano**
    3. Para agregar nueva evaluación:
       - Ingresa nombre y fecha
       - Haz clic en "➕ Agregar"
    4. Para registrar notas:
       - Completa las calificaciones en la tabla
       - Haz clic en "💾 Guardar"

    #### **Paso 5: Ver Calificaciones Finales**
    1. Ve a la pestaña "📊 Calificaciones"
    2. Revisa la tabla de calificaciones finales
    3. Analiza las estadísticas mostradas
    4. Exporta reportes si es necesario

    ### 📊 Componentes de Evaluación

    | Componente | Descripción | Ponderación Típica |
    |------------|-------------|-------------------|
    | 📅 **Asistencia** | Asistencia a clases | 10% |
    | 📝 **Tareas** | Trabajos asignados | 10% |
    | 🎯 **Proyecto** | Proyectos especiales | 15% |
    | 📋 **Prueba** | Exámenes escritos | 20% |
    | 📁 **Portafolio** | Recopilación de trabajos | 10% |
    | 💼 **Trabajo Cotidiano** | Participación diaria | 35% |

    ### 📈 Interpretación de Calificaciones

    | Rango | Calificación | Descripción |
    |-------|--------------|-------------|
    | 90-100 | 🏆 **Excelente** | Rendimiento sobresaliente |
    | 80-89 | 👍 **Bueno** | Rendimiento satisfactorio |
    | 70-79 | ⚠️ **Regular** | Rendimiento aceptable |
    | 0-69 | ❌ **Deficiente** | Necesita mejorar |

    ### 💡 Consejos de Uso

    - **Configuración:** Ajusta ponderaciones según necesidades del curso
    - **Consistencia:** Registra asistencia y notas regularmente
    - **Análisis:** Revisa estadísticas para identificar tendencias
    - **Comunicación:** Comparte reportes con estudiantes y padres

    ### 🔄 Exportación

    - **Reportes completos** en Excel
    - **Calificaciones finales** por estudiante
    - **Estadísticas** de rendimiento
    - **Asistencia** detallada por mes

    ### ⚠️ Consideraciones Importantes

    - Las ponderaciones deben sumar 100%
    - Registra asistencia diariamente
    - Verifica datos antes de exportar
    - Mantén respaldos de información importante
    """)

def show_communication_manual():
    """Manual de la sección de comunicación"""
    st.header("📱 Bot de WhatsApp")

    st.markdown("""
    ### ¿Qué puedes hacer en esta sección?

    El módulo de **Comunicación** integra un bot de WhatsApp Business API que permite
    enviar mensajes automáticos a estudiantes, padres y profesores, facilitando la
    comunicación institucional de manera eficiente y profesional.

    ### 🎯 Funcionalidades Principales

    #### 1. **Gestión de Contactos**
    - Registrar contactos de estudiantes y padres
    - Organizar contactos por roles
    - Mantener información actualizada
    - Gestionar listas de distribución

    #### 2. **Envío de Mensajes**
    - Enviar mensajes individuales
    - Programar mensajes para el futuro
    - Usar plantillas predefinidas
    - Mensajes personalizados

    #### 3. **Tipos de Mensajes**
    - Recordatorios de tareas
    - Avisos de ruta escolar
    - Recordatorios médicos
    - Mensajes personalizados

    #### 4. **Configuración de WhatsApp**
    - Configurar credenciales de API
    - Verificar conexión
    - Gestionar tokens de acceso
    - Monitorear estado del servicio

    ### 🛠️ Cómo usar el módulo

    #### **Paso 1: Configurar WhatsApp Business API**
    1. Ve a la pestaña "⚙️ Configuración"
    2. Sigue la guía de configuración:
       - Crea cuenta en Meta Business Suite
       - Configura WhatsApp Business
       - Obtén credenciales de API
    3. Ingresa las credenciales:
       - **API Token**
       - **Phone Number ID**
    4. Haz clic en "💾 Guardar Configuración"

    #### **Paso 2: Gestionar Contactos**
    1. En "👥 Gestión de Contactos":
       - Ingresa **Nombre** del contacto
       - Agrega **Teléfono** (formato: 506xxxxxxxx)
       - Selecciona **Rol** (Estudiante, Padre, Profesor)
       - Haz clic en "➕ Agregar Contacto"

    #### **Paso 3: Enviar Mensajes**
    1. Selecciona el contacto o ingresa número nuevo
    2. Elige el tipo de mensaje:
       - **Tarea pendiente:** Incluye materia y fecha
       - **Recordatorio de ruta:** Número de ruta y hora
       - **Recordatorio médico:** Medicamento y hora
       - **Mensaje personalizado:** Texto libre
    3. Revisa la vista previa del mensaje
    4. Elige cuándo enviar:
       - **Enviar ahora**
       - **Programar para más tarde**
    5. Haz clic en "📤 Enviar mensaje"

    ### 📱 Tipos de Mensajes Disponibles

    #### **📌 Tarea Pendiente**
    ```
    📌 Tarea pendiente: [Materia], para el [Fecha]
    ```

    #### **🚌 Recordatorio de Ruta**
    ```
    🚌 Ruta #[Número] pasará a las [Hora]
    ```

    #### **💊 Recordatorio Médico**
    ```
    💊 Recuerda tomar [Medicamento] a las [Hora]
    ```

    #### **📝 Mensaje Personalizado**
    - Texto libre personalizado
    - Incluye emojis y formato

    ### 💡 Consejos de Uso

    - **Horarios:** Envía mensajes en horarios apropiados
    - **Personalización:** Usa nombres y detalles específicos
    - **Programación:** Aprovecha la función de programación
    - **Seguimiento:** Verifica que los mensajes se envíen correctamente

    ### 🔒 Seguridad y Privacidad

    - **Credenciales seguras:** Nunca compartas tu API Token
    - **Consentimiento:** Respeta las preferencias de contacto
    - **Políticas:** Cumple con las políticas de WhatsApp
    - **Límites:** Respeta los límites de envío de mensajes

    ### ⚠️ Consideraciones Importantes

    - Los números deben estar en formato internacional
    - Los usuarios deben optar por recibir mensajes
    - Hay límites en el número de mensajes diarios
    - Verifica la configuración antes de enviar mensajes masivos

    ### 🔧 Solución de Problemas

    **Mensaje no se envía:**
    - Verifica credenciales de API
    - Confirma que el número esté correcto
    - Revisa límites de envío

    **Error de configuración:**
    - Revisa la guía de configuración
    - Verifica credenciales en Meta Business Suite
    - Contacta soporte técnico si es necesario
    """)

def show_faq_section():
    """Sección de preguntas frecuentes"""
    st.header("❓ Preguntas Frecuentes")

    st.markdown("""
    ### 🤔 Preguntas Generales

    #### **¿Cómo cambio mi contraseña?**
    Actualmente, las contraseñas se gestionan a través del administrador del sistema.
    Contacta al administrador para solicitar un cambio de contraseña.

    #### **¿Puedo usar el sistema desde mi teléfono?**
    Sí, el sistema es completamente responsive y funciona en dispositivos móviles,
    tablets y computadoras.

    #### **¿Se guardan mis datos automáticamente?**
    Sí, la mayoría de los cambios se guardan automáticamente. Sin embargo,
    siempre verifica que los datos se hayan guardado correctamente.

    #### **¿Puedo exportar mis datos?**
    Sí, la mayoría de módulos incluyen opciones de exportación a Excel y PDF.

    ### 📅 Horarios

    #### **¿Cómo agrego una nueva materia?**
    Las materias se configuran a nivel de sistema. Contacta al administrador
    para agregar nuevas materias al sistema.

    #### **¿Puedo cambiar un horario ya asignado?**
    Sí, activa el "Modo Edición" en la barra lateral y haz clic en la celda
    que deseas modificar.

    #### **¿Cómo detecto conflictos en los horarios?**
    Usa la vista "⚠️ Detector de Conflictos" que identifica automáticamente
    problemas en los horarios.

    ### 👨‍🏫 Profesores

    #### **¿Cómo agrego un nuevo profesor?**
    Ve al módulo de Profesores, haz clic en "➕ Agregar Profesor" y completa
    todos los campos obligatorios.

    #### **¿Puedo ver la carga académica de un profesor?**
    Sí, selecciona el profesor en la lista y revisa la sección "Carga Académica".

    ### 🏫 Aulas

    #### **¿Cómo reporto un problema en un aula?**
    Selecciona el aula, ve a "Estado y Mantenimiento" y reporta el problema
    con los detalles correspondientes.

    #### **¿Puedo reservar un aula para un evento especial?**
    Sí, usa la función de reservas en el módulo de Aulas para eventos especiales.

    ### 📊 Notas

    #### **¿Cómo cambio las ponderaciones de evaluación?**
    En el módulo de Notas, expande "⚙️ Configuración de Ponderaciones" y ajusta
    los porcentajes según tus necesidades.

    #### **¿Puedo agregar un nuevo tipo de evaluación?**
    Los tipos de evaluación están predefinidos en el sistema. Contacta al administrador
    si necesitas agregar nuevos tipos.

    #### **¿Cómo registro asistencia de manera masiva?**
    En la pestaña de Asistencia, puedes marcar la asistencia de todos los estudiantes
    de una fecha específica de manera simultánea.

    ### 📱 Comunicación

    #### **¿Cómo configuro WhatsApp Business API?**
    Sigue la guía detallada en la pestaña "⚙️ Configuración" del módulo de Comunicación.

    #### **¿Puedo enviar mensajes a múltiples contactos?**
    Actualmente, los mensajes se envían de forma individual. Para mensajes masivos,
    contacta al administrador.

    #### **¿Hay límites en el envío de mensajes?**
    Sí, WhatsApp Business API tiene límites diarios. Revisa la documentación oficial
    para más detalles.

    ### 🔧 Problemas Técnicos

    #### **La página no carga correctamente**
    - Verifica tu conexión a internet
    - Intenta refrescar la página
    - Limpia el caché del navegador
    - Contacta soporte técnico

    #### **No puedo iniciar sesión**
    - Verifica usuario y contraseña
    - Asegúrate de que tu cuenta esté activa
    - Contacta al administrador

    #### **Los datos no se guardan**
    - Verifica tu conexión a internet
    - Intenta guardar nuevamente
    - Contacta soporte técnico si persiste

    ### 📞 Contacto y Soporte

    **Para problemas técnicos:**
    - Email: soporte@ctplaspalmitas.edu.cr
    - Teléfono: [Número de soporte]
    - Horario: Lunes a Viernes, 7:00 AM - 4:00 PM

    **Para solicitudes administrativas:**
    - Contacta directamente al administrador del sistema
    - O envía un mensaje a través del módulo de Comunicación

    ---

    ### 📝 Notas Importantes

    - Este manual se actualiza regularmente
    - Consulta la sección correspondiente para información detallada
    - Mantén tu información de contacto actualizada
    - Reporta problemas técnicos inmediatamente
    """)

    # Botón para descargar manual completo
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1]) # type: ignore

    with col2:
        if st.button("📥 Descargar Manual Completo", type="primary", use_container_width=True):
            st.info("""
            **Funcionalidad en desarrollo**

            Próximamente podrás descargar el manual completo en formato PDF
            con toda la información detallada de cada módulo.
            """)
