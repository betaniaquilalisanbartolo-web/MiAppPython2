import sqlite3
import hashlib
import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA Y BASE DE DATOS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Gestión de Iglesia - Células",
    page_icon="⛪",
    layout="wide"
)

def get_db_connection():
    conn = sqlite3.connect("iglesia.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla de Usuarios para Login
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Tabla de Miembros por Célula
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS miembros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            telefono TEXT,
            celula TEXT NOT NULL,
            rol TEXT NOT NULL,
            fecha_registro DATE DEFAULT CURRENT_DATE
        )
    ''')
    
    # Tabla de Reportes de Célula
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reportes_celula (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            celula TEXT NOT NULL,
            lider TEXT NOT NULL,
            fecha DATE NOT NULL,
            asistencia_miembros INTEGER NOT NULL,
            asistencia_visitas INTEGER NOT NULL,
            ofrenda REAL DEFAULT 0.0,
            observaciones TEXT
        )
    ''')
    
    # Tabla de Descarrilados / Ausentes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS descarrilados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            celula TEXT,
            motivo TEXT,
            estado_seguimiento TEXT DEFAULT 'Pendiente',
            fecha_registro DATE DEFAULT CURRENT_DATE
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# -----------------------------------------------------------------------------
# 2. FUNCIONES DE SEGURIDAD (HASH DE CONTRASEÑAS)
# -----------------------------------------------------------------------------
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# -----------------------------------------------------------------------------
# 3. CONTROL DE SESIÓN Y AUTENTICACIÓN
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""

def auth_screen():
    st.title("⛪ Sistema de Gestión Ecuménica y Células")
    
    opcion = st.sidebar.selectbox("Acceso al Sistema", ["Iniciar Sesión", "Crear nueva cuenta de usuario"])
    
    if opcion == "Iniciar Sesión":
        st.subheader("🔑 Iniciar Sesión")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar", type="primary"):
            conn = get_db_connection()
            cursor = conn.cursor()
            hashed_pw = make_hashes(password)
            cursor.execute("SELECT * FROM usuarios WHERE email = ? AND password = ?", (email, hashed_pw))
            usuario = cursor.fetchone()
            conn.close()
            
            if usuario:
                st.session_state["logged_in"] = True
                st.session_state["user_name"] = usuario["nombre"]
                st.success(f"Bienvenido/a {usuario['nombre']}")
                st.rerun()
            else:
                st.error("Correo o contraseña incorrectos")
                
    elif opcion == "Crear nueva cuenta de usuario":
        st.subheader("👤 Crear Nueva Cuenta")
        nombre = st.text_input("Nombre Completo")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")
        confirm_password = st.text_input("Confirmar Contraseña", type="password")
        
        if st.button("Registrarse"):
            if password != confirm_password:
                st.warning("Las contraseñas no coinciden")
            elif not nombre or not email or not password:
                st.warning("Por favor completa todos los campos")
            else:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)",
                        (nombre, email, make_hashes(password))
                    )
                    conn.commit()
                    conn.close()
                    st.success("Cuenta creada exitosamente. Ahora puedes Iniciar Sesión.")
                except sqlite3.IntegrityError:
                    st.error("El correo ya se encuentra registrado.")

# -----------------------------------------------------------------------------
# 4. MÓDULOS Y VISTAS PRINCIPALES
# -----------------------------------------------------------------------------
def panel_de_control():
    st.title("📊 Panel de Control")
    st.markdown("---")
    
    conn = get_db_connection()
    df_reportes = pd.read_sql_query("SELECT * FROM reportes_celula", conn)
    df_miembros = pd.read_sql_query("SELECT * FROM miembros", conn)
    conn.close()
    
    # Indicadores
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_reportes = len(df_reportes)
        st.metric("Total Reportes", total_reportes)
    with col2:
        total_asistencia = df_reportes["asistencia_miembros"].sum() + df_reportes["asistencia_visitas"].sum() if not df_reportes.empty else 0
        st.metric("Asistencia Total Acumulada", total_asistencia)
    with col3:
        total_miembros = len(df_miembros)
        st.metric("Total Miembros Registrados", total_miembros)
    with col4:
        total_ofrenda = df_reportes["ofrenda"].sum() if not df_reportes.empty else 0.0
        st.metric("Total Ofrendas ($)", f"${total_ofrenda:,.2f}")
        
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 Gráficos de Células")
        if not df_reportes.empty:
            df_celula_asistencia = df_reportes.groupby("celula")[["asistencia_miembros", "asistencia_visitas"]].sum().reset_index()
            fig_celulas = px.bar(
                df_celula_asistencia,
                x="celula",
                y=["asistencia_miembros", "asistencia_visitas"],
                title="Asistencia por Célula (Miembros vs Visitas)",
                barmode="group",
                labels={"value": "Personas", "celula": "Célula", "variable": "Tipo"}
            )
            st.plotly_chart(fig_celulas, use_container_width=True)
        else:
            st.info("Aún no hay reportes registrados para mostrar gráficos.")
            
    with col_chart2:
        st.subheader("👥 Gráficos de Miembros")
        if not df_miembros.empty:
            df_miembros_celula = df_miembros["celula"].value_counts().reset_index()
            df_miembros_celula.columns = ["Célula", "Cantidad"]
            fig_miembros = px.pie(
                df_miembros_celula,
                names="Célula",
                values="Cantidad",
                title="Distribución de Miembros por Célula",
                hole=0.4
            )
            st.plotly_chart(fig_miembros, use_container_width=True)
        else:
            st.info("Aún no hay miembros registrados para mostrar gráficos.")

