import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Panel de Control - Gestión de Células", layout="wide")

DB_PATH = "celulas.db"

# ==========================================
# 1. INICIALIZACIÓN DE LA BASE DE DATOS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Tabla de Usuarios (Credenciales)
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'Usuario'
    )""")
    
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone() == 0:
        c.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)", ("admin", "admin123", "Administrador"))
    
    # Tabla de Células (Administración)
    c.execute("""
    CREATE TABLE IF NOT EXISTS cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cell_name TEXT UNIQUE NOT NULL,
        leader_name TEXT NOT NULL,
        sector TEXT
    )""")
    
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
        assigned_cell TEXT,
        conversion_date TEXT,
        baptized TEXT,
        baptism_date TEXT,
        membership_status TEXT,
        emergency_contact TEXT,
        emergency_phone TEXT,
        prayer_requests TEXT
    )""")
    
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
        home_leader TEXT,
        biblical_topic TEXT,
        central_text TEXT,
        offering REAL,
        needs TEXT,
        spiritual_level TEXT,
        attendance_level INTEGER
    )""")
    
    # Tabla de Descarrilados / Seguimiento
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
    )""")
    
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    st.error(f"Error al inicializar Base de Datos: {e}")

# Función para codificación segura de descargas
def to_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

# ==========================================
# 2. CONTROL DE ACCESO (LOGIN / REGISTRO)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso al Sistema Ministerial</h2>", unsafe_allow_html=True)
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
                        c.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (user_input, pass_input))
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
                        st.error("Por favor llene todos los campos.")
                        
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
                            c.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (new_user, new_pass))
                            conn.commit()
                            conn.close()
                            st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
                        except sqlite3.IntegrityError:
                            st.error("El nombre de usuario ya existe.")
    st.stop()

# ==========================================
# 3. BARRA LATERAL DE NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.markdown(f"### 👤 Sesión Activa\nConectado como: **{st.session_state.username}**")
    st.markdown("---")
    st.markdown("### 🎛️ Menú del Panel")
    
    menu_option = st.radio(
        "Seleccione una sección:",
        [
            "📊 Vista General", 
            "⚙️ Configuración de Células", 
            "👤 Ingreso de Nuevos Miembros", 
            "📝 Reportes de Células", 
            "📉 Seguimiento de Almas"
        ]
    )
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# ==========================================
# 4. LÍGICA DE LAS SECCIONES DEL PANEL
# ==========================================

# A. VISTA GENERAL (ESTADÍSTICAS)
if menu_option == "📊 Vista General":
    st.title("📊 Panel de Control y Estadísticas")
    st.write("Resumen ejecutivo del estado actual de los ministerios y células.")
    
    conn = sqlite3.connect(DB_PATH)
    tot_cells = len(pd.read_sql_query("SELECT id FROM cells", conn))
    tot_members = len(pd.read_sql_query("SELECT id FROM members", conn))
    tot_reports = len(pd.read_sql_query("SELECT id FROM cell_reports", conn))
    try:
        tot_backsliders = len(pd.read_sql_query("SELECT id FROM backsliders WHERE status != 'Reconciliado'", conn))
    except:
        tot_backsliders = 0
    conn.close()
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(label="🏠 Células Activas", value=tot_cells)
    kpi2.metric(label="👥 Miembros Registrados", value=tot_members)
    kpi3.metric(label="📄 Reportes Entregados", value=tot_reports)
    kpi4.metric(label="⚠️ Casos en Seguimiento", value=tot_backsliders)

# B. CONFIGURACIÓN DE CÉLULAS
elif menu_option == "⚙️ Configuración de Células":
    st.title("⚙️ Estructura y Administración")
    st.subheader("Formulario de Registro: Células y Líderes")
    
    with st.form("registro_celula"):
        new_cell_name = st.text_input("Nombre de la Célula *")
        cell_leader = st.text_input("Nombre del Líder Asignado *")
        cell_sector = st.text_input("Sector / Zona Geográfica")
        submit_cell = st.form_submit_button("Registrar Nueva Célula")
        
        if submit_cell:
            if new_cell_name and cell_leader:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM cells WHERE cell_name = ?", (new_cell_name,))
                if c.fetchone()[0] > 0:
                    st.error("Ya existe una célula registrada con ese nombre.")
                else:
                    c.execute("INSERT INTO cells (cell_name, leader_name, sector) VALUES (?, ?, ?)", 
                              (new_cell_name, cell_leader, cell_sector))
                    conn.commit()
                    st.success(f"Célula '{new_cell_name}' registrada exitosamente.")
                    st.rerun()
                conn.close()
            else:
                st.error("Por favor rellene los campos obligatorios (*).")
                
    st.markdown("---")
    st.subheader("📋 Células Registradas")
    try:
        conn = sqlite3.connect(DB_PATH)
        df_celulas = pd.read_sql_query("SELECT id as 'ID', cell_name as 'Célula', leader_name as 'Líder', sector as 'Sector/Zona' FROM cells ORDER BY cell_name ASC", conn)
        conn.close()
        if not df_celulas.empty:
            st.dataframe(df_celulas, use_container_width=True)
        else:
            st.info("No hay células registradas todavía.")
    except Exception as e:
        st.error(f"Error al cargar células: {e}")

# C. INGRESO DE NUEVOS MIEMBROS (SINCRONIZACIÓN AUTOMÁTICA EN TIEMPO REAL)
