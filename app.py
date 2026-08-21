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
    conn.commit()
    conn.close()

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
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute('''INSERT INTO cell_reports (cell_name, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (cell_name_final, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level))
                    conn.commit()
                    conn.close()
                    st.success(f"¡Reporte de la célula '{cell_name_final}' guardado exitosamente!")

    # --- Nuevo convertido ---
    with pestana2:
        st.subheader("Registrar Nuevo Convertido")
        lista_celulas_convertidos = [c for c in obtener_nombres_celulas() if c != "➕ Registrar Nueva Célula"]
        with st.form("form_convertido", clear_on_submit=True):
            full_name = st.text_input("Nombre Completo")
            contact = st.text_input("Contacto / Teléfono")
            address = st.text_area("Dirección")
            birth_date = st.text_input("Fecha de Nacimiento (AAAA-MM-DD)")
            age = st.number_input("Edad", min_value=0, step=1)
            status = st.text_input("Estado", value="Nuevo")
            conversion_date = st.text_input("Fecha de Conversión (AAAA-MM-DD)")
            decision_type = st.selectbox("Tipo de Decisión", ["Primera vez", "Reconciliación", "Petición de Oración"])
            assigned_cell = st.selectbox("Célula Asignada", lista_celulas_convertidos)
            observation = st.text_area("Observaciones")

            if st.form_submit_button("Guardar Convertido"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO new_converts (full_name, contact, address, birth_date, age, status, conversion_date, decision_type, assigned_cell, observation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (full_name, contact, address, birth_date, age, status, conversion_date, decision_type, assigned_cell, observation))
                conn.commit()
                conn.close()
                st.success("¡Nuevo convertido guardado con éxito!")

    # --- Miembro ---
    with pestana3:
        st.subheader("Estadísticas de Miembro")
        lista_celulas_miembros = [c for c in obtener_nombres_celulas() if c != "➕ Registrar Nueva Célula"]
        with st.form("form_miembro", clear_on_submit=True):
            full_name = st.text_input("Nombre Completo del Miembro")
            cell = st.selectbox("Célula a la que Pertenece", lista_celulas_miembros)
            sex = st.selectbox("Sexo", ["Masculino", "Femenino"])
            growth_eval = st.slider("Evaluación de Crecimiento", 1, 10, 5)
            discipleship_type = st.text_input("Tipo de Discipulado")
            ministry = st.selectbox("Ministerio", ["Alabanza", "Ujieres", "Niños", "Intercesión", "Media", "Ninguno"])

            if st.form_submit_button("Guardar Estadísticas"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO members_stats (full_name, cell, sex, growth_eval, discipleship_type, ministry) VALUES (?, ?, ?, ?, ?, ?)''',
                          (full_name, cell, sex, growth_eval, discipleship_type, ministry))
                conn.commit()
                conn.close()
                st.success("¡Estadísticas de miembro guardadas!")

# ================= PANEL DE CONTROL =================
elif menu == "📊 Panel de Control y Reportes":
    st.subheader("📊 Panel de Análisis Automático de la Iglesia")
    conn = sqlite3.connect(DB_PATH)
    df_cell = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    df_converts = pd.read_sql_query("SELECT * FROM new_converts", conn)
    df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)
    conn.close()

    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Ofrendas", f"${df_cell['offering'].sum() if not df_cell.empty else 0:.2f}")
    with kpi2:
        st.metric("Nuevos Convertidos", f"{len(df_converts)} personas")
    with kpi3:
        st.metric("Miembros Act
