import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_PATH = "database.db"

def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

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
    conn.commit()
    conn.close()

# Función automática para obtener los nombres únicos de las células registradas
def obtener_nombres_celulas():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT cell_name FROM cell_reports WHERE cell_name IS NOT NULL AND cell_name != ''")
    filas = c.fetchall()
    conn.close()
    lista_celulas = [f[0] for f in filas]
    if not lista_celulas:
        lista_celulas = ["Célula Central", "Célula de Jóvenes", "Célula de Damas"]
    lista_celulas.append("➕ Registrar Nueva Célula")
    return lista_celulas

init_db()

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Gestión de Iglesia", layout="wide")
st.title("⛪ Sistema de Gestión de Células y Miembros")

# Menú de navegación lateral
menu = st.sidebar.selectbox("Selecciona una sección", ["📝 Formularios", "📊 Panel de Control y Reportes"])

# ================= FORMULARIOS =================
if menu == "📝 Formularios":
    pestana1, pestana2, pestana3 = st.tabs(["📌 Reporte de Célula", "👤 Nuevo Convertido", "📈 Miembro"])
    
    # --- Reporte de célula ---
    with pestana1:
        st.subheader("Registrar Reporte de Célula")
        lista_opciones_celulas = obtener_nombres_celulas()
        with st.form("form_celula", clear_on_submit=True):
            celula_seleccionada = st.selectbox("Selecciona el Nombre de la Célula", lista_opciones_celulas)
            nombre_nueva_celula = st.text_input("Si seleccionaste 'Registrar Nueva Célula', escribe su nombre aquí:")
            meeting_date = st.text_input("Fecha de Reunión (AAAA-MM-DD)")
            col1, col2, col3 = st.columns(3)
            adults = col1.number
