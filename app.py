import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

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
    
    # Tabla de Usuarios (Credenciales de acceso)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'Usuario'
        )
    """)
    
    # Insertar un usuario administrador por defecto si la tabla está vacía
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "admin123", "Administrador"))
    
    # Tabla de Células (Administración)
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
        )
    """)
    conn.commit()
    conn.close()

# Ejecutar inicialización de tablas al arrancar la app
init_db()

# ==========================================
# 2. CONTROL DE ACCESO (LOGIN / REGISTRO)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso al Sistema</h2>", unsafe_allow_html=True)
    
    # CORREGIDO: Se añade el argumento numérico 3 a st.columns()
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
                            st.success("¡Cuenta creada exitosamente! Ya puedes iniciar sesión en la pestaña superior.")
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

# Cargar el listado de células reutilizable en los formularios
conn = sqlite3.connect(DB_PATH)
cells_df = pd.read_sql_query("SELECT cell_name FROM cells", conn)
conn.close()
cell_options = cells_df['cell_name'].tolist() if not cells_df.empty else []

# ------------------------------------------
# SECCIÓN: VISTA GENERAL (DASHBOARD)
# ------------------------------------------
if menu_option == "📊 Vista General":
    st.title("📊 Panel de Control y Estadísticas")
    st.write("Resumen ejecutivo del estado de las células de la iglesia.")
    
    conn = sqlite3.connect(DB_PATH)
    # CORREGIDO: Uso correcto de .iloc[0] para extraer el valor escalar de los conteos
    tot_cells = pd.read_sql_query("SELECT COUNT(*) as total FROM cells", conn)['total'].iloc[0]
    tot_members = pd.read_sql_query("SELECT COUNT(*) as total FROM members", conn)['total'].iloc[0]
    tot_reports = pd.read_sql_query("SELECT COUNT(*) as total FROM cell_reports", conn)['total'].iloc[0]
    tot_backsliders = pd.read_sql_query("SELECT COUNT(*) as total FROM backsliders WHERE status != 'Reconciliado'", conn)['total'].iloc[0]
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
                c.execute("""
                    INSERT INTO cells (cell_name, leader_name, sector) 
                    VALUES (?, ?, ?)
                """, (new_cell_name, cell_leader, cell_sector))
                conn.commit()
                conn.close()
                st.success(f"Célula '{new_cell_name}' guardada correctamente.")
                st.rerun()
            else:
                st.error("Por favor, rellene los campos obligatorios: Nombre de Célula y Líder.")

