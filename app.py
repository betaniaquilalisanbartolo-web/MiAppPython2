import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import hashlib

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Panel de Control - Gestión de Células", layout="wide")

DB_PATH = "celulas.db"
MEDIA_DIR = "imagenes_reportes"

if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

# ==========================================
# 1. INICIALIZACIÓN DE LA BASE DE DATOS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Tabla de Usuarios (Credenciales)
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT "Usuario"
        )
    ''')
    
    # Tabla de Células
    c.execute('''
        CREATE TABLE IF NOT EXISTS celulas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            lider TEXT NOT NULL,
            dia_reunion TEXT,
            hora_reunion TEXT,
            direccion TEXT
        )
    ''')
    
    # Tabla de Miembros
    c.execute('''
        CREATE TABLE IF NOT EXISTS miembros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            celula_id INTEGER,
            rol_celula TEXT DEFAULT "Asistente",
            FOREIGN KEY(celula_id) REFERENCES celulas(id)
        )
    ''')
    
    # Tabla de Reportes de Reunión
    c.execute('''
        CREATE TABLE IF NOT EXISTS reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            celula_id INTEGER,
            fecha TEXT,
            asistencia INTEGER,
            ofrenda REAL,
            observaciones TEXT,
            imagen_path TEXT,
            FOREIGN KEY(celula_id) REFERENCES celulas(id)
        )
    ''')
    
    # Crear un usuario administrador por defecto si la tabla está vacía
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)", ("admin", admin_pass, "Administrador"))
        user_pass = hashlib.sha256("user123".encode()).hexdigest()
        c.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)", ("lider", user_pass, "Usuario"))
        
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. FUNCIONES AUXILIARES DE CONEXIÓN
# ==========================================
def run_query(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)

def run_cmd(cmd, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(cmd, params)
        conn.commit()

# ==========================================
# 3. SISTEMA DE AUTENTICACIÓN
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

def login_user(username, password):
    hashed_pass = hashlib.sha256(password.encode()).hexdigest()
    res = run_query("SELECT role FROM usuarios WHERE username = ? AND password = ?", (username, hashed_pass))
    if not res.empty:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = res.iloc[0]['role']
        st.rerun()
    else:
        st.error("❌ Credenciales incorrectas")

def logout_user():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# --- Interfaz de Login ---
if not st.session_state.logged_in:
    st.title("🔑 Acceso al Sistema de Células")
    with st.form("Login"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_form("Iniciar Sesión")
        if submitted:
            login_user(username, password)
    st.info("💡 Cuentas por defecto:\n- Admin: admin / admin123\n- Líder: lider / user123")
    st.stop()

# ==========================================
# 4. BARRA LATERAL (NAVEGACIÓN)
# ==========================================
st.sidebar.title(f"👤 {st.session_state.username}")
st.sidebar.write(f"Rol: **{st.session_state.role}**")

opciones = ["🏠 Dashboard General", "📊 Subir Reporte Semanal", "👥 Gestión de Miembros"]
if st.session_state.role == "Administrador":
    opciones.append("🏛️ Configuración de Células")

menu = st.sidebar.radio("Navegación", opciones)

if st.sidebar.button("🚪 Cerrar Sesión"):
    logout_user()

# ==========================================
# 5. MÓDULO: DASHBOARD GENERAL
# ==========================================
if menu == "🏠 Dashboard General":
    st.title("🏠 Panel de Control Principal")
    
    # Métricas Globales
    col1, col2, col3 = st.columns(3)
    total_celulas = run_query("SELECT COUNT(*) as total FROM celulas").iloc[0]['total']
    total_miembros = run_query("SELECT COUNT(*) as total FROM miembros").iloc[0]['total']
    total_asistencias = run_query("SELECT SUM(asistencia) as total FROM reportes").iloc[0]['total'] or 0
    
    col1.metric("📌 Total Células", total_celulas)
    col2.metric("👥 Miembros Registrados", total_miembros)
    col3.metric("📈 Asistencias Acumuladas", int(total_asistencias))
    
    st.markdown("---")
    
    # Histórico de Reportes
    st.subheader("📋 Últimos Reportes Recibidos")
    df_reportes = run_query('''
        SELECT r.fecha, c.nombre as celula, r.asistencia, r.ofrenda, r.observaciones, r.imagen_path
        FROM reportes r 
        JOIN celulas c ON r.celula_id = c.id 
        ORDER BY r.fecha DESC LIMIT 10
    ''')
    
    if df_reportes.empty:
        st.warning("No hay reportes registrados todavía.")
    else:
        st.dataframe(df_reportes.drop(columns=['imagen_path']), use_container_width=True)
        
        # Galería visual de evidencias
        st.subheader("📸 Evidencias de Reuniones")
        cols_img = st.columns(4)
        idx_col = 0
        for idx, row in df_reportes.iterrows():
            if row['imagen_path'] and os.path.exists(row['imagen_path']):
                with cols_img[idx_col % 4]:
                    st.image(row['imagen_path'], caption=f"{row['celula']} - {row['fecha']}", use_container_width=True)
                idx_col += 1

# ==========================================
# 6. MÓDULO: SUBIR REPORTE SEMANAL
# ==========================================
elif menu == "📊 Subir Reporte Semanal":
    st.title("📊 Registrar Reporte de Célula")
    
    df_celulas = run_query("SELECT id, nombre FROM celulas")
    
    if df_celulas.empty:
        st.error("⚠️ No hay células registradas en el sistema. Contacta al Administrador.")
    else:
        celula_dict = dict(zip(df_celulas['nombre'], df_celulas['id']))
        
        with st.form("Formulario Reporte"):
            celula_sel = st.selectbox("Selecciona tu Célula", list(celula_dict.keys()))
            fecha_rep = st.date_input("Fecha de la Reunión", datetime.now())
            asistencia = st.number_input("Cantidad de Asistentes", min_value=0, step=1)
            ofrenda = st.number_input("Ofrenda Recolectada ($)", min_value=0.0, step=0.5)
            observaciones = st.text_area("Observaciones o Peticiones de Oración")
            foto = st.file_uploader("Subir foto de la reunión (Opcional)", type=["jpg", "jpeg", "png"])
            
            enviar = st.form_submit_button("Guardar Reporte")
            
            if enviar:
                img_final_path = ""
                if foto is not None:
                    # Guardar archivo con nombre único
                    timestamp = datetime.now().strftime("%Y%m%dd_%H%M%S")
                    img_final_path = os.path.join(MEDIA_DIR, f"{celula_sel}_{timestamp}.jpg")
                    with open(img_final_path, "wb") as f:
                        f.write(foto.getbuffer())
                
                run_cmd('''
                    INSERT INTO reportes (celula_id, fecha, asistencia, ofrenda, observaciones, imagen_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (celula_dict[celula_sel], str(fecha_rep), asistencia, ofrenda, observaciones, img_final_path))
                
                st.success(f"🎉 ¡Reporte de la célula '{celula_sel}' guardado correctamente!")