def registro_miembros():
    st.title("📌 Registro de Miembro por Célula")
    
    with st.form("form_miembro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            telefono = st.text_input("Teléfono / WhatsApp")
        with col2:
            celula = st.text_input("Nombre / Número de Célula")
            rol = st.selectbox("Rol en la Célula", ["Miembro", "Líder", "Anfitrión", "Asistente"])
            
        guardar = st.form_submit_button("Registrar Miembro")
        
        if guardar:
            if nombre and celula:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO miembros (nombre_completo, telefono, celula, rol) VALUES (?, ?, ?, ?)",
                    (nombre, telefono, celula, rol)
                )
                conn.commit()
                conn.close()
                st.success(f"Miembro {nombre} registrado con éxito.")
            else:
                st.warning("Completa el nombre y la célula como mínimo.")
                
    st.subheader("Lista de Miembros Registrados")
    conn = get_db_connection()
    df_miembros = pd.read_sql_query("SELECT id, nombre_completo, telefono, celula, rol, fecha_registro FROM miembros", conn)
    conn.close()
    st.dataframe(df_miembros, use_container_width=True)

def reporte_celula():
    st.title("📋 Reporte de Célula")
    
    with st.form("form_reporte", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            celula = st.text_input("Célula")
            lider = st.text_input("Líder a Cargo")
            fecha = st.date_input("Fecha del Reporte")
        with col2:
            asist_miembros = st.number_input("Asistencia de Miembros", min_value=0, step=1)
            asist_visitas = st.number_input("Asistencia de Visitas", min_value=0, step=1)
        with col3:
            ofrenda = st.number_input("Monto de Ofrenda", min_value=0.0, step=1.0)
            observaciones = st.text_area("Observaciones / Peticiones")
            
        guardar = st.form_submit_button("Guardar Reporte")
        
        if guardar:
            if celula and lider:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO reportes_celula 
                       (celula, lider, fecha, asistencia_miembros, asistencia_visitas, ofrenda, observaciones)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (celula, lider, fecha, asist_miembros, asist_visitas, ofrenda, observaciones)
                )
                conn.commit()
                conn.close()
                st.success("Reporte guardado correctamente.")
            else:
                st.warning("Por favor ingresa la célula y el nombre del líder.")
                
    st.subheader("Historial de Reportes")
    conn = get_db_connection()
    df_rep = pd.read_sql_query("SELECT * FROM reportes_celula ORDER BY fecha DESC", conn)
    conn.close()
    st.dataframe(df_rep, use_container_width=True)

def registro_descarrilados():
    st.title("💔 Registro de Descarrilados / Ausentes")
    st.info("Espacio para dar seguimiento pastoral a las personas que se han distanciado de la iglesia o célula.")
    
    with st.form("form_descarrilados", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre de la Persona")
            telefono = st.text_input("Teléfono")
            celula = st.text_input("Célula a la que pertenecía")
        with col2:
            estado = st.selectbox("Estado de Seguimiento", ["Pendiente", "En Contacto", "Restaurado", "No Interesado"])
            motivo = st.text_area("Motivo de la ausencia / Observación pastoral")
            
        guardar = st.form_submit_button("Registrar para Seguimiento")
        
        if guardar:
            if nombre:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO descarrilados (nombre, telefono, celula, motivo, estado_seguimiento) VALUES (?, ?, ?, ?, ?)",
                    (nombre, telefono, celula, motivo, estado)
                )
                conn.commit()
                conn.close()
                st.success("Registro añadido a la lista de consolidación/seguimiento.")
            else:
                st.warning("Por favor ingrese al menos el nombre.")
                
    st.subheader("Personas en Seguimiento Pastoral")
    conn = get_db_connection()
    df_desc = pd.read_sql_query("SELECT * FROM descarrilados ORDER BY fecha_registro DESC", conn)
    conn.close()
    st.dataframe(df_desc, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. ESTRUCTURA PRINCIPAL DE LA APLICACIÓN
# -----------------------------------------------------------------------------
def main():
    if not st.session_state["logged_in"]:
        auth_screen()
    else:
        st.sidebar.write(f"👤 Usuario: **{st.session_state['user_name']}**")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state["logged_in"] = False
            st.session_state["user_name"] = ""
            st.rerun()
            
        st.sidebar.markdown("---")
        opcion = st.sidebar.radio(
            "Navegación Principales",
            [
                "Panel de Control",
                "Registro_miembro por Célula",
                "Reporte de Célula",
                "Registro de Descarrilados"
            ]
        )
        
        if opcion == "Panel de Control":
            panel_de_control()
        elif opcion == "Registro_miembro por Célula":
            registro_miembros()
        elif opcion == "Reporte de Célula":
            reporte_celula()
        elif opcion == "Registro de Descarrilados":
            registro_descarrilados()

if __name__ == "__main__":
    main()
