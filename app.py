import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Reportes de células
    c.execute('''CREATE TABLE IF NOT EXISTS cell_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, meeting_date TEXT,
        adults INTEGER, youth INTEGER, children INTEGER, friends INTEGER, visits INTEGER,
        house_leader TEXT, biblical_theme TEXT, central_text TEXT, offering REAL,
        needs TEXT, spiritual_level TEXT, attendance_level INTEGER
    )''')
    # Nuevos convertidos
    c.execute('''CREATE TABLE IF NOT EXISTS new_converts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, contact TEXT, address TEXT,
        birth_date TEXT, age INTEGER, status TEXT, conversion_date TEXT,
        decision_type TEXT, assigned_cell TEXT, observation TEXT
    )''')
    # Estadísticas de miembros
    c.execute('''CREATE TABLE IF NOT EXISTS members_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, cell TEXT, sex TEXT,
        growth_eval INTEGER, discipleship_type TEXT, ministry TEXT, status TEXT DEFAULT 'activo'
    )''')
    # Registro de células
    c.execute('''CREATE TABLE IF NOT EXISTS cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT UNIQUE, leader TEXT
    )''')
    conn.commit()
    conn.close()

def obtener_nombres_celulas():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT cell_name FROM cells")
    filas = c.fetchall()
    conn.close()
    lista_celulas = [f[0] for f in filas]
    if not lista_celulas:
        lista_celulas = ["Célula Central", "Célula de Jóvenes", "Célula de Damas"]
    return lista_celulas

menu = st.sidebar.selectbox(
    "Selecciona una sección",
    ["➕ Registro de Célula", "👥 Registro de Miembros por Célula", "📝 Formularios", "📊 Panel de Control y Reportes"]
)


init_db()

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Gestión de Iglesia", layout="wide")
st.title("⛪ Sistema de Gestión de Células y Miembros")

menu = st.sidebar.selectbox("Selecciona una sección", ["➕ Registro de Célula", "📝 Formularios", "📊 Panel de Control y Reportes"])

# ================= REGISTRO DE CÉLULA =================
if menu == "➕ Registro de Célula":
    st.subheader("Registrar Nueva Célula")
    with st.form("form_registro_celula", clear_on_submit=True):
        cell_name = st.text_input("Nombre de la Célula")
        leader = st.text_input("Nombre del Líder")
        if st.form_submit_button("Guardar Célula"):
            if cell_name.strip():
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO cells (cell_name, leader) VALUES (?, ?)", (cell_name.strip(), leader))
                    conn.commit()
                    st.success(f"¡Célula '{cell_name}' registrada exitosamente!")
                except sqlite3.IntegrityError:
                    st.error("Ya existe una célula con ese nombre.")
                conn.close()
            else:
                st.error("El nombre de la célula no puede estar vacío.")

