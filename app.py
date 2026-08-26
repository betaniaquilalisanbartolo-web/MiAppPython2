import hashlib
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    
    # Tabla de Células (Gestión centralizada de células)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS celulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        lider TEXT,
        anfitrion TEXT,
        direccion TEXT,
        fecha_creacion DATE DEFAULT CURRENT_DATE
    )
    """)
    
    # Tabla de Miembros por Célula
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS miembros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        telefono TEXT,
        celula TEXT NOT NULL,
        rol TEXT NOT NULL,
        fecha_registro DATE DEFAULT CURRENT_DATE
    )
    """)
    
    # Tabla de Reportes de Célula
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reportes_celula (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        celula TEXT NOT NULL,
        lider TEXT NOT NULL,
        jefe_casa TEXT,
        tema_biblico TEXT,
        texto_biblico TEXT,
        fecha DATE NOT NULL,
        asistencia_miembros INTEGER NOT NULL DEFAULT 0,
        asistencia_visitas INTEGER NOT NULL DEFAULT 0,
        asistencia_amigos INTEGER NOT NULL DEFAULT 0,
        asistencia_ninos INTEGER NOT NULL DEFAULT 0,
        ofrenda REAL DEFAULT 0.0,
        observaciones TEXT
    )
    """)
    
    # Tabla de Descarrilados / Ausentes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS descarrilados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        celula TEXT,
        motivo TEXT,
        estado_seguimiento TEXT DEFAULT 'Pendiente',
        fecha_registro DATE DEFAULT CURRENT_DATE
    )
    """)

    # Migración automática de columnas para bases de datos existentes
    columnas_reportes = [
        ("jefe_casa", "TEXT"),
        ("tema_biblico", "TEXT"),
        ("texto_biblico", "TEXT"),
        ("asistencia_amigos", "INTEGER DEFAULT 0"),
        ("asistencia_ninos", "INTEGER DEFAULT 0"),
        ("observaciones", "TEXT")
    ]
    for col_nombre, col_tipo in columnas_reportes:
        try:
            cursor.execute(f"ALTER TABLE reportes_celula ADD COLUMN {col_nombre} {col_tipo}")
        except sqlite3.OperationalError:
            pass  # La columna ya existe

    conn.commit()
    conn.close()

init_db()

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES DE DATOS
# -----------------------------------------------------------------------------
def obtener_lista_celulas():
    """Obtiene la lista única de células registradas en 'celulas', 'miembros' y 'reportes'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT celula FROM (
            SELECT nombre AS celula FROM celulas WHERE nombre IS NOT NULL AND nombre != ''
            UNION
            SELECT celula FROM miembros WHERE celula IS NOT NULL AND celula != ''
            UNION
            SELECT celula FROM reportes_celula WHERE celula IS NOT NULL AND celula != ''
        ) ORDER BY celula ASC
    """)
    celulas = [row["celula"] for row in cursor.fetchall()]
    conn.close()
    return celulas

def obtener_lider_por_celula(nombre_celula):
    """Obtiene el líder registrado en la tabla celulas, reportes previos o miembros."""
    if not nombre_celula:
        return ""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Buscar en la tabla celulas
    cursor.execute("SELECT lider FROM celulas WHERE nombre = ?", (nombre_celula,))
    res = cursor.fetchone()
    if res and res["lider"]:
        conn.close()
        return res["lider"]
        
    # 2. Buscar en reportes previos
    cursor.execute(
        "SELECT lider FROM reportes_celula WHERE celula = ? ORDER BY id DESC LIMIT 1",
        (nombre_celula,),
    )
    res = cursor.fetchone()
    if res and res["lider"]:
        conn.close()
        return res["lider"]

    # 3. Buscar en miembros
    cursor.execute(
        "SELECT nombre_completo FROM miembros WHERE celula = ? AND rol = 'Líder' LIMIT 1",
        (nombre_celula,),
    )
    res = cursor.fetchone()
    conn.close()
    return res["nombre_completo"] if res else ""

# -----------------------------------------------------------------------------
# 2. FUNCIONES DE SEGURIDAD
# -----------------------------------------------------------------------------
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# -----------------------------------------------------------------------------
# 3. CONTROL DE SESIÓN Y AUTENTICACIÓN
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""

