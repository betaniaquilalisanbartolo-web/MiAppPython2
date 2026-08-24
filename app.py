import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "C:/Users/Pc/Desktop/MiAppPython/MiAppPython2/MiBaseDatos/database.db"

# --- Inicializar base de datos ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabla de células
    c.execute("""CREATE TABLE IF NOT EXISTS cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cell_name TEXT UNIQUE,
        leader TEXT
    )""")

    # Tabla de miembros
    c.execute("""CREATE TABLE IF NOT EXISTS members_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        age INTEGER,
        contact TEXT,
        cell TEXT,
        sex TEXT,
        discipleship_type TEXT,
        other_church TEXT,
        ingreso_date TEXT,
        ministry TEXT,
        status TEXT
    )""")

    # Tabla de convertidos
    c.execute("""CREATE TABLE IF NOT EXISTS new_converts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        age INTEGER,
        contact TEXT,
        address TEXT,
        assigned_cell TEXT,
        decision_type TEXT,
        conversion_date TEXT
    )""")

    # Tabla de reportes
    c.execute("""CREATE TABLE IF NOT EXISTS cell_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cell_name TEXT,
        meeting_date TEXT,
        adults INTEGER,
        youth INTEGER,
        children INTEGER,
        friends INTEGER,
        visits INTEGER,
        house_leader TEXT,
        biblical_theme TEXT,
        central_text TEXT,
        offering REAL,
        needs TEXT,
        spiritual_level TEXT,
        attendance_level INTEGER
    )""")

    # Tabla de descarriados
    c.execute("""CREATE TABLE IF NOT EXISTS descarriados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        age INTEGER,
        contact TEXT,
        cell TEXT,
        reason TEXT,
        date_reported TEXT
    )""")

    conn.commit()
    conn.close()

init_db()

# --- Menú principal ---
menu = st.sidebar.selectbox("Menú", [
    "🏠 Inicio",
    "👤 Registro de Miembros",
    "🙌 Registro de Convertidos",
    "📌 Reportes de Células",
    "📊 Panel de Control y Reportes",
    "⚙️ Administración"
])

# --- Inicio ---
if menu == "🏠 Inicio":
    st.subheader("Bienvenido al Sistema de Gestión de Iglesia")

# --- Registro de Miembros ---
elif menu == "👤 Registro de Miembros":
    st.subheader("Registro de Miembros")
    conn = sqlite3.connect(DB_PATH)
    cells = pd.read_sql_query("SELECT cell_name FROM cells", conn)
    conn.close()
    cell_options = cells['cell_name'].tolist() if not cells.empty else []

    with st.form("registro_miembro"):
        full_name = st.text_input("Nombre completo")
        age = st.number_input("Edad", min_value=0, max_value=120)
        contact = st.text_input("Contacto")
        cell = st.selectbox("Célula", cell_options)
        sex = st.selectbox("Sexo", ["Masculino", "Femenino"])
        discipleship_type = st.selectbox("¿En discipulado?", ["Sí", "No"])
        other_church = st.selectbox("¿Viene de otra iglesia?", ["Sí", "No"])
        ingreso_date = st.date_input("Fecha de ingreso")
        ministry = st.text_input("Ministerio")
        status = st.selectbox("Estado", ["activo", "inactivo"])
        submit = st.form_submit_button("Registrar Miembro")

        if submit and full_name:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""INSERT INTO members_stats 
                (full_name, age, contact, cell, sex, discipleship_type, other_church, ingreso_date, ministry, status)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (full_name, age, contact, cell, sex, discipleship_type, other_church, ingreso_date.strftime("%Y-%m-%d"), ministry, status))
            conn.commit()
            conn.close()
            st.success(f"Miembro {full_name} registrado en la célula {cell}")

# --- Registro de Convertidos ---
elif menu == "🙌 Registro de Convertidos":
    st.subheader("Registro de Nuevos Convertidos")
    conn = sqlite3.connect(DB_PATH)
    cells = pd.read_sql_query("SELECT cell_name FROM cells", conn)
    conn.close()
    cell_options = cells['cell_name'].tolist() if not cells.empty else []

    with st.form("registro_convertido"):
        full_name = st.text_input("Nombre completo")
        age = st.number_input("Edad", min_value=0, max_value=120)
        contact = st.text_input("Contacto")
        address = st.text_input("Dirección")
        assigned_cell = st.selectbox("Célula asignada", cell_options)
        decision_type = st.selectbox("Decisión", ["Aceptó a Cristo", "Reconciliación"])
        conversion_date = st.date_input("Fecha de conversión")
        submit = st.form_submit_button("Registrar Convertido")

        if submit and full_name:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""INSERT INTO new_converts 
                (full_name, age, contact, address, assigned_cell, decision_type, conversion_date)
                VALUES (?,?,?,?,?,?,?)""",
                (full_name, age, contact, address, assigned_cell, decision_type, conversion_date.strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            st.success(f"Convertido {full_name} registrado en la célula {assigned_cell}")

# --- Reportes de Células ---
elif menu == "📌 Reportes de Células":
    st.subheader("Registro de Reportes de Células")
    conn = sqlite3.connect(DB_PATH)
    cells = pd.read_sql_query("SELECT cell_name FROM cells", conn)
    conn.close()
    cell_options = cells['cell_name'].tolist() if not cells.empty else []

    with st.form("registro_reporte"):
        cell_name = st.selectbox("Célula", cell_options)
        meeting_date = st.date_input("Fecha de reunión")
        adults = st.number_input("Adultos", min_value=0)
        youth = st.number_input("Jóvenes", min_value=0)
        children = st.number_input("Niños", min_value=0)
        friends = st.number_input("Amigos", min_value=0)
        visits = st.number_input("Visitas", min_value=0)
        house_leader = st.text_input("Líder de casa")
        biblical_theme = st.text_input("Tema bíblico")
        central_text = st.text_input("Texto central")
        offering = st.number_input("Ofrenda", min_value=0.0)
        needs = st.text_area("Necesidades")
        spiritual_level = st.selectbox("Nivel espiritual", ["Alto", "Medio", "Bajo"])
        attendance_level = adults + youth + children + friends
        submit = st.form_submit_button("Registrar Reporte")

        if submit and cell_name:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""INSERT INTO cell_reports 
                (cell_name, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (cell_name, meeting_date.strftime("%Y-%m-%d"), adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level))
            conn.commit()
            conn.close()
            st.success(f"Reporte registrado para la célula {cell_name}")

# --- Panel de Control ---
elif menu == "📊 Panel de Control y Reportes":
    st.subheader("📊 Panel de Análisis Automático de la Iglesia")

    conn = sqlite3.connect(DB_PATH)
    df_cell = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    df_converts = pd.read_sql_query("SELECT * FROM new_converts", conn)
    df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)
    df_descarriados = pd.read_sql_query("SELECT * FROM descarriados", conn)
    conn.close()

    # Datos generales de miembros
    if not df_members.empty:
        st.markdown("### 👥 Datos Generales de Miembros por Célula")
        st.dataframe(df_members)
        csv = df_members.to_csv(index=False).encode('utf-8')
        st.download_button("📄 Descargar datos en CSV", csv, "miembros.csv", "text/csv")

    # Gráfica de crecimiento
    st.markdown("### 📈 Crecimiento de las Células")
    if not df_members.empty or not df_converts.empty or not df_cell.empty:
        miembros_por_c
