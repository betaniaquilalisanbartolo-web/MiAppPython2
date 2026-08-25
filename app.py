import sqlite3
from io import BytesIO
import pandas as pd
import streamlit as st

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_PATH = "database.db"

def get_connection():
    """Retorna una nueva conexión SQLite configurada."""
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS cell_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, meeting_date TEXT,
            adults INTEGER, youth INTEGER, children INTEGER, friends INTEGER, visits INTEGER,
            house_leader TEXT, biblical_theme TEXT, central_text TEXT, offering REAL,
            needs TEXT, spiritual_level TEXT, attendance_level INTEGER
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS new_converts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, contact TEXT, address TEXT,
            birth_date TEXT, age INTEGER, status TEXT, conversion_date TEXT,
            decision_type TEXT, assigned_cell TEXT, observation TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS members_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, cell TEXT, sex TEXT,
            growth_eval INTEGER, discipleship_type TEXT, ministry TEXT, status TEXT DEFAULT 'activo'
        )''')
        conn.commit()

def obtener_nombres_celulas():
    """Obtiene la lista de nombres únicos de células registradas."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT DISTINCT cell_name FROM cell_reports WHERE cell_name IS NOT NULL AND cell_name != ''")
        lista_celulas = [f[0] for f in c.fetchall()]

    if not lista_celulas:
        lista_celulas = ["Célula Central", "Célula de Jóvenes", "Célula de Damas"]
    return lista_celulas

init_db()

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Gestión de Iglesia", layout="wide")
st.title("⛪ Sistema de Gestión de Células y Miembros")

menu = st.sidebar.selectbox("Selecciona una sección", ["📝 Formularios", "📊 Panel de Control y Reportes"])

if menu == "📝 Formularios":
    pestana1, pestana2, pestana3 = st.tabs(["📌 Reporte de Célula", "👤 Nuevo Convertido", "📈 Miembro"])
    
    with pestana1:
        st.subheader("Registrar Reporte de Célula")
        opciones_celulas = obtener_nombres_celulas() + ["➕ Registrar Nueva Célula"]
        
        with st.form("form_celula", clear_on_submit=True):
            celula_seleccionada = st.selectbox("Selecciona el Nombre de la Célula", opciones_celulas)
            nombre_nueva_celula = st.text_input("Si seleccionaste 'Registrar Nueva Célula', escribe su nombre aquí:")
            meeting_date = st.date_input("Fecha de Reunión")
            
            col1, col2, col3 = st.columns(3)
            adults = col1.number_input("Adultos", min_value=0, step=1)
            youth = col2.number_input("Jóvenes", min_value=0, step=1)
            children = col3.number_input("Niños", min_value=0, step=1)
            friends = col1.number_input("Amigos", min_value=0, step=1)
            visits = col2.number_input("Visitas", min_value=0, step=1)
            
            house_leader = st.text_input("Líder de Casa")
            biblical_theme = st.text_input("Tema Bíblico")
            central_text = st.text_input("Texto Central")
            offering = st.number_input("Ofrenda", min_value=0.0, step=1.0)
            needs = st.text_area("Necesidades")
            spiritual_level = st.selectbox("Nivel Espiritual", ["Bajo", "Medio", "Alto"])
            attendance_level = st.slider("Nivel de Asistencia", 1, 10, 5)
            
            if st.form_submit_button("Guardar Reporte"):
                cell_name_final = nombre_nueva_celula.strip() if celula_seleccionada == "➕ Registrar Nueva Célula" else celula_seleccionada

                if not cell_name_final:
                    st.error("Por favor, introduce un nombre válido para la célula.")
                else:
                    with get_connection() as conn:
                        c = conn.cursor()
                        c.execute('''INSERT INTO cell_reports (cell_name, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level) 
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                  (cell_name_final, str(meeting_date), adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level))
                        conn.commit()
                    st.success(f"¡Reporte de la célula '{cell_name_final}' guardado exitosamente!")
                    st.rerun()

    with pestana2:
        st.subheader("Registrar Nuevo Convertido")
        lista_celulas = obtener_nombres_celulas()
        
        with st.form("form_convertido", clear_on_submit=True):
            full_name = st.text_input("Nombre Completo")
            contact = st.text_input("Contacto / Teléfono")
            address = st.text_area("Dirección")
            birth_date = st.date_input("Fecha de Nacimiento")
            age = st.number_input("Edad", min_value=0, step=1)
            status = st.text_input("Estado", value="Nuevo")
            conversion_date = st.date_input("Fecha de Conversión")
            decision_type = st.selectbox("Tipo de Decisión", ["Primera vez", "Reconciliación", "Petición de Oración"])
            assigned_cell = st.selectbox("Célula Asignada", lista_celulas)
            observation = st.text_area("Observaciones")
            
            if st.form_submit_button("Guardar Convertido"):
                with get_connection() as conn:
                    c = conn.cursor()
                    c.execute('''INSERT INTO new_converts (full_name, contact, address, birth_date, age, status, conversion_date, decision_type, assigned_cell, observation) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (full_name, contact, address, str(birth_date), age, status, str(conversion_date), decision_type, assigned_cell, observation))
                    conn.commit()
                st.success("¡Nuevo convertido guardado con éxito!")

    with pestana3:
        st.subheader("Estadísticas de Miembro")
        lista_celulas = obtener_nombres_celulas()
        
        with st.form("form_miembro", clear_on_submit=True):
            full_name = st.text_input("Nombre Completo del Miembro")
            cell = st.selectbox("Célula a la que Pertenece", lista_celulas)
            sex = st.selectbox("Sexo", ["Masculino", "Femenino"])
            growth_eval = st.slider("Evaluación de Crecimiento", 1, 10, 5)
            discipleship_type = st.text_input("Tipo de Discipulado")
            ministry = st.selectbox("Ministerio", ["Alabanza", "Ujieres", "Niños", "Intercesión", "Media", "Ninguno"])
            
            if st.form_submit_button("Guardar Estadísticas"):
                with get_connection() as conn:
                    c = conn.cursor()
                    c.execute('''INSERT INTO members_stats (full_name, cell, sex, growth_eval, discipleship_type, ministry) 
                                 VALUES (?, ?, ?, ?, ?, ?)''',
                              (full_name, cell, sex, growth_eval, discipleship_type, ministry))
                    conn.commit()
                st.success("¡Estadísticas de miembro guardadas!")

elif menu == "📊 Panel de Control y Reportes":
    st.subheader("📊 Panel de Análisis Automático de la Iglesia")
    
    with get_connection() as conn:
        df_cell = pd.read_sql_query("SELECT * FROM cell_reports", conn)
        df_converts = pd.read_sql_query("SELECT * FROM new_converts", conn)
        df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)

    # --- 1. TARJETAS MÉTRICAS AUTOMÁTICAS (KPIs) ---
    st.markdown("### 📈 Indicadores Clave del Sistema")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_ofrenda = df_cell['offering'].sum() if not df_cell.empty else 0.0
    total_nuevos = len(df_converts)
    miembros_activos = len(df_members[df_members['status'] == 'activo']) if not df_members.empty else 0
    total_asistencia = (df_cell['adults'].sum() + df_cell['youth'].sum() + df_cell['children'].sum()) if not df_cell.empty else 0

    kpi1.metric("Total Ofrendas", f"${total_ofrenda:,.2f}")
    kpi2.metric("Nuevos Convertidos", f"{total_nuevos} personas")
    kpi3.metric("Miembros Activos", f"{miembros_activos} personas")
    kpi4.metric("Impacto Total Asistencia", f"{total_asistencia} asistencias")

    st.markdown("---")

    # --- 2. ANÁLISIS GRÁFICO ---
    st.markdown("### 📊 Gráficos y Distribución")
    grafico1, grafico2 = st.columns(2)

    with grafico1:
        st.write("🏃‍♂️ **Asistencia Acumulada por Categoría**")
        if not df_cell.empty:
            data_asistencia = pd.DataFrame({
                'Categoría': ['Adultos', 'Jóvenes', 'Niños', 'Amigos', 'Visitas'],
                'Cantidad': [
                    df_cell['adults'].sum(), df_cell['youth'].sum(), df_cell['children'].sum(),
                    df_cell['friends'].sum(), df_cell['visits'].sum()
                ]
            })
            st.bar_chart(data=data_asistencia, x='Categoría', y='Cantidad')
        else:
            st.info("Agrega reportes de células para visualizar métricas de asistencia.")

    with grafico2:
        st.write("💰 **Ofrendas por Célula**")
        if not df_cell.empty:
            df_ofrendas = df_cell.groupby("cell_name")["offering"].sum().reset_index()
            st.bar_chart(data=df_ofrendas, x='cell_name', y='offering')
        else:
            st.info("No hay datos de ofrendas para mostrar.")

    st.markdown("---")

    # --- 3. DESCARGA DE REPORTES ---
    st.markdown("### 📥 Exportar Datos a Excel")
    if not df_cell.empty or not df_converts.empty or not df_members.empty:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_cell.to_excel(writer, sheet_name='Reportes Células', index=False)
            df_converts.to_excel(writer, sheet_name='Nuevos Convertidos', index=False)
            df_members.to_excel(writer, sheet_name='Miembros', index=False)
        
        st.download_button(
            label="📊 Descargar Reporte Completo (.xlsx)",
            data=buffer.getvalue(),
            file_name="Reporte_General_Iglesia.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
