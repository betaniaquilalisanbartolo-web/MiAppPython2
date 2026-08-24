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

    # Tablas
    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cell_name TEXT UNIQUE,
        leader TEXT
    )""")
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

# --- Inicio/Login ---
if not st.session_state["logged_in"]:
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

else:
    st.info(f"Ya has iniciado sesión como {st.session_state['username']}")
    if st.button("Cerrar sesión"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""

    # --- Pestañas principales ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👤 Miembros",
        "🙌 Convertidos",
        "📌 Reportes",
        "🚨 Descarriados",
        "📊 Panel",
        "⚙️ Administración"
    ])

    # --- Miembros ---
    with tab1:
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

    # --- Convertidos ---
    with tab2:
        st.subheader("Registro de Convertidos")
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

    # --- Reportes ---
    with tab3:
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

    # --- Descarriados ---
    with tab4:
        st.subheader("Registro de Descarriados")
        conn = sqlite3.connect(DB_PATH)
        cells = pd.read_sql_query("SELECT cell_name FROM cells", conn)
        conn.close()
        cell_options = cells['cell_name'].tolist() if not cells.empty else []
        with st.form("registro_descarriado"):
            full_name = st.text_input("Nombre completo")
            age = st.number_input("Edad", min_value=0, max