def auth_screen():
    st.title("⛪ Sistema de Gestión Ecuménica y Células")
    opcion = st.sidebar.selectbox(
        "Acceso al Sistema", ["Iniciar Sesión", "Crear nueva cuenta de usuario"]
    )
    if opcion == "Iniciar Sesión":
        st.subheader("🔑 Iniciar Sesión")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", type="primary"):
            conn = get_db_connection()
            cursor = conn.cursor()
            hashed_pw = make_hashes(password)
            cursor.execute(
                "SELECT * FROM usuarios WHERE email = ? AND password = ?",
                (email, hashed_pw),
            )
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
                        (nombre, email, make_hashes(password)),
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

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reportes", len(df_reportes))
    with col2:
        if not df_reportes.empty:
            total_asistencia = (
                df_reportes["asistencia_miembros"].sum()
                + df_reportes["asistencia_visitas"].sum()
                + df_reportes.get("asistencia_amigos", pd.Series([0])).sum()
                + df_reportes.get("asistencia_ninos", pd.Series([0])).sum()
            )
        else:
            total_asistencia = 0
        st.metric("Asistencia Total Acumulada", total_asistencia)
    with col3:
        st.metric("Total Miembros Registrados", len(df_miembros))
    with col4:
        total_ofrenda = (
            df_reportes["ofrenda"].sum() if not df_reportes.empty else 0.0
        )
        st.metric("Total Ofrendas ($)", f"${total_ofrenda:,.2f}")

    st.markdown("---")
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("📈 Asistencia por Célula")
        if not df_reportes.empty:
            columnas_asistencia = [
                c for c in [
                    "asistencia_miembros",
                    "asistencia_visitas",
                    "asistencia_amigos",
                    "asistencia_ninos",
                ] if c in df_reportes.columns
            ]
            df_celula_asistencia = (
                df_reportes.groupby("celula")[columnas_asistencia]
                .sum()
                .reset_index()
            )
            fig_celulas = px.bar(
                df_celula_asistencia,
                x="celula",
                y=columnas_asistencia,
                title="Asistencia Detallada por Célula",
                barmode="group",
                labels={"value": "Personas", "celula": "Célula", "variable": "Categoría"},
            )
            st.plotly_chart(fig_celulas, use_container_width=True)
        else:
            st.info("Aún no hay reportes registrados para mostrar gráficos.")

    with col_chart2:
        st.subheader("👥 Distribución de Miembros")
        if not df_miembros.empty:
            df_miembros_celula = (
                df_miembros["celula"].value_counts().reset_index()
            )
            df_miembros_celula.columns = ["Célula", "Cantidad"]
            fig_miembros = px.pie(
                df_miembros_celula,
                names="Célula",
                values="Cantidad",
                title="Distribución de Miembros por Célula",
                hole=0.4,
            )
            st.plotly_chart(fig_miembros, use_container_width=True)
        else:
            st.info("Aún no hay miembros registrados para mostrar gráficos.")

def gestion_celulas():
    st.title("🏡 Registro y Gestión de Células")
    st.markdown("Registra las células principales para mantener los datos organizados en todo el sistema.")
    
    with st.form("form_celulas", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre_celula = st.text_input("Nombre / Número de la Célula *")
            lider = st.text_input("Líder Encargado")
        with col2:
            anfitrion = st.text_input("Anfitrión / Jefe de Casa")
            direccion = st.text_input("Dirección o Sector")
            
        guardar = st.form_submit_button("Registrar Célula")
        
        if guardar:
            if nombre_celula:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO celulas (nombre, lider, anfitrion, direccion) VALUES (?, ?, ?, ?)",
                        (nombre_celula.strip(), lider.strip(), anfitrion.strip(), direccion.strip())
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"Célula '{nombre_celula}' creada correctamente.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Ya existe una célula registrada con ese nombre.")
            else:
                st.warning("El nombre de la célula es obligatorio.")
                
    st.subheader("Lista de Células Registradas")
    conn = get_db_connection()
    df_celulas = pd.read_sql_query("SELECT id, nombre, lider, anfitrion, direccion, fecha_creacion FROM celulas", conn)
    conn.close()
    st.dataframe(df_celulas, use_container_width=True)

def registro_miembros():
    st.title("📌 Registro de Miembro por Célula")
    celulas_existentes = obtener_lista_celulas()
    
    with st.form("form_miembro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Completo")
            telefono = st.text_input("Teléfono / WhatsApp")
        with col2:
            opcion_celula = st.selectbox(
                "Seleccionar Célula",
                ["-- Seleccionar Célula --"] + celulas_existentes + ["+ Registrar Nueva Célula"],
            )
            nueva_celula_input = ""
            if opcion_celula == "+ Registrar Nueva Célula" or not celulas_existentes:
                nueva_celula_input = st.text_input("Nombre / Número de la Nueva Célula")
            
            rol = st.selectbox(
                "Rol en la Célula", ["Miembro", "Líder", "Anfitrión", "Asistente"]
            )
            
        guardar = st.form_submit_button("Registrar Miembro")
        
        if guardar:
            celula_final = (
                nueva_celula_input if opcion_celula == "+ Registrar Nueva Célula" else opcion_celula
            )
            if celula_final == "-- Seleccionar Célula --":
                celula_final = ""
                
            if nombre and celula_final:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO miembros (nombre_completo, telefono, celula, rol) VALUES (?, ?, ?, ?)",
                    (nombre, telefono, celula_final, rol),
                )
                conn.commit()
                conn.close()
                st.success(f"Miembro {nombre} registrado con éxito en la célula '{celula_final}'.")
                st.rerun()
            else:
                st.warning("Completa el nombre y la célula como mínimo.")

    st.subheader("Lista de Miembros Registrados")
    conn = get_db_connection()
    df_miembros = pd.read_sql_query(
        "SELECT id, nombre_completo, telefono, celula, rol, fecha_registro FROM miembros", conn
    )
    conn.close()
    st.dataframe(df_miembros, use_container_width=True)