# ==========================================
# 7. MÓDULO: GESTIÓN DE MIEMBROS
# ==========================================
elif menu == "👥 Gestión de Miembros":
    st.title("👥 Control de Miembros")
    
    df_celulas = run_query("SELECT id, nombre FROM celulas")
    
    if df_celulas.empty:
        st.error("⚠️ Primero debes registrar al menos una célula para añadir miembros.")
    else:
        celula_dict = dict(zip(df_celulas['nombre'], df_celulas['id']))
        
        tab1, tab2 = st.tabs(["Añadir Miembro", "Ver / Editar Lista"])
        
        with tab1:
            with st.form("Nuevo Miembro"):
                nombre_m = st.text_input("Nombre Completo")
                telefono_m = st.text_input("Teléfono de Contacto")
                celula_m = st.selectbox("Asignar a Célula", list(celula_dict.keys()))
                rol_m = st.selectbox("Rol en la Célula", ["Asistente", "Líder de Célula", "Anfitrión", "Tesorero"])
                
                guardar_m = st.form_submit_button("Registrar Miembro")
                if guardar_m and nombre_m:
                    run_cmd('''
                        INSERT INTO miembros (nombre, telefono, celula_id, rol_celula)
                        VALUES (?, ?, ?, ?)
                    ''', (nombre_m, telefono_m, celula_dict[celula_m], rol_m))
