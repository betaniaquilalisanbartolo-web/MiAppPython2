import streamlit as st
import sqlite3
import pandas as pd
import datetime

DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tablas principales
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
    c.execute('''CREATE TABLE IF NOT EXISTS cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT UNIQUE, leader TEXT
    )''')
    # Tabla de líderes
    c.execute('''CREATE TABLE IF NOT EXISTS leaders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT
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

init_db()

# --- LOGIN ---
st.sidebar.subheader("🔑 Ingreso de Líder")
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM leaders WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success(f"Bienvenido líder {username}")
        else:
            st.error("Usuario o contraseña incorrectos")
else:
    st.sidebar.success(f"Conectado como {st.session_state['username']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state['logged_in'] = False

# --- CONTENIDO SOLO SI ESTÁ LOGUEADO ---
if st.session_state['logged_in']:
    st.set_page_config(page_title="Gestión de Iglesia", layout="wide")
    st.title("⛪ Sistema de Gestión de Células y Miembros")

    menu = st.sidebar.selectbox(
        "Selecciona una sección",
        ["➕ Registro de Célula", "👥 Registro de Miembros por Célula", "📝 Formularios", "📊 Panel de Control y Reportes"]
    )

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

    # ================= REGISTRO DE MIEMBROS POR CÉLULA =================
    elif menu == "👥 Registro de Miembros por Célula":
        st.subheader("Registrar Miembros en una Célula")
        lista_celulas = obtener_nombres_celulas()
        with st.form("form_miembros_celula", clear_on_submit=True):
            cell = st.selectbox("Selecciona la Célula", lista_celulas)
            full_name = st.text_input("Nombre Completo del Miembro")
            sex = st.selectbox("Sexo", ["Masculino", "Femenino"])
            discipleship_type = st.text_input("Tipo de Discipulado")
            ministry = st.selectbox("Ministerio", ["Alabanza", "Ujieres", "Niños", "Intercesión", "Media", "Ninguno"])

            if st.form_submit_button("Guardar Miembro"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO members_stats (full_name, cell, sex, discipleship_type, ministry) VALUES (?, ?, ?, ?, ?)''',
                          (full_name, cell, sex, discipleship_type, ministry))
                conn.commit()
                conn.close()
                st.success(f"¡Miembro '{full_name}' registrado en la célula '{cell}'!")

    # ================= FORMULARIOS =================
    elif menu == "📝 Formularios":
        # Aquí van tus pestañas de Reporte de Célula, Nuevo Convertido y Miembro
        st.info("Aquí se mantienen los formularios que ya construimos en pasos anteriores.")

    # ================= PANEL DE CONTROL =================
    elif menu == "📊 Panel de Control y Reportes":
        st.subheader("📊 Panel de Análisis Automático de la Iglesia")
        conn = sqlite3.connect(DB_PATH)
        df_cell = pd.read_sql_query("SELECT * FROM cell_reports", conn)
        df_converts = pd.read_sql_query("SELECT * FROM new_converts", conn)
        df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)
        conn.close()

        hoy = datetime.date.today()
        mes_actual = hoy.month
        anio_actual = hoy.year

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

        total_ofrenda_mes = df_cell_mes['offering'].sum() if not df_cell_mes.empty else 0.0
        total_convertidos_mes = len(df_converts_mes) if not df_converts_mes.empty else 0

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        with kpi1:
            st.metric("Ofrenda del Mes", f"${total_ofrenda_mes:,.2f}")

        with kpi2:
            st.metric("Convertidos del Mes", f"{total_convertidos_mes} personas")

        with kpi3:
            miembros_activos = len(df_members[df_members['status'] == 'activo']) if not df_members.empty else 0
            st.metric("Miembros Activos", f"{miembros_activos} personas")

        with kpi4:
            total_asistencia = (
                df_cell_mes['adults'].sum() + df_cell_mes['youth'].sum() + df_cell_mes['children'].sum()
            ) if not df_cell_mes.empty else 0
            st.metric("Asistencia del Mes", f"{total_asistencia} asistencias")

        st.markdown("### 📌 Reportes de Células")
        st.dataframe(df_cell_mes)

        st.markdown("### 👤 Nuevos Convertidos")
        st.dataframe(df_converts_mes)

        st.markdown("### 📈 Miembros")
        st.dataframe(df_members)

else:
    st.warning("Por favor ingresa con tu usuario y contraseña para acceder al sistema.")
