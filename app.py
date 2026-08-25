import streamlit as st
import sqlite3
import pandas as pd
import os

# --- Base de datos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tablas principales
    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cell_name TEXT UNIQUE,
        leader TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS members_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        age INTEGER,
        contact TEXT,
        cell TEXT,
        sex TEXT,
        discipleship_type TEXT,
        other_church TEXT,
        ingreso_date TEXT,
        ministry TEXT,
        status TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS new_converts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        age INTEGER,
        contact TEXT,
        address TEXT,
        assigned_cell TEXT,
        decision_type TEXT,
        conversion_date TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS cell_reports (
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
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS descarriados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        age INTEGER,
        contact TEXT,
        cell TEXT,
        reason TEXT,
        date_reported TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS new_converts_dropped (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        drop_date TEXT,
        reason TEXT,
        important_notes TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

# --- Estado de sesión ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

# --- Inicio/Login y Registro ---
if not st.session_state["logged_in"]:
    tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "🆕 Registrar Cuenta"])

    with tab_login:
        st.subheader("Iniciar Sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT * FROM accounts WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            conn.close()
            if user:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with tab_register:
        st.subheader("Registrar nueva cuenta")
        new_user = st.text_input("Nuevo usuario")
        new_pass = st.text_input("Nueva contraseña", type="password")
        if st.button("Registrar"):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO accounts (username, password) VALUES (?,?)", (new_user, new_pass))
                conn.commit()
                st.success(f"Cuenta '{new_user}' creada correctamente")
            except sqlite3.IntegrityError:
                st.error("Ese usuario ya existe")
            conn.close()

else:
    # --- MENÚ DE USUARIO AUTENTICADO ---
    st.sidebar.info(f"Sesión activa: {st.session_state['username']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()

    # --- Pestañas principales ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👤 Miembros",
        "🙌 Convertidos",
        "📌 Reportes",
        "🚨 Descarriados",
        "⚙️ Administración",
        "📊 Panel"
    ])

    # --- 1. Miembros ---
    with tab1:
        st.subheader("Registro de Miembros")
        conn = sqlite3.connect(DB_PATH)
        cells = pd.read_sql_query("SELECT cell_name FROM cells", conn)
        conn.close()
        cell_options = cells['cell_name'].tolist() if not cells.empty else []
        
        with st.form("registro_miembro"):
            full_name = st.text_input("Nombre completo")
            age = st.number_input("Edad", min_value=0, max_value=120)
            contact = st.text_input("Contacto")
            cell = st.selectbox("Célula", cell_options)
            sex = st.selectbox("Sexo", ["Masculino", "Femenino"])
            discipleship_type = st.selectbox("¿En discipulado?", ["Sí", "No"])
            other_church = st.selectbox("¿Viene de otra iglesia?", ["Sí", "No"])
            ingreso_date = st.date_input("Fecha de ingreso")
            ministry = st.text_input("Ministerio")
            status = st.selectbox("Estado", ["activo", "inactivo"])
            submit = st.form_submit_button("Registrar Miembro")
            
            if submit and full_name:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""INSERT INTO members_stats 
                    (full_name, age, contact, cell, sex, discipleship_type, other_church, ingreso_date, ministry, status)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (full_name, age, contact, cell, sex, discipleship_type, other_church, ingreso_date.strftime("%Y-%m-%d"), ministry, status))
                conn.commit()
                conn.close()
                st.success(f"Miembro {full_name} registrado en la célula {cell}")

    # --- 2. Convertidos ---
    with tab2:
        st.subheader("Registro de Convertidos")
        conn = sqlite3.connect(DB_PATH)
        cells = pd.read_sql_query("SELECT cell_name FROM cells", conn)
        converts_query = pd.read_sql_query("SELECT full_name FROM new_converts", conn)
        conn.close()
        
        cell_options = cells['cell_name'].tolist() if not cells.empty else []
        convert_names = converts_query['full_name'].tolist() if not converts_query.empty else []
        
        sub_tab_alta, sub_tab_baja = st.tabs(["➕ Registrar Alta", "🚨 Reportar Deserción o Abandono"])
        
        with sub_tab_alta:
            with st.form("registro_convertido"):
                full_name = st.text_input("Nombre completo")
                age = st.number_input("Edad", min_value=0, max_value=120)
                contact = st.text_input("Contacto")
                address = st.text_input("Dirección")
                assigned_cell = st.selectbox("Célula asignada", cell_options)
                decision_type = st.selectbox("Decisión", ["Aceptó a Cristo", "Reconciliación"])
                conversion_date = st.date_input("Fecha de conversión")
                submit = st.form_submit_button("Registrar Convertido")
                
                if submit and full_name:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("""INSERT INTO new_converts 
                        (full_name, age, contact, address, assigned_cell, decision_type, conversion_date)
                        VALUES (?,?,?,?,?,?,?)""",
                        (full_name, age, contact, address, assigned_cell, decision_type, conversion_date.strftime("%Y-%m-%d")))
                    conn.commit()
                    conn.close()
                    st.success(f"Convertido {full_name} registrado en la célula {assigned_cell}")
                    st.rerun()

        with sub_tab_baja:
            st.markdown("**Utiliza este espacio si un nuevo convertido dejó de asistir para mantener un control de los motivos.**")
            if convert_names:
                with st.form("registro_desercion_convertido"):
                    selected_convert = st.selectbox("Seleccione el Nuevo Convertido", convert_names)
                    drop_date = st.date_input("Fecha en que se desertó / distanció")
                    drop_reason = st.selectbox("Motivo principal", ["Falta de tiempo", "Problemas familiares", "Regresó al mundo", "Cambio de domicilio", "Desinterés", "Otro"])
                    important_notes = st.text_area("Datos importantes / Notas de seguimiento pastoral")
                    submit_drop = st.form_submit_button("💾 Guardar Historial de Deserción")
                    
                    if submit_drop:
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("""INSERT INTO new_converts_dropped (full_name, drop_date, reason, important_notes)
                                     VALUES (?, ?, ?, ?)""", 
                                  (selected_convert, drop_date.strftime("%Y-%m-%d"), drop_reason, important_notes))
                        conn.commit()
                        conn.close()
                        st.warning(f"Se ha registrado el abandono de {selected_convert} para evaluación consolidada.")
            else:
                st.info("No hay nuevos convertidos registrados en el sistema para procesar una baja.")
                
    # --- 3. Reportes ---
    with tab3:
        st.subheader("Registro de Reportes de Células")
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
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""INSERT INTO cell_reports 
                    (cell_name, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (cell_name, meeting_date.strftime("%Y-%m-%d"), adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level))
                conn.commit()
                conn.close()
                st.success("Reporte de célula guardado exitosamente.")

    