def reporte_celula():
    st.title("📋 Reporte de Célula")
    celulas_existentes = obtener_lista_celulas()

    st.markdown("### Selecciona la Célula")
    if celulas_existentes:
        celula_seleccionada = st.selectbox(
            "Seleccione una Célula existente:",
            celulas_existentes + ["+ Otra Célula"],
        )
        if celula_seleccionada == "+ Otra Célula":
            celula_nombre = st.text_input("Nombre de la nueva Célula:")
        else:
            celula_nombre = celula_seleccionada
    else:
        st.info("No hay células registradas. Ingresa el nombre manualmente:")
        celula_nombre = st.text_input("Nombre de la Célula:")

    lider_sugerido = obtener_lider_por_celula(celula_nombre) if celula_nombre else ""

    with st.form("form_reporte", clear_on_submit=True):
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            lider = st.text_input("Líder a Cargo", value=lider_sugerido)
            jefe_casa = st.text_input("Nombre del Jefe de Casa / Anfitrión")
            fecha = st.date_input("Fecha del Reporte")
        with col2:
            tema_biblico = st.text_input("Tema Bíblico")
            texto_biblico = st.text_input("Texto Bíblico / Cita")

        st.markdown("#### Asistencia y Ofrenda")
        col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns(5)
        with col_a1:
            asist_miembros = st.number_input("Miembros", min_value=0, step=1)
        with col_a2:
            asist_visitas = st.number_input("Visitas", min_value=0, step=1)
        with col_a3:
            asist_amigos = st.number_input("Amigos", min_value=0, step=1)
        with col_a4:
            asist_ninos = st.number_input("Niños", min_value=0, step=1)
        with col_a5:
            ofrenda = st.number_input("Monto Ofrenda ($)", min_value=0.0, step=1.0)

        observaciones = st.text_area("Observaciones / Peticiones de Oración")
        guardar = st.form_submit_button("Guardar Reporte")

        if guardar:
            if celula_nombre and lider:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO reportes_celula 
                    (celula, lider, jefe_casa, tema_biblico, texto_biblico, fecha, asistencia_miembros, asistencia_visitas, asistencia_amigos, asistencia_ninos, ofrenda, observaciones) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        celula_nombre,
                        lider,
                        jefe_casa,
                        tema_biblico,
                        texto_biblico,
                        fecha,
                        asist_miembros,
                        asist_visitas,
                        asist_amigos,
                        asist_ninos,
                        ofrenda,
                        observaciones,
                    ),
                )
                conn.commit()
                conn.close()
                st.success("Reporte guardado correctamente.")
                st.rerun()
            else:
                st.warning("Por favor asegúrate de especificar el nombre de la célula y del líder.")

    st.subheader("Historial de Reportes")
    conn = get_db_connection()
    df_rep = pd.read_sql_query(
        "SELECT * FROM reportes_celula ORDER BY fecha DESC", conn
    )
    conn.close()
    st.dataframe(df_rep, use_container_width=True)

def registro_descarrilados():
    st.title("💔 Registro de Descarrilados / Ausentes")
    st.info("Espacio para dar seguimiento pastoral a las personas que se han distanciado de la iglesia o célula.")
    celulas_existentes = obtener_lista_celulas()

    with st.form("form_descarrilados", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre de la Persona")
            telefono = st.text_input("Teléfono")
            celula = st.selectbox(
                "Célula a la que pertenecía",
                ["-- Ninguna / Desconocida --"] + celulas_existentes,
            )
        with col2:
            estado = st.selectbox(
                "Estado de Seguimiento",
                ["Pendiente", "En Contacto", "Restaurado", "No Interesado"],
            )
            motivo = st.text_area("Motivo de la ausencia / Observación pastoral")

        guardar = st.form_submit_button("Registrar para Seguimiento")

        if guardar:
            if nombre:
                celula_val = "" if celula == "-- Ninguna / Desconocida --" else celula
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO descarrilados (nombre, telefono, celula, motivo, estado_seguimiento) VALUES (?, ?, ?, ?, ?)",
                    (nombre, telefono, celula_val, motivo, estado),
                )
                conn.commit()
                conn.close()
                st.success("Registro añadido a la lista de consolidación/seguimiento.")
                st.rerun()
            else:
                st.warning("Por favor ingrese al menos el nombre.")

    st.subheader("Personas en Seguimiento Pastoral")
    conn = get_db_connection()
    df_desc = pd.read_sql_query(
        "SELECT * FROM descarrilados ORDER BY fecha_registro DESC", conn
    )
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
            "Navegación Principal",
            [
                "Panel de Control",
                "Gestión de Células",
                "Registro de Miembro por Célula",
                "Reporte de Célula",
                "Registro de Descarrilados",
            ],
        )

        if opcion == "Panel de Control":
            panel_de_control()
        elif opcion == "Gestión de Células":
            gestion_celulas()
        elif opcion == "Registro de Miembro por Célula":
            registro_miembros()
        elif opcion == "Reporte de Célula":
            reporte_celula()
        elif opcion == "Registro de Descarrilados":
            registro_descarrilados()

if __name__ == "__main__":
    main()
