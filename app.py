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
        id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, age INTEGER, contact TEXT,
        address TEXT, assigned_cell TEXT, decision_type TEXT, conversion_date TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS members_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, age INTEGER, contact TEXT,
        cell TEXT, sex TEXT, discipleship_type TEXT, other_church TEXT, ingreso_date TEXT,
        ministry TEXT, status TEXT DEFAULT 'activo'
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

# --- LOGIN Y REGISTRO ---
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

    # 🔐 Registrar líder disponible ANTES de login
    st.subheader("Registrar Nuevo Líder")
    with st.form("form_registro_lider", clear_on_submit=True):
        new_user = st.text_input("Nuevo Usuario")
        new_pass = st.text_input("Nueva Contraseña", type="password")
        if st.form_submit_button("Crear Cuenta"):
            if new_user.strip() and new_pass.strip():
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO leaders (username, password) VALUES (?, ?)", (new_user.strip(), new_pass.strip()))
                    conn.commit()
                    st.success(f"¡Cuenta creada para '{new_user}'! Ahora puedes iniciar sesión.")
                except sqlite3.IntegrityError:
                    st.error("Ese usuario ya existe.")
                conn.close()
            else:
                st.error("Usuario y contraseña no pueden estar vacíos.")

else:
    st.sidebar.success(f"Conectado como {st.session_state['username']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state['logged_in'] = False

    # --- Bloque de administración en la barra lateral ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Administración")

    if st.sidebar.button("Registrar Nueva Célula"):
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

    if st.sidebar.button("Registrar Nuevo Líder"):
        st.subheader("Registrar Nuevo Líder")
        with st.form("form_registro_lider_admin", clear_on_submit=True):
            username = st.text_input("Usuario del Líder")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Guardar Líder"):
                if username.strip() and password.strip():
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    try:
                        c.execute("INSERT INTO leaders (username, password) VALUES (?, ?)", (username.strip(), password.strip()))
                        conn.commit()
                        st.success(f"¡Líder '{username}' registrado exitosamente!")
                    except sqlite3.IntegrityError:
                        st.error("Ya existe un líder con ese usuario.")
                    conn.close()
                else:
                    st.error("Usuario y contraseña no pueden estar vacíos.")

# --- CONTENIDO SOLO SI ESTÁ LOGUEADO ---
if st.session_state['logged_in']:
    st.set_page_config(page_title="Gestión de Iglesia", layout="wide")
    st.title("⛪ Sistema de Gestión de Células y Miembros")

    # Menú principal en la página principal
    menu = st.selectbox(
        "Selecciona una sección",
        [
            "👥 Registro de Miembros por Célula",
            "📝 Registro de Nuevos Convertidos",
            "📋 Reportes de Cultos de Célula",
            "📊 Panel de Control y Reportes"
        ]
    )

    # ================= REGISTRO DE MIEMBROS POR CÉLULA =================
    if menu == "👥 Registro de Miembros por Célula":
        st.subheader("Registrar Miembros en una Célula")
        lista_celulas = obtener_nombres_celulas()
        with st.form("form_miembros_celula", clear_on_submit=True):
            full_name = st.text_input("Nombre Completo")
            age = st.number_input("Edad", min_value=1, max_value=120)
            phone = st.text_input("Teléfono")
            cell = st.selectbox("Célula", lista_celulas)
            sex = st.selectbox("Sexo", ["Masculino", "Femenino"])
            discipulado = st.radio("¿Está siendo discipulado?", ["Sí", "No"])
            otra_iglesia = st.radio("¿Vino de otra iglesia?", ["Sí", "No"])
            fecha_ingreso = st.date_input("Fecha de Ingreso")
            ministry = st.selectbox("Ministerio", ["Alabanza", "Ujieres", "Niños", "Intercesión", "Media", "Ninguno"])

            if st.form_submit_button("Guardar Miembro"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO members_stats 
                    (full_name, age, contact, cell, sex, discipleship_type, other_church, ingreso_date, ministry, status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (full_name, age, phone, cell, sex, discipulado, otra_iglesia, fecha_ingreso, ministry, "activo"))
                conn.commit()
                conn.close()
                st.success(f"¡Miembro '{full_name}' registrado en la célula '{cell}'!")

    # ================= REGISTRO DE NUEVOS CONVERTIDOS =================
    elif menu == "📝 Registro de Nuevos Convertidos":
        st.subheader("Registrar Nuevos Convertidos")
        lista_celulas = obtener_nombres_celulas()
        with st.form("form_convertidos", clear_on_submit=True):
            full_name = st.text_input("Nombres y Apellidos")
            age = st.number_input("Edad", min_value=1, max_value=120)
            phone = st.text_input("Teléfono")
            address = st.text_input("Dirección")
            assigned_cell = st.selectbox("Célula Asignada", lista_celulas)
            decision_type = st.radio("Tipo de
