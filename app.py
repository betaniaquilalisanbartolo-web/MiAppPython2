import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(page_title="Panel de Control - Gestión de Células", layout="wide")

DB_PATH = "celulas.db"
MEDIA_DIR = "imagenes_reportes"

# Crear directorio de imágenes si no existe en el servidor local
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

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
    
    # Tabla de Células (Administración con columna de Metas Anuales)
    c.execute("""
    CREATE TABLE IF NOT EXISTS cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cell_name TEXT UNIQUE NOT NULL,
        leader_name TEXT NOT NULL,
        sector TEXT,
        yearly_target INTEGER DEFAULT 10
    )""")
    
    # Tabla de Nuevos Miembros (CAMPOS EXTENDIDOS)
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
        prayer_requests TEXT,
        invited_by TEXT,
        spiritual_gift TEXT,
        family_members INTEGER,
        observations TEXT
    )""")
    
    # Tabla de Reportes de Células (Con columna foto_path)
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
        attendance_level INTEGER,
        foto_path TEXT
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
        observations TEXT,
        contact_method TEXT,
        spiritual_diagnosis TEXT
    )""")

    # TABLA NUEVA: Calendario de Actividades Ministeriales
    c.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_date TEXT NOT NULL,
        event_time TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        target_cell TEXT DEFAULT 'Todas'
    )""")
    
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    st.error(f"Error al inicializar Base de Datos: {e}")

# Función para codificación de descargas (Excel compatible)
def to_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

# ==========================================
# 2. CONTROL DE ACCESO (LOGIN / REGISTRO)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = "Usuario"

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
                        c.execute("SELECT username, role FROM usuarios WHERE username = ? AND password = ?", (user_input, pass_input))
                        user_record = c.fetchone()
                        conn.close()
                        
                        if user_record:
                            st.session_state.logged_in = True
                            st.session_state.username = user_record[0]
                            st.session_state.role = user_record[1]
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
                            c.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, 'Usuario')", (new_user, new_pass))
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
    st.markdown(f"### 👤 Sesión Activa\nConectado como: **{st.session_state.username}**\nRol: `{st.session_state.role}`")
    st.markdown("---")
    st.markdown("### 🎛️ Menú del Panel")
    
    menu_option = st.radio(
        "Seleccione una sección:",
        [
            "📊 Vista General", 
            "⚙️ Configuración de Células", 
            "👤 Ingreso de Nuevos Miembros", 
            "📝 Reportes de Células", 
            "📉 Seguimiento de Almas",
            "📅 Agenda y Calendario"
        ]
    )
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = "Usuario"
        st.rerun()

# Carga global rápida de opciones de células
opciones_celulas_global = ["Ninguna"]
try:
    conn = sqlite3.connect(DB_PATH)
    cells_df = pd.read_sql_query("SELECT cell_name FROM cells ORDER BY cell_name ASC", conn)
    conn.close()
    if not cells_df.empty:
        opciones_celulas_global += cells_df["cell_name"].tolist()
except:
    pass

# ==========================================
# 4. LÍGICA DE LAS SECCIONES DEL PANEL
# ==========================================

# A. VISTA GENERAL (ESTADÍSTICAS Y METAS ANUALES)
if menu_option == "📊 Vista General":
    st.title("📊 Panel de Control y Estadísticas")
    st.write("Resumen ejecutivo del estado actual de los ministerios y cumplimiento de metas.")
    
    conn = sqlite3.connect(DB_PATH)
    tot_cells = len(pd.read_sql_query("SELECT id FROM cells", conn))
    tot_members = len(pd.read_sql_query("SELECT id FROM members", conn))
    tot_reports = len(pd.read_sql_query("SELECT id FROM cell_reports", conn))
    try:
        tot_backsliders = len(pd.read_sql_query("SELECT id FROM backsliders WHERE status != 'Reconciliado / Restaurado'", conn))
    except:
        tot_backsliders = 0
    conn.close()
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(label="🏠 Células Activas", value=tot_cells)
    kpi2.metric(label="👥 Miembros Registrados", value=tot_members)
    kpi3.metric(label="📄 Reportes Entregados", value=tot_reports)
    kpi4.metric(label="⚠️ Casos en Seguimiento", value=tot_backsliders)
    
    st.markdown("---")
    st.subheader("📈 Monitoreo de Metas Anuales por Célula")
    
    # UNIFICACIÓN DE CONSULTA: Definida fuera del try para prevenir errores sintácticos de identación
    query_metas = (
        "SELECT c.cell_name as 'Célula', "
        "c.yearly_target as 'Meta de Nuevos Miembros', "
        "COUNT(m.id) as 'Miembros Registrados Actuales' "
        "FROM cells c "
        "LEFT JOIN members m ON c.cell_name = m.assigned_cell "
        "GROUP BY c.cell_name"
