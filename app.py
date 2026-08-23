import streamlit as st
import sqlite3
import pandas as pd
import datetime

DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tablas principales
    c.execute('''CREATE TABLE IF NOT EXISTS cell_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, meeting_date TEXT,
        adults INTEGER, youth INTEGER, children INTEGER, friends INTEGER, visits INTEGER,
        house_leader TEXT, biblical_theme TEXT, central_text TEXT, offering REAL,
        needs TEXT, spiritual_level TEXT, attendance_level INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS new_converts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, age INTEGER, contact TEXT,
        address TEXT, assigned_cell TEXT, decision_type TEXT, conversion_date TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS members_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, age INTEGER, contact TEXT,
        cell TEXT, sex TEXT, discipleship_type TEXT, other_church TEXT, ingreso_date TEXT,
        ministry TEXT, status TEXT DEFAULT 'activo'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT UNIQUE, leader TEXT
    )''')
    # Tabla de líderes
    c.execute('''CREATE TABLE IF NOT EXISTS leaders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT
    )''')
    conn.commit()
    conn.close()

def obtener_nombres_celulas():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT cell_name FROM cells")
    filas = c.fetchall()
    conn.close()
    lista_celulas = [f[0] for f in filas]
    if not lista_celulas:
        lista_celulas = ["Célula Central", "Célula de Jóvenes", "Célula de Damas"]
    return lista_celulas

init_db()

# --- LOGIN Y REGISTRO ---
st.sidebar.subheader("🔑 Ingreso de Líder")
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM leaders WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success(f"Bienvenido líder {username}")
        else:
            st.error("Usuario o contraseña incorrectos")

    # 🔐 Registrar líder disponible ANTES de login
    st.subheader("Registrar Nuevo Líder")
    with st.form("form_registro_lider", clear_on_submit=True):
        new_user = st.text_input("Nuevo Usuario")
        new_pass = st.text_input("Nueva Contraseña", type="password")
        if st.form_submit_button("Crear Cuenta"):
            if new_user.strip() and new_pass.strip():
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO leaders (username, password) VALUES (?, ?)", (new_user.strip(), new_pass.strip()))
                    conn.commit()
                    st.success(f"¡Cuenta creada para '{new_user}'! Ahora puedes iniciar sesión.")
                except sqlite3.IntegrityError:
                    st.error("Ese usuario ya existe.")
                conn.close()
            else:
                st.error("Usuario y contraseña no pueden estar vacíos.")

