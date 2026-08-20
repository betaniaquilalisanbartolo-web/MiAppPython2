import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
# Ahora la base de datos se creará directamente en la carpeta del proyecto
DB_PATH = "database.db"

def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Reportes de células
    c.execute('''CREATE TABLE IF NOT EXISTS cell_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, meeting_date TEXT,
        adults INTEGER, youth INTEGER, children INTEGER, friends INTEGER, visits INTEGER,
        house_leader TEXT, biblical_theme TEXT, central_text TEXT, offering REAL,
        needs TEXT, spiritual_level TEXT, attendance_level INTEGER
    )''')
    # Nuevos convertidos
    c.execute('''CREATE TABLE IF NOT EXISTS new_converts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, contact TEXT, address TEXT,
        birth_date TEXT, age INTEGER, status TEXT, conversion_date TEXT,
        decision_type TEXT, assigned_cell TEXT, observation TEXT
    )''')
    # Estadísticas de miembros
    c.execute('''CREATE TABLE IF NOT EXISTS members_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, cell TEXT, sex TEXT,
        growth_eval INTEGER, discipleship_type TEXT, ministry TEXT, status TEXT DEFAULT 'activo'
    )''')
    conn.commit()
    conn.close()

init_db()

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Gestión de Iglesia", layout="wide")
st.title("⛪ Sistema de Gestión de Células y Miembros")

# Menú de navegación lateral
menu = st.sidebar.selectbox("Selecciona una sección", ["📝 Formularios", "📊 Reportes y Gráficos"])

if menu == "📝 Formularios":
    pestana1, pestana2, pestana3 = st.tabs(["📌 Reporte de Célula", "👤 Nuevo Convertido", "📈 Miembro"])
    
    with pestana1:
        st.subheader("Registrar Reporte de Célula")
        with st.form("form_celula", clear_on_submit=True):
            cell_name = st.text_input("Nombre de la Célula")
            meeting_date = st.date_range_picker = st.text_input("Fecha de Reunión (AAAA-MM-DD)")
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
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO cell_reports (cell_name, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (cell_name, meeting_date, adults, youth, children, friends, visits, house_leader, biblical_theme, central_text, offering, needs, spiritual_level, attendance_level))
                conn.commit()
                conn.close()
                st.success("¡Reporte de célula guardado exitosamente!")

    with pestana2:
        st.subheader("Registrar Nuevo Convertido")
        with st.form("form_convertido", clear_on_submit=True):
            full_name = st.text_input("Nombre Completo")
            contact = st.text_input("Contacto / Teléfono")
            address = st.text_area("Dirección")
            birth_date = st.text_input("Fecha de Nacimiento (AAAA-MM-DD)")
            age = st.number_input("Edad", min_value=0, step=1)
            status = st.text_input("Estado", value="Nuevo")
            conversion_date = st.text_input("Fecha de Conversión (AAAA-MM-DD)")
            decision_type = st.text_input("Tipo de Decisión")
            assigned_cell = st.text_input("Célula Asignada")
            observation = st.text_area("Observaciones")
            
            if st.form_submit_button("Guardar Convertido"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO new_converts (full_name, contact, address, birth_date, age, status, conversion_date, decision_type, assigned_cell, observation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (full_name, contact, address, birth_date, age, status, conversion_date, decision_type, assigned_cell, observation))
                conn.commit()
                conn.close()
                st.success("¡Nuevo convertido guardado!")

    with pestana3:
        st.subheader("Estadísticas de Miembro")
        with st.form("form_miembro", clear_on_submit=True):
            full_name = st.text_input("Nombre Completo del Miembro")
            cell = st.text_input("Célula")
            sex = st.selectbox("Sexo", ["Masculino", "Femenino"])
            growth_eval = st.slider("Evaluación de Crecimiento", 1, 10, 5)
            discipleship_type = st.text_input("Tipo de Discipulado")
            ministry = st.text_input("Ministerio")
            
            if st.form_submit_button("Guardar Estadísticas"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO members_stats (full_name, cell, sex, growth_eval, discipleship_type, ministry) VALUES (?, ?, ?, ?, ?, ?)''',
                          (full_name, cell, sex, growth_eval, discipleship_type, ministry))
                conn.commit()
                conn.close()
                st.success("¡Estadísticas de miembro guardadas!")

elif menu == "📊 Reportes y Gráficos":
    st.subheader("Visualización de Datos")
    
    conn = sqlite3.connect(DB_PATH)
    df_cell = pd.read_sql_query("SELECT * FROM cell_reports", conn)
    df_converts = pd.read_sql_query("SELECT * FROM new_converts", conn)
    df_members = pd.read_sql_query("SELECT * FROM members_stats", conn)
    conn.close()

    # Filtros de búsqueda para Reportes de Célula
    st.markdown("### 🔍 Filtrar Reportes de Células")
    col_f1, col_f2 = st.columns(2)
    filtro_fecha = col_f1.text_input("Filtrar por fecha (AAAA-MM-DD)")
    filtro_celula = col_f2.text_input("Filtrar por nombre de célula")

    df_cell_filtrado = df_cell.copy()
    if filtro_fecha:
        df_cell_filtrado = df_cell_filtrado[df_cell_filtrado['meeting_date'] == filtro_fecha]
    if filtro_celula:
        df_cell_filtrado = df_cell_filtrado[df_cell_filtrado['cell_name'].str.contains(filtro_celula, case=False, na=False)]

    st.write("📋 **Reportes de Células**", df_cell_filtrado)
    
    # Botones de exportación en la barra lateral o debajo
    col_exp1, col_exp2 = st.columns(2)
    if not df_cell.empty:
        csv = df_cell.to_csv(index=False).encode('utf-8')
        col_exp1.download_button("📥 Descargar CSV", data=csv, file_name="reportes_celula.csv", mime="text/csv")
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_cell.to_excel(writer, index=False, sheet_name="Reportes")
        col_exp2.download_button("📥 Descargar Excel", data=output.getvalue(), file_name="reportes_celula.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.write("📋 **Nuevos Convertidos**", df_converts)
    st.write("📋 **Estadísticas de Miembros**", df_members)

    # Acción de dar de baja / actualizar estado de miembro
    st.markdown("### ⚙️ Acciones de Miembros")
    if not df_members.empty:
        miembro_id = st.number_input("ID del Miembro para marcar como 'Desertó'", min_value=1, step=1)
        if st.button("Confirmar Estado 'Desertó'"):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE members_stats SET status='desertó' WHERE id=?", (miembro_id,))
            conn.commit()
            conn.close()
            st.success(f"Miembro con ID {miembro_id} actualizado.")
            st.rerun()
