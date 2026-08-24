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
menu = st.sidebar.selectbox("Menú", ["🏠 Inicio", "👤 Registro de Miembros", "📊 Panel de Control y Reportes", "⚙️ Administración"])

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
    selected_cell = st.selectbox("Seleccione la célula", cell_options)

    # Aquí iría el formulario para registrar miembros usando selected_cell

# --- Panel de Control ---
elif menu == "📊 Panel de Control y Reportes":
    st.subheader("📊 Panel de Análisis Automático de la Iglesia")

    conn = sqlite3.connect(DB_PATH)
    df_cell = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    df_converts = pd.read_sql_query("SELECT * FROM new_converts", conn)
    df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)
    df_descarriados = pd.read_sql_query("SELECT * FROM descarriados", conn)
    conn.close()

    # Mostrar datos generales de cada miembro
    if not df_members.empty:
        st.markdown("### 👥 Datos Generales de Miembros por Célula")
        st.dataframe(df_members)

        # Botón para exportar
        csv = df_members.to_csv(index=False).encode('utf-8')
        st.download_button("📄 Descargar datos en CSV", csv, "miembros.csv", "text/csv")

    # Aquí mantienes las gráficas y KPIs como antes

# --- Administración ---
elif menu == "⚙️ Administración":
    st.subheader("Panel de Administración")

    # Registrar nueva célula y líder
    with st.form("nueva_celula"):
        cell_name = st.text_input("Nombre de la célula")
        leader = st.text_input("Nombre del líder")
        submit = st.form_submit_button("Registrar")

        if submit and cell_name:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO cells (cell_name, leader) VALUES (?,?)", (cell_name, leader))
            conn.commit()
            conn.close()
            st.success(f"Célula '{cell_name}' registrada con líder {leader}")