# ================= FORMULARIOS =================
elif menu == "📝 Formularios":
    pestana1, pestana2, pestana3 = st.tabs(["📌 Reporte de Célula", "👤 Nuevo Convertido", "📈 Miembro"])
    
    # --- Reporte de célula ---
    with pestana1:
        st.subheader("Registrar Reporte de Célula")
        lista_opciones_celulas = obtener_nombres_celulas()
        with st.form("form_celula", clear_on_submit=True):
            celula_seleccionada = st.selectbox("Selecciona el Nombre de la Célula", lista_opciones_celulas)
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
            spiritual_level = st.selectbox("Nivel Espiritual", ["Oración", "Gozo", "Comunión", "Adoración"])
            attendance_level = st.slider("Nivel de Asistencia", 1, 10, 5)

            if st.form_submit_button("Guardar Reporte"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO cell_reports (cell_name, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (celula_seleccionada, str(meeting_date), adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level))
                conn.commit()
                conn.close()
                st.success(f"¡Reporte de la célula '{celula_seleccionada}' guardado exitosamente!")

    # --- Nuevo convertido ---
    with pestana2:
        st.subheader("Registrar Nuevo Convertido")
        lista_celulas_convertidos = obtener_nombres_celulas()
        with st.form("form_convertido", clear_on_submit=True):
            full_name = st.text_input("Nombre Completo")
            contact = st.text_input("Contacto / Teléfono")
            address = st.text_area("Dirección")
            birth_date = st.date_input("Fecha de Nacimiento")
            age = st.number_input("Edad", min_value=0, step=1)
            status = st.text_input("Estado", value="Nuevo")
            conversion_date = st.date_input("Fecha de Conversión")
            decision_type = st.selectbox("Tipo de Decisión", ["Primera vez", "Reconciliación", "Petición de Oración"])
            assigned_cell = st.selectbox("Célula Asignada", lista_celulas_convertidos)
            observation = st.text_area("Observaciones")

            if st.form_submit_button("Guardar Convertido"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO new_converts (full_name, contact, address, birth_date, age, status, conversion_date, decision_type, assigned_cell, observation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (full_name, contact, address, str(birth_date), age, status, str(conversion_date), decision_type, assigned_cell, observation))
                conn.commit()
                conn.close()
                st.success("¡Nuevo convertido guardado con éxito!")

    # --- Miembro ---
    with pestana3:
        st.subheader("Estadísticas de Miembro")
        lista_celulas_miembros = obtener_nombres_celulas()
        with st.form("form_miembro", clear_on_submit=True):
            full_name = st.text_input("Nombre Completo del Miembro")
            cell = st.selectbox("Célula a la que Pertenece", lista_celulas_miembros)
            sex = st.selectbox("Sexo", ["Masculino", "Femenino"])
            growth_eval = st.slider("Evaluación de Crecimiento", 1, 10, 5)
            discipleship_type = st.text_input("Tipo de Discipulado")
            ministry = st.selectbox("Ministerio", ["Alabanza", "Ujieres", "Niños", "Intercesión", "Media", "Ninguno"])

          # ================= PANEL DE CONTROL =================
elif menu == "📊 Panel de Control y Reportes":
    st.subheader("📊 Panel de Análisis Automático de la Iglesia")
    conn = sqlite3.connect(DB_PATH)
    df_cell = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    df_converts = pd.read_sql_query("SELECT * FROM new_converts", conn)
    df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)
    conn.close()

    import datetime

hoy = datetime.date.today()
mes_actual = hoy.month
anio_actual = hoy.year

# Convertir columnas de fecha solo si existen y no están vacías
if not df_cell.empty and 'meeting_date' in df_cell.columns:
    df_cell['meeting_date'] = pd.to_datetime(df_cell['meeting_date'], errors='coerce')
    df_cell_mes = df_cell[(df_cell['meeting_date'].dt.month == mes_actual) & (df_cell['meeting_date'].dt.year == anio_actual)]
else:
    df_cell_mes = pd.DataFrame()

if not df_converts.empty and 'conversion_date' in df_converts.columns:
    df_converts['conversion_date'] = pd.to_datetime(df_converts['conversion_date'], errors='coerce')
    df_converts_mes = df_converts[(df_converts['conversion_date'].dt.month == mes_actual) & (df_converts['conversion_date'].dt.year == anio_actual)]
else:
    df_converts_mes = pd.DataFrame()

with kpi1:
    st.metric("Ofrenda del Mes", f"${total_ofrenda_mes:,.2f}")

with kpi2:
    st.metric("Convertidos del Mes", f"{total_convertidos_mes} personas")


# KPIs mensuales
total_ofrenda_mes = df_cell_mes['offering'].sum() if not df_cell_mes.empty else 0.0
total_convertidos_mes = len(df_converts_mes) if not df_converts_mes.empty else 0


    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        total_ofrenda = df_cell['offering'].sum() if not df_cell.empty else 0.0
        st.metric("Total Ofrendas", f"${total_ofrenda:,.2f}")

    with kpi2:
        total_nuevos = len(df_converts) if not df_converts.empty else 0
        st.metric("Nuevos Convertidos", f"{total_nuevos} personas")

    with kpi3:
        miembros_activos = len(df_members[df_members['status'] == 'activo']) if not df_members.empty else 0
        st.metric("Miembros Activos", f"{miembros_activos} personas")

    with kpi4:
        total_asistencia = (
            df_cell['adults'].sum() + df_cell['youth'].sum() + df_cell['children'].sum()
        ) if not df_cell.empty else 0
        st.metric("Impacto Total Asistencia", f"{total_asistencia} asistencias")

    # Mostrar tablas
    st.markdown("### 📌 Reportes de Células")
    st.dataframe(df_cell)

    st.markdown("### 👤 Nuevos Convertidos")
    st.dataframe(df_converts)

    st.markdown("### 📈 Miembros")
    st.dataframe(df_members)

import datetime

# Obtener mes y año actual
hoy = datetime.date.today()
mes_actual = hoy.month
anio_actual = hoy.year

# Convertir columnas de fecha a datetime
df_cell['meeting_date'] = pd.to_datetime(df_cell['meeting_date'], errors='coerce')
df_converts['conversion_date'] = pd.to_datetime(df_converts['conversion_date'], errors='coerce')

# Filtrar registros del mes actual
df_cell_mes = df_cell[(df_cell['meeting_date'].dt.month == mes_actual) & (df_cell['meeting_date'].dt.year == anio_actual)]
df_converts_mes = df_converts[(df_converts['conversion_date'].dt.month == mes_actual) & (df_converts['conversion_date'].dt.year == anio_actual)]

# KPIs mensuales
total_ofrenda_mes = df_cell_mes['offering'].sum() if not df_cell_mes.empty else 0.0
total_convertidos_mes = len(df_converts_mes) if not df_converts_mes.empty else 0

