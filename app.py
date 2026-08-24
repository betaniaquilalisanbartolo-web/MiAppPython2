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
                st.success(f"Bienvenido {username}")
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
    st.info(f"Ya has iniciado sesión como {st.session_state['username']}")
    if st.button("Cerrar sesión"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""

    # --- Pestañas principales ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👤 Miembros",
        "🙌 Convertidos",
        "📌 Reportes",
        "🚨 Descarriados",
        "⚙️ Administración",
        "📊 Panel"
    ])

    # --- Miembros ---
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

    # --- Convertidos ---
    with tab2:
        st.subheader("Registro de Convertidos")
        conn = sqlite3.connect(DB_PATH)
        cells = pd.read_sql_query("SELECT cell_name FROM cells", conn)
        conn.close()
        cell_options = cells['cell_name'].tolist() if not cells.empty else []
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

    # --- Reportes ---
    with tab3:
        st.subheader("Registro de Reportes de Células")
        conn = sqlite3.connect(DB_PATH)
        cells = pd.read_sql_query("SELECT cell_name FROM cells", conn)
        conn.close()
        cell_options = cells['cell_name'].tolist() if not cells.empty else []
        with st.form("registro_reporte"):
            cell_name = st.selectbox("Célula", cell_options)
            meeting_date = st.date_input("Fecha de reunión")
            adults = st.number_input("Adultos", min_value=0)
            youth = st.number_input("Jóvenes", min_value=0)
            children = st.number_input("Niños", min_value=0)
            friends = st.number_input("Amigos", min_value=0)
            visits = st.number_input("Visitas", min_value=0)
            house_leader = st.text_input("Líder de casa")
            biblical_theme = st.text_input("Tema bíblico")
            central_text = st.text_input("Texto central")
            offering = st.number_input("Ofrenda", min_value=0.0)
            needs = st.text_area("Necesidades")
            spiritual_level = st.selectbox("Nivel espiritual", ["Alto", "Medio", "Bajo"])
            attendance_level = adults + youth + children + friends
            submit = st.form_submit_button("Registrar Reporte")
            if submit and cell_name:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""INSERT INTO cell_reports 
                    (cell_name, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (cell_name, meeting_date.strftime("%Y-%m-%d"), adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level))
                conn.commit()
                conn.close()
                st
    # --- Descarriados ---
    with tab4:
        st.subheader("Registro de Descarriados")
        conn = sqlite3.connect(DB_PATH)
        cells = pd.read_sql_query("SELECT cell_name FROM cells", conn)
        conn.close()
        cell_options = cells['cell_name'].tolist() if not cells.empty else []
        with st.form("registro_descarriado"):
            full_name = st.text_input("Nombre completo")
            age = st.number_input("Edad", min_value=0, max_value=120)
            contact = st.text_input("Contacto")
            cell = st.selectbox("Célula", cell_options)
            reason = st.text_area("Razón de descarriado")
            date_reported = st.date_input("Fecha de reporte")
            submit = st.form_submit_button("Registrar Descarriado")
            if submit and full_name:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""INSERT INTO descarriados 
                    (full_name, age, contact, cell, reason, date_reported)
                    VALUES (?,?,?,?,?,?)""",
                    (full_name, age, contact, cell, reason, date_reported.strftime("%Y-%m-%d")))
                conn.commit()
                conn.close()
                st.success(f"Descarriado {full_name} registrado en la célula {cell}")
    # --- Administración ---
    with tab5:
      st.subheader("⚙️ Administración")

      st.markdown("### 🌱 Registrar nueva célula y líder")
      cell_name = st.text_input("Nombre de la célula")
      leader = st.text_input("Nombre del líder")
    if st.button("Registrar célula"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO cells (cell_name, leader) VALUES (?,?)", (cell_name, leader))
            conn.commit()
            st.success(f"Célula '{cell_name}' registrada con líder {leader}")
        except sqlite3.IntegrityError:
            st.error("Esa célula ya existe")
        conn.close()

    # Botón para reiniciar datos
    if st.button("🗑️ Reiniciar datos"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM members_stats")
        c.execute("DELETE FROM new_converts")
        c.execute("DELETE FROM cell_reports")
        c.execute("DELETE FROM descarriados")
        conn.commit()
        conn.close()
        st.success("Todos los datos fueron eliminados. Ahora las tablas están vacías.")

# --- Panel ---
with tab6:
    st.subheader("📊 Panel de Control y Gráficas")

    # Conexión y carga de datos
    conn = sqlite3.connect(DB_PATH)
    df_conv = pd.read_sql_query("SELECT * FROM new_converts", conn)
    df_reports = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)
    df_descarriados = pd.read_sql_query("SELECT * FROM descarriados", conn)
    conn.close()

    # KPIs
    st.markdown("### 📈 Indicadores Clave del Sistema")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        total_ofrenda = df_reports['offering'].sum() if not df_reports.empty else 0.0
        st.metric("Total Ofrendas", f"${total_ofrenda:,.2f}")
    with kpi2:
        total_nuevos = len(df_conv) if not df_conv.empty else 0
        st.metric("Nuevos Convertidos", f"{total_nuevos} personas")
    with kpi3:
        miembros_activos = len(df_members[df_members['status'] == 'activo']) if not df_members.empty else 0
        st.metric("Miembros Activos", f"{miembros_activos} personas")
    with kpi4:
        total_asistencia = df_reports['attendance_level'].sum() if not df_reports.empty else 0
        st.metric("Impacto Total Asistencia", f"{total_asistencia} asistencias")

    st.markdown("---")

    # Convertidos por mes
    if not df_conv.empty:
        df_conv['conversion_date'] = pd.to_datetime(df_conv['conversion_date'], errors='coerce')
        conv_mes = df_conv.groupby(df_conv['conversion_date'].dt.to_period("M")).size()
        st.line_chart(conv_mes)

    # Reportes
    if not df_reports.empty:
        df_reports['meeting_date'] = pd.to_datetime(df_reports['meeting_date'], errors='coerce')
        amigos_mes = df_reports.groupby(df_reports['meeting_date'].dt.to_period("M"))['friends'].sum()
        st.bar_chart(amigos_mes)

        crecimiento = df_reports.groupby('cell_name')['attendance_level'].sum()
        st.bar_chart(crecimiento)

    # Crecimiento y deserciones
    if not df_members.empty or not df_descarriados.empty:
        st.markdown("### 👥 Crecimiento y Deserciones")
        df_members['ingreso_date'] = pd.to_datetime(df_members['ingreso_date'], errors='coerce')
        df_descarriados['date_reported'] = pd.to_datetime(df_descarriados['date_reported'], errors='coerce')
        miembros_mes = df_members.groupby(df_members['ingreso_date'].dt.to_period("M")).size()
        deserciones_mes = df_descarriados.groupby(df_descarriados['date_reported'].dt.to_period("M")).size()
        grafico_crecimiento = pd.DataFrame({
            "Miembros Activos": miembros_mes,
            "Deserciones": deserciones_mes
        }).fillna(0)
        st.line_chart(grafico_crecimiento)

    # Amigos alcanzados
    if not df_reports.empty:
        st.markdown("### 🤝 Amigos Alcanzados por Mes")
        amigos_mes = df_reports.groupby(df_reports['meeting_date'].dt.to_period("M"))['friends'].sum()
        st.area_chart(amigos_mes)

    # Asistencia y ofrendas
    if not df_reports.empty:
        st.markdown("### 📊 Gráficos de Células y Finanzas")
        grafico1, grafico2 = st.columns(2)
        with grafico1:
            st.write("🏃♂️ *Asistencia Acumulada por Categoría*")
            data_asistencia = {
                'Categoría': ['Adultos', 'Jóvenes', 'Niños', 'Amigos', 'Visitas'],
                'Cantidad': [
                    df_reports['adults'].sum(), df_reports['youth'].sum(),
                    df_reports['children'].sum(), df_reports['friends'].sum(),
                    df_reports['visits'].sum()
                ]
            }
            st.bar_chart(pd.DataFrame(data_asistencia), x='Categoría', y='Cantidad')
        with grafico2:
            st.write("💰 *Ofrendas por Célula*")
            ofrendas_por_celula = df_reports.groupby('cell_name')['offering'].sum()
            st.bar_chart(ofrendas_por_celula)