# ------------------------------------------
# SECCIÓN: INGRESO DE NUEVOS MIEMBROS
# ------------------------------------------



    # --- Panel / Dashboard Mejorado ---
    with tab6:
        st.header("📊 Panel de Control y Análisis")
        
        # Conexión única para las consultas del panel
        conn = sqlite3.connect(DB_PATH)
        
        # ----------------------------------------------------
        # 1. BLOQUE DE KPI'S (Métricas Rápidas y Total de Amigos)
        # ----------------------------------------------------
        # Cálculo de amigos directo desde los reportes sumando la columna 'friends'
        try:
            total_amigos_rep = conn.execute("SELECT SUM(friends) FROM cell_reports").fetchone()[0] or 0
        except Exception:
            total_amigos_rep = 0
            
        total_miembros = conn.execute("SELECT COUNT(*) FROM members_stats WHERE status='activo'").fetchone()[0] or 0
        total_converts = conn.execute("SELECT COUNT(*) FROM new_converts").fetchone()[0] or 0
        total_descarriados = conn.execute("SELECT COUNT(*) FROM descarriados").fetchone()[0] or 0
        
        st.subheader("📌 Métricas Clave de la Iglesia")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric(label="👥 Miembros Activos", value=total_miembros)
        kpi2.metric(label="🙌 Nuevos Convertidos", value=total_converts)
        kpi3.metric(label="🚨 Total Descarriados", value=total_descarriados)
        kpi4.metric(label="❤️ Total Amigos (Reportados)", value=int(total_amigos_rep))
        
        st.markdown("---")
        
        # ----------------------------------------------------
        # 2. COMPARACIÓN DE MIEMBROS VERSUS DESCARRIADOS
        # ----------------------------------------------------
        st.subheader("⚖️ Comparativa: Miembros Activos vs Descarriados por Célula")
        
        # Consultas agrupadas por célula
        df_m_cell = pd.read_sql_query("SELECT cell, COUNT(*) as Miembros FROM members_stats WHERE status='activo' GROUP BY cell", conn)
        df_d_cell = pd.read_sql_query("SELECT cell, COUNT(*) as Descarriados FROM descarriados GROUP BY cell", conn)
        
        # Unificar ambos flujos de datos
        df_comparativo = pd.merge(df_m_cell, df_d_cell, on="cell", how="outer").fillna(0)
        df_comparativo.rename(columns={"cell": "Célula"}, inplace=True)
        
        if not df_comparativo.empty:
            # Gráfico de barras comparativo nativo
            st.bar_chart(data=df_comparativo.set_index("Célula"), y=["Miembros", "Descarriados"], color=["#2ecc71", "#e74c3c"])
        else:
            st.info("No hay datos suficientes para generar la gráfica comparativa.")
            
        st.markdown("---")
        
        # ----------------------------------------------------
        # 3. REPORTES DE CÉLULAS Y EVOLUCIÓN FINANCIERA (OFRENDAS)
        # ----------------------------------------------------
        st.subheader("📈 Análisis de Ofrendas y Reportes Globales")
        
        df_reports = pd.read_sql_query("""
            SELECT meeting_date as Fecha, cell_name as Célula, offering as Ofrenda, 
                   (adults + youth + children + friends + visits) as AsistenciaTotal 
            FROM cell_reports ORDER BY meeting_date ASC
        """, conn)
        
        if not df_reports.empty:
            col_graph1, col_graph2 = st.columns(2)
            
            with col_graph1:
                st.markdown("**Evolución Histórica de Ofrendas**")
                st.line_chart(data=df_reports, x="Fecha", y="Ofrenda", color="#f1c40f")
                
            with col_graph2:
                st.markdown("**Tendencias de Asistencia Total en Reuniones**")
                st.line_chart(data=df_reports, x="Fecha", y="AsistenciaTotal", color="#3498db")
                
            st.markdown("**Historial Completo de Reportes de Células**")
            st.dataframe(df_reports, use_container_width=True)
        else:
            st.info("Aún no se han registrado reportes de células para proyectar análisis financieros.")
            
        st.markdown("---")
        
        # ----------------------------------------------------
        # 4. CRECIMIENTO DE CÉLULAS (Nuevas incorporaciones por fecha)
        # ----------------------------------------------------
        st.subheader("🌱 Crecimiento Histórico e Incorporaciones")
        
        df_growth_m = pd.read_sql_query("SELECT ingreso_date as Fecha, COUNT(*) as Nuevos_Miembros FROM members_stats GROUP BY ingreso_date", conn)
        df_growth_c = pd.read_sql_query("SELECT conversion_date as Fecha, COUNT(*) as Nuevos_Convertidos FROM new_converts GROUP BY conversion_date", conn)
        
        df_growth = pd.merge(df_growth_m, df_growth_c, on="Fecha", how="outer").fillna(0).sort_values("Fecha")
        
        if not df_growth.empty:
            st.markdown("Registros cronológicos de ingresos a la congregación:")
            st.area_chart(data=df_growth.set_index("Fecha"), y=["Nuevos_Miembros", "Nuevos_Convertidos"])
        else:
            st.info("Sin registros de fechas para trazar curvas de crecimiento.")
            
        st.markdown("---")
        
        # ----------------------------------------------------
        # 5. REGISTRO POR CÉLULAS A DESCARGAR (Filtros y exportación)
        # ----------------------------------------------------
        st.subheader("📥 Exportar Datos Consolidados por Célula")
        
        # Obtener listado de células vigentes para el filtro
        cells_query = pd.read_sql_query("SELECT cell_name FROM cells", conn)
        cell_list = cells_query['cell_name'].tolist() if not cells_query.empty else []
        
        if cell_list:
            selected_cell = st.selectbox("Seleccione la célula que desea inspeccionar y descargar:", cell_list)
            
            # Pestañas secundarias de filtrado de información limpia
            sub_tab_m, sub_tab_c, sub_tab_r = st.tabs(["👥 Miembros", "🙌 Convertidos Asignados", "📌 Reportes Enviados"])
            
            with sub_tab_m:
                df_download_m = pd.read_sql_query("SELECT full_name, age, contact, sex, discipleship_type, ministry, status FROM members_stats WHERE cell=?", conn, params=(selected_cell,))
                if not df_download_m.empty:
                    st.dataframe(df_download_m, use_container_width=True)
                    csv_m = df_download_m.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Descargar Miembros (.CSV)", data=csv_m, file_name=f"miembros_{selected_cell}.csv", mime="text/csv")
                else:
                    st.info("No se registran miembros en esta célula.")
                    
            with sub_tab_c:
                df_download_c = pd.read_sql_query("SELECT full_name, age, contact, address, decision_type, conversion_date FROM new_converts WHERE assigned_cell=?", conn, params=(selected_cell,))
                if not df_download_c.empty:
                    st.dataframe(df_download_c, use_container_width=True)
                    csv_c = df_download_c.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Descargar Convertidos (.CSV)", data=csv_c, file_name=f"convertidos_{selected_cell}.csv", mime="text/csv")
                else:
                    st.info("No hay nuevos convertidos asignados a esta célula.")
                    
            with sub_tab_r:
                df_download_r = pd.read_sql_query("SELECT meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, offering FROM cell_reports WHERE cell_name=?", conn, params=(selected_cell,))
                if not df_download_r.empty:
                    st.dataframe(df_download_r, use_container_width=True)
                    csv_r = df_download_r.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Descargar Reportes (.CSV)", data=csv_r, file_name=f"reportes_{selected_cell}.csv", mime="text/csv")
                else:
                    st.info("Esta célula no cuenta con reportes históricos enviados.")
        else:
            st.warning("Debe registrar al menos una célula desde la pestaña de '⚙️ Administración' para poder usar el gestor de descargas.")
            
        conn.close()


    
