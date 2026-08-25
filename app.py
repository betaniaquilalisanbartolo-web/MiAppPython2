import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
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
        )
    """)
    
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)", ("admin", "admin123", "Administrador"))
        
    # Tabla de Células (Administración con columna de Metas Anuales)
    c.execute("""
        CREATE TABLE IF NOT EXISTS cells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cell_name TEXT UNIQUE NOT NULL,
            leader_name TEXT NOT NULL,
            sector TEXT,
            yearly_target INTEGER DEFAULT 10
        )
    """)
    
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
        )
    """)
    
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
        )
    """)
    
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
        )
    """)
    
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
        )
    """)
    
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
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = "Usuario"

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔑 Acceso al Sistema Ministerial</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col2:
        tab_login, tab_signup = st.tabs(["🔐 Iniciar Sesión", "📝 Crear una Cuenta"])
        
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
    st.markdown(f"### 👤 Sesión Activa\nConectado como: **{st.session_state.username}**\nRol: {st.session_state.role}")
    st.markdown("---")
    st.markdown("### 🎬 Menú del Panel")
    
    menu_option = st.radio(
        "Seleccione una sección:",
        [
            "📊 Vista General",
            "⚙️ Configuración de Células",
            "👤 Ingreso de Nuevos Miembros",
            "🏠 Reportes de Células",
            "🍇 Seguimiento de Almas",
            "📆 Agenda y Calendario"
        ]
    )
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = "Usuario"
        st.rerun()

        conn.close()
        
        if not df_metas.empty:
            # Calcular porcentaje de cumplimiento
            df_metas['% Cumplimiento'] = (df_metas['Miembros Registrados Actuales'] / df_metas['Meta de Nuevos Miembros'].replace(0, 1)) * 100
            df_metas['% Cumplimiento'] = df_metas['% Cumplimiento'].round(1)
            
            # Mostrar tabla interactiva
            st.dataframe(df_metas, use_container_width=True)
            
            # Gráfico de barras simple para comparar meta vs actual
            st.bar_chart(df_metas.set_index('Célula')[['Meta de Nuevos Miembros', 'Miembros Registrados Actuales']])
        else:
            st.info("No hay datos de metas o células para mostrar.")
    except Exception as e:
        st.error(f"Error al cargar las métricas: {e}")

# B. CONFIGURACIÓN DE CÉLULAS
elif menu_option == "⚙️ CONFIGURACIÓN DE CÉLULAS":
    st.title("⚙️ Administración de Células")
    
    tab_crear, tab_ver = st.tabs(["➕ Registrar Célula", "📋 Células Existentes"])
    
    with tab_crear:
        with st.form("form_celulas"):
            cell_name = st.text_input("Nombre de la Célula (Único)")
            leader_name = st.text_input("Nombre del Líder")
            sector = st.text_input("Sector / Zona")
            yearly_target = st.number_input("Meta Anual de Nuevos Miembros", min_value=1, value=10)
            
            btn_celula = st.form_submit_button("Guardar Célula")
            if btn_celula:
                if cell_name and leader_name:
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("INSERT INTO cells (cell_name, leader_name, sector, yearly_target) VALUES (?, ?, ?, ?)",
                                  (cell_name, leader_name, sector, yearly_target))
                        conn.commit()
                        conn.close()
                        st.success(f"Célula '{cell_name}' registrada con éxito.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("El nombre de la célula ya existe.")
                else:
                    st.error("Por favor llene los campos obligatorios (Nombre y Líder).")
                    
    with tab_ver:
        conn = sqlite3.connect(DB_PATH)
        df_c = pd.read_sql_query("SELECT id, cell_name as Célula, leader_name as Líder, sector as Sector, yearly_target as Meta FROM cells", conn)
        conn.close()
        st.dataframe(df_c, use_container_width=True)

# C. INGRESO DE NUEVOS MIEMBROS
elif menu_option == "👤 Ingreso de Nuevos Miembros":
    st.title("👤 Registro de Nuevos Miembros")
    
    with st.form("form_miembros", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Nombre Completo *")
            phone = st.text_input("Teléfono")
            email = st.text_input("Correo Electrónico")
            address = st.text_area("Dirección Residencial")
            birth_date = st.date_input("Fecha de Nacimiento", min_value=datetime(1920,1,1)).strftime('%Y-%m-%d')
            gender = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])
            marital_status = st.selectbox("Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión Libre"])
            assigned_cell = st.selectbox("Asignar a Célula", opciones_celulas_global)
            conversion_date = st.date_input("Fecha de Conversión").strftime('%Y-%m-%d')
            
        with col2:
            baptized = st.selectbox("¿Es Bautizado?", ["No", "Sí"])
            baptism_date = st.date_input("Fecha de Bautizo (Si aplica)").strftime('%Y-%m-%d')
            membership_status = st.selectbox("Estatus de Membresía", ["Asistente", "Miembro Activo", "En Observación", "Traslado"])
            emergency_contact = st.text_input("Contacto de Emergencia")
            emergency_phone = st.text_input("Teléfono de Emergencia")
            invited_by = st.text_input("Invitado por")
            spiritual_gift = st.text_input("Don Espiritual / Ministerio")
            family_members = st.number_input("Cantidad de Familiares en la Iglesia", min_value=0, value=0, step=1)
            prayer_requests = st.text_area("Peticiones de Oración")
            observations = st.text_area("Observaciones Adicionales")
            
        btn_miembro = st.form_submit_button("Registrar Miembro")
        if btn_miembro:
            if full_name:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""INSERT INTO members (full_name, phone, email, address, birth_date, gender, marital_status, 
                          assigned_cell, conversion_date, baptized, baptism_date, membership_status, emergency_contact, 
                          emergency_phone, prayer_requests, invited_by, spiritual_gift, family_members, observations) 
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                          (full_name, phone, email, address, birth_date, gender, marital_status, assigned_cell, 
                           conversion_date, baptized, baptism_date, membership_status, emergency_contact, emergency_phone, 
                           prayer_requests, invited_by, spiritual_gift, family_members, observations))
                conn.commit()
                conn.close()
                st.success(f"¡Miembro '{full_name}' guardado correctamente!")
            else:
                st.error("El nombre completo es obligatorio.")

# D. REPORTES DE CÉLULAS
elif menu_option == "🏠 Reportes de Células":
    st.title("🏠 Reportes de Reuniones de Célula")
    
    tab_rep_crear, tab_rep_ver = st.tabs(["📝 Subir Reporte", "📊 Historial de Reportes"])
    
    with tab_rep_crear:
        with st.form("form_reportes"):
            col1, col2 = st.columns(2)
            with col1:
                r_cell = st.selectbox("Seleccione la Célula", [c for c in opciones_celulas_global if c != "Ninguna"])
                r_date = st.date_input("Fecha de la Reunión").strftime('%Y-%m-%d')
                r_leader = st.text_input("Líder / Anfitrión del Hogar")
                r_topic = st.text_input("Tema Bíblico Impartido")
                r_text = st.text_input("Texto Bíblico Central")
                r_offering = st.number_input("Ofrenda Recolectada ($)", min_value=0.0, step=0.01)
                
            with col2:
                r_adults = st.number_input("Adultos Asistentes", min_value=0, step=1)
                r_youth = st.number_input("Jóvenes Asistentes", min_value=0, step=1)
                r_children = st.number_input("Niños Asistentes", min_value=0, step=1)
                r_friends = st.number_input("Amigos / Invitados", min_value=0, step=1)
                r_visits = st.number_input("Visitas Realizadas en la Semana", min_value=0, step=1)
                r_spiritual = st.select_slider("Nivel Espiritual de la Reunión", options=["Bajo", "Regular", "Bueno", "Excelente", "Ferviente"])
                r_attendance = st.slider("Porcentaje de Asistencia Estimado", 0, 100, 100)
                
            r_needs = st.text_area("Necesidades Especiales Reportadas")
            r_photo = st.file_uploader("Captura de asistencia o foto de la reunión", type=["jpg", "jpeg", "png"])
            
            btn_reporte = st.form_submit_button("Enviar Reporte Semanal")
            if btn_reporte:
                foto_final_path = ""
                if r_photo is not None:
                    # Guardar archivo en el servidor local con nombre único basado en timestamp
                    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{r_photo.name}"
                    foto_final_path = os.path.join(MEDIA_DIR, filename)
                    with open(foto_final_path, "wb") as f:
                        f.write(r_photo.getbuffer())
                
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""INSERT INTO cell_reports (cell_name, meeting_date, adults, youth, children, friends, 
                          visits, home_leader, biblical_topic, central_text, offering, needs, spiritual_level, 
                          attendance_level, foto_path) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                          (r_cell, r_date, r_adults, r_youth, r_children, r_friends, r_visits, r_leader, 
                           r_topic, r_text, r_offering, r_needs, r_spiritual, r_attendance, foto_final_path))
                conn.commit()
                conn.close()
                st.success("Reporte consolidado e ingresado al sistema.")
                
    with tab_rep_ver:
        conn = sqlite3.connect(DB_PATH)
        df_rep = pd.read_sql_query("SELECT * FROM cell_reports ORDER BY meeting_date DESC", conn)
        conn.close()
        st.dataframe(df_rep, use_container_width=True)
        if not df_rep.empty:
            st.download_button("Descargar Reportes (CSV)", data=to_csv(df_rep), file_name="reportes_celulas.csv", mime="text/csv")

# E. SEGUIMIENTO DE ALMAS
elif menu_option == "🍇 Seguimiento de Almas":
    st.title("🍇 Plan de Consolidación y Seguimiento")
    st.write("Administración de descarrilados, personas distanciadas o casos especiales de restauración.")
    
    tab_seg_crear, tab_seg_ver = st.tabs(["➕ Registrar Alma en Seguimiento", "📋 Casos Activos"])
    
    with tab_seg_crear:
        with st.form("form_seguimiento"):
            b_name = st.text_input("Nombre de la Persona *")
            b_phone = st.text_input("Teléfono de Contacto")
            b_cell = st.selectbox("Célula de Procedencia / Cercana", opciones_celulas_global)
            b_last = st.date_input("Última Fecha de Asistencia").strftime('%Y-%m-%d')
            b_risk = st.selectbox("Nivel de Riesgo de Abandono", ["Bajo", "Medio", "Alto", "Crítico"])


# Carga global rápida de opciones de células
opciones_celulas_global = ["Ninguna"]
try:
    conn = sqlite3.connect(DB_PATH)
    cells_df = pd.read_sql_query("SELECT cell_name FROM cells ORDER BY cell_name ASC", conn)
    conn.close()
    if not cells_df.empty:
        opciones_celulas_global += cells_df['cell_name'].tolist()
except:
    pass

# ==========================================
# 4. LÓGICA DE LAS SECCIONES DEL PANEL
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
    kpi3.metric(label="📋 Reportes Entregados", value=tot_reports)
    kpi4.metric(label="⚠️ Casos en Seguimiento", value=tot_backsliders)
    st.markdown("---")
    
    st.subheader("📈 Monitoreo de Metas Anuales por Célula")
    
