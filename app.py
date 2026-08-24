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

    # Tabla de cuentas
    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")

    # Tabla de células
    c.execute("""CREATE TABLE IF NOT EXISTS cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cell_name TEXT UNIQUE,
        leader TEXT
    )""")

    # Tabla de miembros
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

    # Tabla de convertidos
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

    # Tabla de reportes
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

    # Tabla de descarriados
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

# --- Menú principal ---
menu = st.sidebar.selectbox("Menú", [
    "🏠 Inicio (Login)",
    "👤 Registro de Miembros",
    "🙌 Registro de Convertidos",
    "📌 Reportes de Células",
    "🚨 Registro de Descarriados",
    "📊 Panel de Control y Reportes",
    "⚙️ Administración"
])

# --- Inicio/Login ---
if menu == "🏠 Inicio (Login)":
    st.subheader("🔑 Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM accounts WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            st.success(f"Bienvenido {username}")
        else:
            st.error("Usuario o contraseña incorrectos")

# --- Administración ---
elif menu == "⚙️ Administración":
    st.subheader("⚙️ Panel de Administración")

    # Registrar nueva cuenta
    st.markdown("### 🆕 Registrar nueva cuenta")
    new_user = st.text_input("Nuevo usuario")
    new_pass = st.text_input("Nueva contraseña", type="password")
    if st.button("Registrar cuenta"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO accounts (username, password) VALUES (?,?)", (new_user, new_pass))
            conn.commit()
            st.success(f"Cuenta '{new_user}' creada correctamente")
        except sqlite3.IntegrityError:
            st.error("Ese usuario ya existe")
        conn.close()

    # Registrar nueva célula
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

# --- Registro de Miembros ---
elif menu == "👤 Registro de Miembros":
    st.subheader("Registro de Miembros")
    # (pega aquí el bloque de formulario de miembros que ya te pasé)

# --- Registro de Convertidos ---
elif menu == "🙌 Registro de Convertidos":
    st.subheader("Registro de Nuevos Convertidos")
    # (pega aquí el bloque de formulario de convertidos)

# --- Reportes de Células ---
elif menu == "📌 Reportes de Células":
    st.subheader("Registro de Reportes de Células")
    # (pega aquí el bloque de formulario de reportes)

# --- Registro de Descarriados ---
elif menu == "🚨 Registro de Descarriados":
    st.subheader("Registro de Descarriados")
    # (pega aquí el bloque de formulario de descarriados)

# --- Panel de Control ---
elif menu == "📊 Panel de Control y Reportes":
    st.subheader("📊 Panel de Análisis Automático de la Iglesia")

    conn = sqlite3.connect(DB_PATH)
    df_cell = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    df_converts = pd.read_sql_query("SELECT * FROM new_converts", conn)
    df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)
    df_descarriados = pd.read_sql_query("SELECT * FROM descarriados", conn)
    conn.close()

    # KPIs
    total_ofrenda = df_cell['offering'].sum() if not df_cell.empty else 0.0
    total_convertidos = len(df_converts) if not df_converts.empty else 0
    total_amigos = df_cell['friends'].sum() if not df_cell.empty else 0

    st.metric("💰 Ofrenda Total", f"${total_ofrenda:,.2f}")
    st.metric("🙌 Convertidos Totales", f"{total_convertidos}")
    st.metric("🤝 Amigos Evangelizados", f"{total_amigos}")

    # Gráfica de convertidos por mes
    if not df_converts.empty:
        df_converts['conversion_date'] = pd.to_datetime(df_converts['conversion_date'])
        converts_by_month = df_converts.groupby(df_converts['conversion_date'].dt.to_period("M")).size()
        st.markdown("### 📈 Nuevos Convertidos por Mes")
        st.bar_chart(converts_by_month)

    # Gráficas de amigos evangelizados
    if not df_cell.empty:
        df_cell['meeting_date'] = pd.to_datetime(df_cell['meeting_date'])
        friends_by_month = df_cell.groupby(df_cell['meeting_date'].dt.to_period("M"))['friends'].sum()
        friends_by_week = df_cell.groupby(df_cell['meeting_date'].dt.to_period("W"))['friends'].sum()
        st.markdown("### 🤝 Amigos Evangelizados por Mes")
        st.line_chart(friends_by_month)
        st.markdown("### 🤝 Amigos Evangelizados por Semana")
        st.line_chart(friends_by_week)

    # Gráfica de crecimiento por célula
    if not df_members.empty or not df_converts.empty or not df_cell.empty:
        miembros_por_celula = df_members.groupby("cell")["full_name"].count().reset_index()
        miembros_por_celula.rename(columns={"full_name": "Miembros"}, inplace=True)
        convertidos_por_celula = df_converts.groupby("assigned_cell")["full_name"].count().reset_index()
        convertidos_por_celula.rename(columns={"full_name": "Convertidos"}, inplace=True)
        asistencia_por_celula = df_cell.groupby("cell_name")[["adults","youth","children","friends"]].sum().reset_index()

        crecimiento = pd.merge(miembros_por_celula, convertidos_por_celula,
                               left_on="cell", right_on="assigned_cell", how="outer").fillna(0)
        crecimiento["Célula"] = crecimiento["cell"].combine_first(crecimiento["assigned_cell"])
        crecimiento = pd.merge(crecimiento, asistencia_por_celula, left_on="Célula", right_on="cell_name", how="outer").fillna(0)

        crecimiento = crecimiento[["Célula","Miembros","Convertidos","adults","youth","children","friends"]]
        crecimiento.rename(columns={"adults":"Adultos","youth":"Jóvenes","children":"Niños","friends":"Amigos"}, inplace=True)

        st.markdown("### 🌱 Crecimiento por Célula
