import streamlit as st
import sqlite3
import pandas as pd
import datetime

DB_PATH = "C:/Users/Pc/Desktop/MiAppPython/MiAppPython2/MiBaseDatos/database.db"

# --- Inicializar base de datos ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Crear tablas si no existen
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

# --- Menú principal ---
menu = st.sidebar.selectbox("Menú", ["🏠 Inicio", "👤 Registro de Miembros", "📊 Panel de Control y Reportes"])

# --- Inicio ---
if menu == "🏠 Inicio":
    st.subheader("Bienvenido al Sistema de Gestión de Iglesia")

# --- Registro de Miembros ---
elif menu == "👤 Registro de Miembros":
    st.subheader("Registro de Miembros")
    st.write("Aquí iría el formulario para registrar miembros.")

# --- Panel de Control ---
elif menu == "📊 Panel de Control y Reportes":
    st.subheader("📊 Panel de Análisis Automático de la Iglesia")

    conn = sqlite3.connect(DB_PATH)
    df_cell = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    df_converts = pd.read_sql_query("SELECT * FROM new_converts", conn)
    df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)
    df_descarriados = pd.read_sql_query("SELECT * FROM descarriados", conn)
    conn.close()

    # --- Gráfica de crecimiento por célula ---
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

        st.dataframe(crecimiento)
        st.bar_chart(crecimiento.set_index("Célula"))
    else:
        st.info("Aún no hay datos suficientes para mostrar la gráfica de crecimiento.")

    # --- KPIs ---
    total_ofrenda = df_cell['offering'].sum() if not df_cell.empty else 0.0
    total_convertidos = len(df_converts) if not df_converts.empty else 0
    total_discipulado = len(df_members[df_members['discipleship_type']=="Sí"]) if not df_members.empty else 0
    total_amigos = df_cell['friends'].sum() if not df_cell.empty else 0
    total_ninos = df_cell['children'].sum() if not df_cell.empty else 0
    total_jovenes = df_cell['youth'].sum() if not df_cell.empty else 0
    total_adultos = df_cell['adults'].sum() if not df_cell.empty else 0
    total_descarriados = len(df_descarriados) if not df_descarriados.empty else 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1: st.metric("Ofrenda Total", f"${total_ofrenda:,.2f}")
    with kpi2: st.metric("Convertidos Totales", f"{total_convertidos}")
    with kpi3: st.metric("En Discipulado", f"{total_discipulado}")
    with kpi4: st.metric("Asistencia Total", f"{total_adultos + total_jovenes + total_ninos}")

    kpi5, kpi6, kpi7, kpi8 = st.columns(4)
    with kpi5: st.metric("Total Amigos", f"{total_amigos}")
    with kpi6: st.metric("Total Niños", f"{total_ninos}")
    with kpi7: st.metric("Total Jóvenes", f"{total_jovenes}")
    with kpi8: st.metric("Total Adultos", f"{total_adultos}")

    st.metric("Miembros Descarriados", f"{total_descarriados}")
    if not df_descarriados.empty:
        st.markdown("### 🚨 Lista de Descarriados")
        st.dataframe(df_descarriados)

    # --- Nombres de miembros y convertidos ---
    if not df_members.empty:
        st.markdown("### 👥 Miembros por Célula")
        miembros_por_celula = df_members.groupby("cell")["full_name"].apply(list).reset_index()
        for _, fila in miembros_por_celula.iterrows():
            st.write(f"**{fila['cell']}**: {', '.join(fila['full_name'])}")

    if not df_converts.empty:
        st.markdown("### 🙌 Convertidos por Célula")
        convertidos_por_celula = df_converts.groupby("assigned_cell")["full_name"].apply(list).reset_index()
        for _, fila in convertidos_por_celula.iterrows():
            st.write(f"**{fila['assigned_cell']}**: {', '.join(fila['full_name'])}")

    # --- Tablas detalladas ---
    st.markdown("### 📌 Reportes de Células")
    st.dataframe(df_cell)

    st.markdown("### 👤 Nuevos Convertidos")
    st.dataframe(df_converts)

    st.markdown("### 📖 Miembros en Discipulado")
    st.dataframe(df_members[df_members['discipleship_type']=="Sí"])
