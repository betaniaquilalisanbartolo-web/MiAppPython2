import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

# Configuración de la página
st.set_page_config(page_title="Panel de Control - Gestión de Células", layout="wide")

# Configuración del archivo de base de datos
DB_PATH = "celulas.db"

# ==========================================
# 1. INICIALIZACIÓN DE LA BASE DE DATOS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Tabla de Usuarios
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'Usuario'
        )
    """)
    
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "admin123", "Administrador"))
    
    # Tabla de Células
    c.execute("""
        CREATE TABLE IF NOT EXISTS cells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cell_name TEXT NOT NULL,
            leader_name TEXT NOT NULL,
            sector TEXT
        )
    """)
    
    # Tabla de Nuevos Miembros
    c.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            birth_date TEXT,
            gender TEXT,
            marital_status TEXT,
            cell_assigned TEXT,
            conversion_date TEXT,
            baptized TEXT,
            baptism_date TEXT,
            membership_status TEXT,
            emergency_contact TEXT,
            emergency_phone TEXT,
            prayer_requests TEXT
        )
    """)
    
    # Tabla de Reportes de Células
    c.execute("""
        CREATE TABLE IF NOT EXISTS cell_reports (
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
        )
    """)
    
    # Tabla de Descarrilados
    c.execute("""
        CREATE TABLE IF NOT EXISTS backsliders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_name TEXT NOT NULL,
            phone TEXT,
            cell_name TEXT,
            last_attendance TEXT,
            risk_level TEXT,
            reason TEXT,
            assigned_visitor TEXT,
            action_plan TEXT,
            visit_date TEXT,
            status TEXT,
            observations TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Función auxiliar para convertir DataFrames a Excel descargable
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
    return output.getvalue()

# ==========================================
# 2. CONTROL DE ACCESO (LOGIN / REGISTRO)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso al Sistema</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col2:
        tab_login, tab_signup = st.tabs(["🔑 Iniciar Sesión", "📝 Crear una Cuenta"])
        
        with tab_login:
            with st.form("login_form"):
                user_input = st.text_input("Usuario", key="login_user")
                pass_input = st.text_input("Contraseña", type="password", key="login_pass")
                login_button = st.form_submit_button("Ingresar al Panel")
                
                if login_button:
                    if user_input and pass_input:
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (user_input, pass_input))
                        user_record = c.fetchone()
                        conn.close()
                        
                        if user_record:
                            st.session_state.logged_in = True
                            st.session_state.username = user_input
                            st.success(f"¡Bienvenido, {user_input}!")
                            st.rerun()
                        else:
                            st.error("Usuario o contraseña incorrectos.")
                    else:
                        st.error("Por favor rellene todos los campos.")
                        
        with tab_signup:
            with st.form("signup_form"):
                new_user = st.text_input("Elige un Nombre de Usuario")
                new_pass = st.text_input("Elige una Contraseña", type="password")
                confirm_pass = st.text_input("Confirma tu Contraseña", type="password")
                signup_button = st.form_submit_button("Registrar Cuenta")
                
                if signup_button:
                    if not new_user or not new_pass:
                        st.error("Todos los campos son obligatorios.")
                    elif new_pass != confirm_pass:
                        st.error("Las contraseñas no coinciden.")
                    else:
                        try:
                            conn = sqlite3.connect(DB_PATH)
                            c = conn.cursor()
                            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_user, new_pass))
                            conn.commit()
                            conn.close()
                            st.success("¡Cuenta creada exitosamente! Ya puedes iniciar sesión.")
                        except sqlite3.IntegrityError:
                            st.error("El nombre de usuario ya existe. Elige otro.")
    st.stop()

# ==========================================
# 3. INTERFAZ PRINCIPAL DEL PANEL DE CONTROL
# ==========================================
with st.sidebar:
    st.markdown("### 👤 Sesión Activa")
    st.write(f"Conectado como: **{st.session_state.username}**")
    st.markdown("---")
    st.markdown("### 🧭 Navegación")
    menu_option = st.radio(
        "Seleccione una sección:",
        [
            "📊 Vista General", 
            "⚙️ Configuración de Células", 
            "👥 Ingreso de Nuevos Miembros",
            "📝 Reportes de Células", 
            "👣 Seguimiento de Descarrilados"
        ]
    )
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# Cargar opciones globales de células
conn = sqlite3.connect(DB_PATH)
cells_df = pd.read_sql_query("SELECT cell_name FROM cells", conn)
conn.close()
cell_options = cells_df['cell_name'].tolist() if not cells_df.empty else []

# ------------------------------------------
# SECCIÓN: VISTA GENERAL (DASHBOARD)
# ------------------------------------------
if menu_option == "📊 Vista General":
    st.title("📊 Panel de Control y Estadísticas")
    
    conn = sqlite3.connect(DB_PATH)
    tot_cells = pd.read_sql_query("SELECT COUNT(*) as total FROM cells", conn)['total'].iloc[0]
    tot_members = pd.read_sql_query("SELECT COUNT(*) as total FROM members", conn)['total'].iloc[0]
    tot_reports = pd.read_sql_query("SELECT COUNT(*) as total FROM cell_reports", conn)['total'].iloc[0]
    tot_backsliders = pd.read_sql_query("SELECT COUNT(*) as total FROM backsliders WHERE status != 'Reconciliado con el Señor'", conn)['total'].iloc[0]
    conn.close()
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(label="🏠 Células Activas", value=int(tot_cells))
    kpi2.metric(label="👥 Miembros Activos", value=int(tot_members))
    kpi3.metric(label="📋 Reportes Entregados", value=int(tot_reports))
    kpi4.metric(label="👣 Casos Descarrilados", value=int(tot_backsliders))

# ------------------------------------------
# SECCIÓN: CONFIGURACIÓN DE CÉLULAS
# ------------------------------------------
elif menu_option == "⚙️ Configuración de Células":
    st.title("⚙️ Configuración y Estructura")
    st.subheader("Registro de Nombre de la Célula y el Líder")
    
    with st.form("registro_celula"):
        new_cell_name = st.text_input("Nombre de la Célula")
        cell_leader = st.text_input("Nombre del Líder")
        cell_sector = st.text_input("Sector / Zona de Reunión")
        submit_cell = st.form_submit_button("Registrar Nueva Célula")
        
        if submit_cell:
            if new_cell_name and cell_leader:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("INSERT INTO cells (cell_name, leader_name, sector) VALUES (?, ?, ?)", (new_cell_name, cell_leader, cell_sector))
                conn.commit()
                conn.close()
                st.success(f"Célula '{new_cell_name}' guardada correctamente.")
                st.rerun()
            else:
                st.error("Por favor, rellene los campos obligatorios.")

    st.markdown("---")
    st.subheader("📋 Células Registradas Actuales")
    conn = sqlite3.connect(DB_PATH)
    all_cells = pd.read_sql_query("SELECT cell_name as 'Nombre Célula', leader_name as 'Líder', sector as 'Sector' FROM cells", conn)
    conn.close()
    
    if not all_cells.empty:
        st.dataframe(all_cells, use_container_width=True)
