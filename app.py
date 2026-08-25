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
    
    # Crear administrador por defecto si no existe
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)", ("admin", "admin123", "Administrador"))
    
    # Tabla de Células
    c.execute("""
    CREATE TABLE IF NOT EXISTS celulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        lider TEXT NOT NULL,
        dia_reunion TEXT,
        hora_reunion TEXT,
        direccion TEXT,
        fecha_creacion TEXT
    )""")
    
    # Tabla de Asistencia / Reportes
    c.execute("""
    CREATE TABLE IF NOT EXISTS reportes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        celula_id INTEGER,
        fecha TEXT,
        asistentes INTEGER DEFAULT 0,
        nuevos INTEGER DEFAULT 0,
        observaciones TEXT,
        FOREIGN KEY (celula_id) REFERENCES celulas(id) ON DELETE CASCADE
    )""")
    
    conn.commit()
    conn.close()

# Inicializar DB al arrancar
init_db()

# Helper para conectar a la BD
def run_query(query, params=(), fetch=False, is_select=True):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if is_select:
            if fetch:
                return cursor.fetchall()
            return cursor.fetchall()
        conn.commit()

# ==========================================
# 2. SISTEMA DE AUTENTICACIÓN SIMPLE
# ==========================================
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.rol = None

def login():
    st.subheader("🔑 Iniciar Sesión")
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        res = run_query("SELECT role FROM usuarios WHERE username = ? AND password = ?", (user, password))
        if res:
            st.session_state.autenticado = True
            st.session_state.usuario = user
            st.session_state.rol = res[0][0]
            st.success(f"Bienvenido {user} ({st.session_state.rol})")
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

def logout():
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.rol = None
    st.rerun()

# ==========================================
# 3. INTERFAZ PRINCIPAL
# ==========================================
if not st.session_state.autenticado:
    login()
else:
    # Barra lateral
    st.sidebar.title(f"👤 {st.session_state.usuario}")
    st.sidebar.write(f"Rol: **{st.session_state.rol}**")
    menu = st.sidebar.radio("Navegación", ["Dashboard", "Gestionar Células", "Registrar Reporte"])
    if st.sidebar.button("Cerrar Sesión"):
        logout()

    # --- VISTA: DASHBOARD ---
    if menu == "Dashboard":
        st.title("📊 Panel de Control General")
        
        # Métricas rápidas
        df_celulas = pd.read_sql_query("SELECT * FROM celulas", sqlite3.connect(DB_PATH))
        df_reportes = pd.read_sql_query("SELECT * FROM reportes", sqlite3.connect(DB_PATH))
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Células", len(df_celulas))
        col2.metric("Total Asistencias Registradas", int(df_reportes['asistentes'].sum()) if not df_reportes.empty else 0)
        col3.metric("Nuevos Integrantes", int(df_reportes['nuevos'].sum()) if not df_reportes.empty else 0)
        
        st.subheader("📍 Lista de Células Activas")
        st.dataframe(df_celulas, use_container_width=True)

    # --- VISTA: GESTIONAR CÉLULAS ---
    elif menu == "Gestionar Células":
        st.title("🏢 Administración de Células")
        
        # Formulario de creación (Solo Admin o Usuario autorizado)
        with st.expander("➕ Crear Nueva Célula", expanded=True):
            with st.form("nueva_celula"):
                nombre = st.text_input("Nombre de la Célula")
                lider = st.text_input("Nombre del Líder")
                dia = st.selectbox("Día de Reunión", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
                hora = st.time_input("Hora de Reunión", value=datetime.now().time())
                direccion = st.text_area("Dirección")
                
                if st.form_submit_button("Guardar Célula"):
                    if nombre and lider:
                        run_query("""
                            INSERT INTO celulas (nombre, lider, dia_reunion, hora_reunion, direccion, fecha_creacion)
                            VALUES (?, ?, ?, ?, ?, ?)""",
                            (nombre, lider, dia, hora.strftime("%H:%M"), direccion, datetime.now().strftime("%Y-%m-%d")),
                            is_select=False)
                        st.success("¡Célula registrada con éxito!")
                        st.rerun()
                    else:
                        st.error("El nombre y el líder son obligatorios.")

        # Eliminar células (Acción crítica)
        st.subheader("🗑️ Eliminar o Modificar")
        conn = sqlite3.connect(DB_PATH)
        df_celulas = pd.read_sql_query("SELECT id, nombre, lider FROM celulas", conn)
        conn.close()
        
        if not df_celulas.empty:
            opciones = {f"{row['nombre']} - {row['lider']}": row['id'] for _, row in df_celulas.iterrows()}
            seleccion = st.selectbox("Selecciona una célula para eliminar", opciones.keys())
            if st.button("Eliminar Célula Permanentemente", type="primary"):
                run_query("DELETE FROM celulas WHERE id = ?", (opciones[seleccion],), is_select=False)
                st.success("Célula eliminada.")
                st.rerun()

    # --- VISTA: REGISTRAR REPORTE ---
    elif menu == "Registrar Reporte":
        st.title("📝 Reporte de Asistencia Semanal")
        
        conn = sqlite3.connect(DB_PATH)
        df_celulas = pd.read_sql_query("SELECT id, nombre FROM celulas", conn)
        conn.close()
        
        if df_celulas.empty:
            st.warning("Primero debes crear una célula para poder generar reportes.")
        else:
            celulas_dict = {row['nombre']: row['id'] for _, row in df_celulas.iterrows()}
            
            with st.form("reporte_asistencia"):
                celula_sel = st.selectbox("Selecciona la Célula", celulas_dict.keys())
                fecha_reunion = st.date_input("Fecha de la Reunión", datetime.now())
                asistentes = st.number_input("Cantidad de Asistentes", min_value=0, step=1)
                nuevos = st.number_input("Cantidad de Personas Nuevas", min_value=0, step=1)
                obs = st.text_area("Observaciones o Peticiones de Oración")
                
                if st.form_submit_button("Enviar Reporte"):
                    run_query("""
                        INSERT INTO reportes (celula_id, fecha, asistentes, nuevos, observaciones)
                        VALUES (?, ?, ?, ?, ?)""",
                        (celulas_dict[celula_sel], fecha_reunion.strftime("%Y-%m-%d"), asistentes, nuevos, obs),
                        is_select=False)
                    st.success("¡Reporte guardado correctamente!")