else:
    st.sidebar.success(f"Conectado como {st.session_state['username']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state['logged_in'] = False

    # --- Bloque de administración en la barra lateral ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Administración")

    if st.sidebar.button("Registrar Nueva Célula"):
        st.subheader("Registrar Nueva Célula")
        with st.form("form_registro_celula", clear_on_submit=True):
            cell_name = st.text_input("Nombre de la Célula")
            leader = st.text_input("Nombre del Líder")
            if st.form_submit_button("Guardar Célula"):
                if cell_name.strip():
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    try:
                        c.execute("INSERT INTO cells (cell_name, leader) VALUES (?, ?)", (cell_name.strip(), leader))
                        conn.commit()
                        st.success(f"¡Célula '{cell_name}' registrada exitosamente!")
                    except sqlite3.IntegrityError:
                        st.error("Ya existe una célula con ese nombre.")
                    conn.close()
                else:
                    st.error("El nombre de la célula no puede estar vacío.")

    if st.sidebar.button("Registrar Nuevo Líder"):
        st.subheader("Registrar Nuevo Líder")
        with st.form("form_registro_lider_admin", clear_on_submit=True):
            username = st.text_input("Usuario del Líder")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Guardar Líder"):
                if username.strip() and password.strip():
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    try:
                        c.execute("INSERT INTO leaders (username, password) VALUES (?, ?)", (username.strip(), password.strip()))
                        conn.commit()
                        st.success(f"¡Líder '{username}' registrado exitosamente!")
                    except sqlite3.IntegrityError:
                        st.error("Ya existe un líder con ese usuario.")
                    conn.close()
                else:
                    st.error("Usuario y contraseña no pueden estar vacíos.")
                    
# --- CONTENIDO SOLO SI ESTÁ LOGUEADO ---
if st.session_state['logged_in']:
    st.set_page_config(page_title="Gestión de Iglesia", layout="wide")
    st.title("⛪ Sistema de Gestión de Células y Miembros")

    # Menú principal
    menu = st.selectbox(
        "Selecciona una sección",
        [
            "👥 Registro de Miembros por Célula",
            "📝 Registro de Nuevos Convertidos",
            "📋 Reportes de Cultos de Célula",
            "📊 Panel de Control y Reportes",
            "🚨 Registro de Descarriados"
        ]
    )

    # ================= REGISTRO DE MIEMBROS POR CÉLULA =================
    if menu == "👥 Registro de Miembros por Célula":
        st.subheader("Registrar Miembros en una Célula")
        lista_celulas = obtener_nombres_celulas()
        with st.form("form_miembros_celula", clear_on_submit=True):
            full_name = st.text_input("Nombre Completo")
            age = st.number_input("Edad", min_value=1, max_value=120)
            phone = st.text_input("Teléfono")
            cell = st.selectbox("Célula", lista_celulas)
            sex = st.selectbox("Sexo", ["Masculino", "Femenino"])
            discipulado = st.radio("¿Está siendo discipulado?", ["Sí", "No"])
            otra_iglesia = st.radio("¿Vino de otra iglesia?", ["Sí", "No"])
            fecha_ingreso = st.date_input("Fecha de Ingreso")
            ministry = st.selectbox("Ministerio", ["Alabanza", "Ujieres", "Niños", "Intercesión", "Media", "Ninguno"])

            if st.form_submit_button("Guardar Miembro"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO members_stats 
                    (full_name, age, contact, cell, sex, discipleship_type, other_church, ingreso_date, ministry, status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (full_name, age, phone, cell, sex, discipulado, otra_iglesia, fecha_ingreso, ministry, "activo"))
                conn.commit()
                conn.close()
                st.success(f"¡Miembro '{full_name}' registrado en la célula '{cell}'!")

    # ================= REGISTRO DE NUEVOS CONVERTIDOS =================
    elif menu == "📝 Registro de Nuevos Convertidos":
        st.subheader("Registrar Nuevos Convertidos")
        lista_celulas = obtener_nombres_celulas()
        with st.form("form_convertidos", clear_on_submit=True):
            full_name = st.text_input("Nombres y Apellidos")
            age = st.number_input("Edad", min_value=1, max_value=120)
            phone = st.text_input("Teléfono")
            address = st.text_input("Dirección")
            assigned_cell = st.selectbox("Célula Asignada", lista_celulas)
            decision_type = st.radio("Tipo de Decisión", ["Acepto", "Reconciliación"])
            conversion_date = st.date_input("Fecha de la Decisión")

            if st.form_submit_button("Guardar Convertido"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO new_converts 
                    (full_name, age, contact, address, assigned_cell, decision_type, conversion_date) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (full_name, age, phone, address, assigned_cell, decision_type, conversion_date))
                conn.commit()
                conn.close()
                st.success(f"¡Nuevo convertido '{full_name}' registrado en la célula '{assigned_cell}'!")

    # ================= REPORTES DE CULTOS DE CÉLULA =================
    elif menu == "📋 Reportes de Cultos de Célula":
        st.subheader("Registrar Reporte de Culto de Célula")
        lista_celulas = obtener_nombres_celulas()
        opciones_celulas = lista_celulas + ["➕ Registrar Nueva Célula"]

        with st.form("form_celula", clear_on_submit=True):
            celula_seleccionada = st.selectbox("Selecciona el Nombre de la Célula", opciones_celulas)
            nombre_nueva_celula = st.text_input("Si seleccionaste 'Registrar Nueva Célula', escribe su nombre aquí:")
            meeting_date = st.date_input("Fecha de Reunión")
            
            col1, col2, col3 = st.columns(3)
            adults = col1.number_input("Adultos", min_value=0, step=1)
            youth = col2.number_input("Jóvenes", min_value=0, step=1)
            children = col3.number_input("Niños", min_value=0, step=1)
            friends = col1.number_input("Amigos", min_value=0, step=1)
            visits = col2.number_input("Visitas", min_value=0, step=1)

            house_leader = st.text_input("Líder de Casa")
            biblical_theme = st.text_input("Tema Bíblico")
            central_text = st.text_input("Texto Central")
            offering = st.number_input("Ofrenda", min_value=0.0, step=1.0)
            needs = st.text_area("Necesidades")
            spiritual_level = st.selectbox("Nivel Espiritual", ["Bajo", "Medio", "Alto"])
            attendance_level = st.slider("Nivel de Asistencia", 1, 10, 5)
            
            if st.form_submit_button("Guardar Reporte"):
                if celula_seleccionada == "➕ Registrar Nueva Célula":
                    cell_name_final = nombre_nueva_celula.strip()
                else:
                    cell_name_final = celula_seleccionada

                if not cell_name_final:
                    st.error("Por favor, introduce un nombre válido para la célula.")
                else:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute('''INSERT INTO cell_reports 
                        (cell_name, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (cell_name_final, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level))
                    conn.commit()
                    conn.close()
                    st.success(f"¡Reporte de la célula '{cell_name_final}' guardado exitosamente!")

    # ================= PANEL DE CONTROL =================
    elif menu == "📊 Panel de Control y Reportes":
        st.subheader("📊 Panel de Análisis Automático de la Iglesia")
        conn = sqlite3.connect(DB_PATH)
        df_cell = pd.read_sql_query("SELECT * FROM cell_reports", conn)
        df_converts = pd.read_sql_query("SELECT * FROM new_converts", conn)
        df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)

        # Verificar si existe la tabla de descarriados
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='descarriados'")
        if c.fetchone():
            df_descarriados = pd.read_sql_query("SELECT * FROM descarriados", conn)
        else:
            df_descarriados = pd.DataFrame()
        conn.close()

        hoy = datetime.date.today()
        mes_actual = hoy.month
        anio_actual = hoy.year

        # --- KPIs básicos ---
        # --- Gráfica de crecimiento por célula ---
        st.markdown("### 📈 Crecimiento de las Células (Miembros, Convertidos y Asistencia)")
        if not df_members.empty or not df_converts.empty or not df_cell_mes.empty:
            # Miembros por célula
            miembros_por_celula = df_members.groupby("cell")["full_name"].count().reset_index()
            miembros_por_celula.rename(columns={"full_name": "Miembros"}, inplace=True)

            # Convertidos por célula
            convertidos_por_celula = df_converts.groupby("assigned_cell")["full_name"].count().reset_index()
            convertidos_por_celula.rename(columns={"full_name": "Convertidos"}, inplace=True)

            # Asistencia por célula (adultos, jóvenes, niños, amigos)
            asistencia_por_celula = df_cell_mes.groupby("cell_name")[["adults","youth","children","friends"]].sum().reset_index()

            # Unir todo en un solo DataFrame
            crecimiento = pd.merge(miembros_por_celula, convertidos_por_celula,
                                   left_on="cell", right_on="assigned_cell", how="outer").fillna(0)
            crecimiento["Célula"] = crecimiento["cell"].combine_first(crecimiento["assigned_cell"])
            crecimiento = pd.merge(crecimiento, asistencia_por_celula, left_on="Célula", right_on="cell_name", how="outer").fillna(0)

            # Seleccionar columnas relevantes y renombrar
            crecimiento = crecimiento[["Célula","Miembros","Convertidos","adults","youth","children","friends"]]
            crecimiento.rename(columns={"adults":"Adultos","youth":"Jóvenes","children":"Niños","friends":"Amigos"}, inplace=True)

            # Mostrar tabla y gráfico
            st.dataframe(crecimiento)
            st.bar_chart(crecimiento.set_index("Célula"))
        else:
            st.info("Aún no hay datos suficientes para mostrar la gráfica de crecimiento.")
        
        if not df_cell.empty and 'meeting_date' in df_cell.columns:
            df_cell['meeting_date'] = pd.to_datetime(df_cell['meeting_date'], errors='coerce')
            df_cell_mes = df_cell[(df_cell['meeting_date'].dt.month == mes_actual) & (df_cell['meeting_date'].dt.year == anio_actual)]
        else:
            df_cell_mes = pd.DataFrame()

        if not df_converts.empty and 'conversion_date' in df_converts.columns:
            df_converts['conversion_date'] = pd.to_datetime(df_converts['conversion_date'], errors='coerce')
            df_converts_mes = df_converts[(df_converts['conversion_date'].dt.month == mes_actual) & (df_converts['conversion_date'].dt.year == anio_actual)]
        else:
            df_converts_mes = pd.DataFrame()

        if not df_members.empty and 'discipleship_type' in df_members.columns:
            discipulado_mes = df_members[df_members['discipleship_type'] == "Sí"]
        else:
            discipulado_mes = pd.DataFrame()

        total_ofrenda_mes = df_cell_mes['offering'].sum() if not df_cell_mes.empty else 0.0
        total_convertidos_mes = len(df_converts_mes) if not df_converts_mes.empty else 0
        total_discipulado_mes = len(discipulado_mes) if not discipulado_mes.empty else 0
        total_amigos = df_cell_mes['friends'].sum() if not df_cell_mes.empty else 0
        total_ninos = df_cell_mes['children'].sum() if not df_cell_mes.empty else 0
        total_jovenes = df_cell_mes['youth'].sum() if not df_cell_mes.empty else 0
        total_adultos = df_cell_mes['adults'].sum() if not df_cell_mes.empty else 0
        total_descarriados = len(df_descarriados) if not df_descarriados.empty else 0

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1: st.metric("Ofrenda del Mes", f"${total_ofrenda_mes:,.2f}")
        with kpi2: st.metric("Convertidos del Mes", f"{total_convertidos_mes} personas")
        with kpi3: st.metric("En Discipulado", f"{total_discipulado_mes} personas")
        with kpi4: st.metric("Asistencia del Mes", f"{total_adultos + total_jovenes + total_ninos} asistencias")

        kpi5, kpi6, kpi7, kpi8 = st.columns(4)
        with kpi5: st.metric("Total Amigos", f"{total_amigos}")
        with kpi6: st.metric("Total Niños", f"{total_ninos}")
        with kpi7: st.metric("Total Jóvenes", f"{total_jovenes}")
        with kpi8: st.metric("Total Adultos", f"{total_adultos}")

        # --- Clasificación por edad y sexo ---
        def clasificar_edad(edad):
            if edad <= 12: return "Niños"
            elif edad <= 17: return "Adolescentes"
            elif edad <= 30: return "Jóvenes"
            elif edad <= 60: return "Adultos"
            else: return "Tercera Edad"

        if not df_members.empty:
            df_members["grupo_edad"] = df_members["age"].apply(clasificar_edad)
            estadisticas = df_members.groupby(["grupo_edad","sex"])["full_name"].count().reset_index()
            st.markdown("### 📈 Distribución por Edad y Sexo")
            st.dataframe(estadisticas)

            # Estado espiritual
            if "discipleship_type" in df_members.columns:
                espirituales = df_members.groupby("discipleship_type")["full_name"].count().reset_index()
                st.markdown("### ✝️ Estado Espiritual (Bautizado / Catecúmeno)")
                st.dataframe(espirituales)

        # --- Descarriados ---
        st.metric("Miembros Descarriados", f"{total_descarriados}")
        if not df_descarriados.empty:
            st.markdown("### 🚨 Lista de Descarriados")
            st.dataframe(df_descarriados)



        # --- Tablas detalladas ---
        st.markdown("### 📌 Reportes de Células")
        st.dataframe(df_cell)

        st.markdown("### 👤 Nuevos Convertidos")
        st.dataframe(df_converts)

        st.markdown("### 📖 Miembros en Discipulado")
        st.dataframe(df_members[df_members['discipleship_type']=="Sí"])

        if not df_descarriados.empty:
            st.markdown("### 🚨 Lista de Descarriados")
            st.dataframe(df_descarriados)
    # ================= REGISTRO DE DESCARRIADOS =================
    elif menu == "🚨 Registro de Descarriados":
        st.subheader("Registrar Miembro Descarriado")
        lista_celulas = obtener_nombres_celulas()
        with st.form("form_descarriados", clear_on_submit=True):
            full_name = st.text_input("Nombre Completo")
            cell = st.selectbox("Célula", lista_celulas)
            fecha_desercion = st.date_input("Fecha de Deserción")
            motivo = st.text_area("Motivo de Deserción (opcional)")

            if st.form_submit_button("Guardar Descarriado"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS descarriados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    full_name TEXT, 
                    cell TEXT, 
                    fecha_desercion TEXT, 
                    motivo TEXT
                )''')
                c.execute("INSERT INTO descarriados (full_name, cell, fecha_desercion, motivo) VALUES (?, ?, ?, ?)",
                          (full_name, cell, fecha_desercion, motivo))
                c.execute("UPDATE members_stats SET status='desertado' WHERE full_name=? AND cell=?", (full_name, cell))
                conn.commit()
                conn.close()
                st.success(f"¡Miembro '{full_name}' marcado como descarriado en la célula '{cell}'!")
    # ================= PANEL DE CONTROL =================
    elif menu == "📊 Panel de Control y Reportes":
        st.subheader("📊 Panel de Análisis Automático de la Iglesia")
        conn = sqlite3.connect(DB_PATH)
        df_cell = pd.read_sql_query("SELECT * FROM cell_reports", conn)
        df_converts = pd.read_sql_query("SELECT * FROM new_converts", conn)
        df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)

        # Verificar si existe la tabla de descarriados
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='descarriados'")
        if c.fetchone():
            df_descarriados = pd.read_sql_query("SELECT * FROM descarriados", conn)
        else:
            df_descarriados = pd.DataFrame()
        conn.close()

        hoy = datetime.date.today()
        mes_actual = hoy.month
        anio_actual = hoy.year

        # --- KPIs básicos ---
        if not df_cell.empty and 'meeting_date' in df_cell.columns:
            df_cell['meeting_date'] = pd.to_datetime(df_cell['meeting_date'], errors='coerce')
            df_cell_mes = df_cell[(df_cell['meeting_date'].dt.month == mes_actual) & (df_cell['meeting_date'].dt.year == anio_actual)]
        else:
            df_cell_mes = pd.DataFrame()

        if not df_converts.empty and 'conversion_date' in df_converts.columns:
            df_converts['conversion_date'] = pd.to_datetime(df_converts['conversion_date'], errors='coerce')
            df_converts_mes = df_converts[(df_converts['conversion_date'].dt.month == mes_actual) & (df_converts['conversion_date'].dt.year == anio_actual)]
        else:
            df_converts_mes = pd.DataFrame()

        if not df_members.empty and 'discipleship_type' in df_members.columns:
            discipulado_mes = df_members[df_members['discipleship_type'] == "Sí"]
        else:
            discipulado_mes = pd.DataFrame()

        total_ofrenda_mes = df_cell_mes['offering'].sum() if not df_cell_mes.empty else 0.0
        total_convertidos_mes = len(df_converts_mes) if not df_converts_mes.empty else 0
        total_discipulado_mes = len(discipulado_mes) if not discipulado_mes.empty else 0
        total_amigos = df_cell_mes['friends'].sum() if not df_cell_mes.empty else 0
        total_ninos = df_cell_mes['children'].sum() if not df_cell_mes.empty else 0
        total_jovenes = df_cell_mes['youth'].sum() if not df_cell_mes.empty else 0
        total_adultos = df_cell_mes['adults'].sum() if not df_cell_mes.empty else 0
        total_descarriados = len(df_descarriados) if not df_descarriados.empty else 0

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1: st.metric("Ofrenda del Mes", f"${total_ofrenda_mes:,.2f}")
        with kpi2: st.metric("Convertidos del Mes", f"{total_convertidos_mes} personas")
        with kpi3: st.metric("En Discipulado", f"{total_discipulado_mes} personas")
        with kpi4: st.metric("Asistencia del Mes", f"{total_adultos + total_jovenes + total_ninos} asistencias")

        kpi5, kpi6, kpi7, kpi8 = st.columns(4)
        with kpi5: st.metric("Total Amigos", f"{total_amigos}")
        with kpi6: st.metric("Total Niños", f"{total_ninos}")
        with kpi7: st.metric("Total Jóvenes", f"{total_jovenes}")
        with kpi8: st.metric("Total Adultos", f"{total_adultos}")

        # --- Clasificación por edad y sexo ---
        def clasificar_edad(edad):
            if edad <= 12: return "Niños"
            elif edad <= 17: return "Adolescentes"
            elif edad <= 30: return "Jóvenes"
            elif edad <= 60: return "Adultos"
            else: return "Tercera Edad"

        if not df_members.empty:
            df_members["grupo_edad"] = df_members["age"].apply(clasificar_edad)
            estadisticas = df_members.groupby(["grupo_edad","sex"])["full_name"].count().reset_index()
            st.markdown("### 📈 Distribución por Edad y Sexo")
            st.dataframe(estadisticas)

            # Estado espiritual
            if "discipleship_type" in df_members.columns:
                espirituales = df_members.groupby("discipleship_type")["full_name"].count().reset_index()
                st.markdown("### ✝️ Estado Espiritual (Bautizado / Catecúmeno)")
                st.dataframe(espirituales)

        # --- Descarriados ---
        st.metric("Miembros Descarriados", f"{total_descarriados}")
        if not df_descarriados.empty:
            st.markdown("### 🚨 Lista de Descarriados")
            st.dataframe(df_descarriados)
            


