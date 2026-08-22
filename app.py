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

init_db()

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Gestión de Iglesia", layout="wide")
st.title("⛪ Sistema de Gestión de Células y Miembros")

menu = st.sidebar.selectbox("Selecciona una sección", ["📝 Formularios", "📊 Panel de Control y Reportes", "➕ Registro de Célula"])

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

           if st.form_submit_button("Guardar Estadísticas"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO members_stats (full_name, cell, sex, growth_eval, discipleship_type, ministry) VALUES (?, ?, ?, ?, ?, ?)''',
                          (full_name, cell, sex, growth_eval, discipleship_type, ministry))
                conn.commit()
                conn.close()
                st.success("¡Estadísticas de miembro guardadas!")

# ================= PANEL DE CONTROL =================
elif menu == "📊 Panel de Control y Reportes
