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
    
    # Tabla de Células (Administración)
    c.execute("""
        CREATE TABLE IF NOT EXISTS cells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cell_name TEXT NOT NULL,
            leader_name TEXT NOT NULL,
            sector TEXT
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
            cell_name TEXT,
            last_attendance TEXT,
            reason TEXT,
            action_plan TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

# Ejecutar inicialización de tablas al arrancar la app
init_db()

# ==========================================
# 2. CONTROL DE ACCESO / CONTROL DE SESIÓN
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Formulario de inicio de sesión (Login)
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 Control de Acceso</h2>", unsafe_allow_html=True)
    
    # Contenedor centrado para el login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            login_button = st.form_submit_button("Ingresar al Panel")
            
            if login_button:
                if username == "admin" and password == "admin123":
                    st.session_state.logged_in = True
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
    st.stop()

# ==========================================
# 3. INTERFAZ PRINCIPAL DEL PANEL DE CONTROL
# ==========================================

# Barra lateral (Sidebar) con información de usuario y navegación
with st.sidebar:
    st.markdown("### 👤 Sesión Activa")
    st.write("Conectado como: **Administrador**")
    
    st.markdown("---")
    st.markdown("### 🧭 Navegación")
    menu_option = st.radio(
        "Seleccione una sección:",
        ["📊 Vista General", "⚙️ Administración", "📝 Reportes de Células", "👣 Seguimiento de Descarrilados"]
    )
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ------------------------------------------
# SECCIÓN: VISTA GENERAL (DASHBOARD)
# ------------------------------------------
if menu_option == "📊 Vista General":
    st.title("📊 Panel de Control y Estadísticas")
    st.write("Resumen ejecutivo del estado de las células de la iglesia.")
    
    conn = sqlite3.connect(DB_PATH)
    # Consultas rápidas para indicadores (KPIs)
    tot_cells = pd.read_sql_query("SELECT COUNT(*) as total FROM cells", conn)['total'].iloc[0]
    tot_reports = pd.read_sql_query("SELECT COUNT(*) as total FROM cell_reports", conn)['total'].iloc[0]
    tot_backsliders = pd.read_sql_query("SELECT COUNT(*) as total FROM backsliders WHERE status != 'Reconciliado'", conn)['total'].iloc[0]
    conn.close()
    
    # Tarjetas informativas superiores
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="🏠 Células Registradas", value=int(tot_cells))
    kpi2.metric(label="📋 Reportes Recibidos", value=int(tot_reports))
    kpi3.metric(label="👣 Casos en Seguimiento (Apartados)", value=int(tot_backsliders))

# ------------------------------------------
# SECCIÓN: ADMINISTRACIÓN
# ------------------------------------------
elif menu_option == "⚙️ Administración":
    st.title("⚙️ Administración del Sistema")
    st.subheader("Registro de Nuevas Células y Líderes")
    
    with st.form("registro_celula"):
        new_cell_name = st.text_input("Nombre de la Célula")
        cell_leader = st.text_input("Nombre del Líder")
        cell_sector = st.text_input("Sector / Zona")
        
        submit_cell = st.form_submit_button("Registrar Célula")
        
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
                st.success(f"Célula '{new_cell_name}' registrada con éxito.")
                st.rerun()
            else:
                st.error("Por favor, rellene los campos obligatorios: Nombre de Célula y Líder.")

# ------------------------------------------
# SECCIÓN: REGISTRO DE REPORTES
# ------------------------------------------
elif menu_option == "📝 Reportes de Células":
    st.title("📝 Reportes de Actividad")
    st.subheader("Formulario de Reportes de Células")
    
    conn = sqlite3.connect(DB_PATH)
    cells = pd.read_sql_query("SELECT cell_name FROM cells", conn)
    conn.close()
    cell_options = cells['cell_name'].tolist() if not cells.empty else []
    
    with st.form("registro_reporte"):
        cell_name = st.selectbox("Célula", cell_options)
        meeting_date = st.date_input("Fecha de reunión")
        adults = st.number_input("Adultos", min_value=0, step=1)
        youth = st.number_input("Jóvenes", min_value=0, step=1)
        children = st.number_input("Niños", min_value=0, step=1)
        friends = st.number_input("Amigos", min_value=0, step=1)
        visits = st.number_input("Visitas", min_value=0, step=1)
        house_leader = st.text_input("Líder de casa")
        biblical_theme = st.text_input("Tema bíblico")
        central_text = st.text_input("Texto central")
        offering = st.number_input("Ofrenda", min_value=0.0, step=0.01)
        needs = st.text_area("Necesidades reportadas")
        spiritual_level = st.select_slider("Nivel espiritual", options=["Bajo", "Regular", "Bueno", "Excelente"])
        attendance_level = st.slider("Porcentaje asistencia", 0, 100, 50)
        submit_report = st.form_submit_button("Guardar Reporte")
        
        if submit_report:
            if cell_name:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""
                    INSERT INTO cell_reports 
                    (cell_name, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (cell_name, meeting_date.strftime("%Y-%m-%d"), adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level))
                conn.commit()
                conn.close()
                st.success("Reporte de célula guardado exitosamente.")
                st.rerun()
            else:
                st.error("Primero debe registrar una célula en la sección de Administración.")

# ------------------------------------------
# SECCIÓN: SEGUIMIENTO DE DESCARRILADOS
# ------------------------------------------
elif menu_option == "👣 Seguimiento de Descarrilados":
    st.title("👣 Módulo de Consolidación")
    st.subheader("Registro y Seguimiento de Personas Apartadas / Descarrilados")
    
    conn = sqlite3.connect(DB_PATH)
    cells_df = pd.read_sql_query("SELECT cell_name FROM cells", conn)
    conn.close()
    cell_options_desc = cells_df['cell_name'].tolist() if not cells_df.empty else []

    with st.form("registro_descarrilado"):
        person_name = st.text_input("Nombre Completo de la Persona")
        assigned_cell = st.selectbox("Célula Responsable del Seguimiento", cell_options_desc)
        last_attendance = st.date_input("Fecha aproximada de última asistencia")
        reason = st.text_area("Motivo del alejamiento (si se conoce)")
        action_plan = st.text_input("Acción a tomar (Ej: Visita, llamada, oración)")
        current_status = st.selectbox("Estado actual", ["Apartado", "En contacto", "Visitado", "Reconciliado"])
        
        submit_backslider = st.form_submit_button("Guardar Registro de Seguimiento")
        
        if submit_backslider:
            if person_name:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""
                    INSERT INTO backsliders 
                    (person_name, cell_name, last_attendance, reason, action_plan, status) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (person_name, assigned_cell, last_attendance.strftime("%Y-%m-%d"), reason, action_plan, current_status))
                conn.commit()
                conn.close()
                

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


    
