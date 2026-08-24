import streamlit as st
import sqlite3
import pandas as pd
import os

# --- Base de datos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabla de cuentas
    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")

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

# --- Estado de sesión ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

# --- Menú dinámico ---
if not st.session_state["logged_in"]:
    menu = st.sidebar.selectbox("Menú", ["🏠 Inicio (Login)"])
else:
    menu = st.sidebar.selectbox("Menú", [
        "🏠 Inicio (Login)",
        "👤 Registro de Miembros",
        "🙌 Registro de Convertidos",
        "📌 Reportes de Células",
        "🚨 Registro de Descarriados",
        "📊 Panel de Control y Reportes",
        "⚙️ Administración"
    ])

# --- Inicio/Login ---
if menu == "🏠 Inicio (Login)":
    st.subheader("🔑 Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM accounts WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Bienvenido {username}")
        else:
            st.error("Usuario o contraseña incorrectos")

    if st.session_state["logged_in"]:
        st.info(f"Ya has iniciado sesión como {st.session_state['username']}")
        if st.button("Cerrar sesión"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""

# --- Administración ---
elif menu == "⚙️ Administración":
    st.subheader("⚙️ Panel de Administración")

    # Registrar nueva cuenta
    st.markdown("### 🆕 Registrar nueva cuenta")
    new_user = st.text_input("Nuevo usuario")
    new_pass = st.text_input("Nueva contraseña", type="password")
    if st.button("Registrar cuenta"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO accounts (username, password) VALUES (?,?)", (new_user, new_pass))
            conn.commit()
            st.success(f"Cuenta '{new_user}' creada correctamente")
        except sqlite3.IntegrityError:
            st.error("Ese usuario ya existe")
        conn.close()

    # Registrar nueva célula
    st.markdown("### 🌱 Registrar nueva célula y líder")
    cell_name = st.text_input("Nombre de la célula")
    leader = st.text_input("Nombre del líder")
    if st.button("Registrar célula"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO cells (cell_name, leader) VALUES (?,?)", (cell_name, leader))
            conn.commit()
            st.success(f"Célula '{cell_name}' registrada con líder {leader}")
        except sqlite3.IntegrityError:
            st.error("Esa célula ya existe")
        conn.close()

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
        children
