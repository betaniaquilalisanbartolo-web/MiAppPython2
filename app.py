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
        [
            "➕ Registro de Célula",
            "👥 Registro de Miembros por Célula",
            "📝 Formularios",
            "📊 Panel de Control y Reportes",
            "🔐 Registrar Líder"
        ]
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
                        st.error("Ya existe una célula con ese
