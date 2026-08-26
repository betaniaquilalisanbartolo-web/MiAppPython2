import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------
# 1. Configuración de la página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Interactivo",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Análisis y Control")
st.caption("Aplicación completa desarrollada en Streamlit")

# ---------------------------------------------------------
# 2. Inicialización de Estado de Sesión (Session State)
# ---------------------------------------------------------
if "df" not in st.session_state:
    # Generar datos iniciales ficticios
    np.random.seed(42)
    fechas = pd.date_range(start="2026-01-01", periods=100)
    categorias = ["Electrónica", "Ropa", "Hogar", "Juguetes"]
    
    st.session_state.df = pd.DataFrame({
        "Fecha": np.random.choice(fechas, 100),
        "Categoría": np.random.choice(categorias, 100),
        "Ventas": np.random.randint(100, 1000, 100),
        "Satisfacción": np.random.uniform(3.0, 5.0, 100).round(1)
    })

# ---------------------------------------------------------
# 3. Barra Lateral (Sidebar) - Filtros y Carga de Archivos
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuración y Filtros")
    
    # Subida de archivos opcional
    uploaded_file = st.file_uploader("Cargar tu propio CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.success("¡Archivo cargado correctamente!")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            
    st.divider()
    
    # Filtro por categoría (si la columna existe)
    if "Categoría" in st.session_state.df.columns:
        cats_disponibles = list(st.session_state.df["Categoría"].unique())
        cats_seleccionadas = st.multiselect(
            "Filtrar por Categoría:",
            options=cats_disponibles,
            default=cats_disponibles
        )
    else:
        cats_seleccionadas = []

# Aplicar filtro al DataFrame
df_filtrado = st.session_state.df.copy()
if cats_seleccionadas and "Categoría" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Categoría"].isin(cats_seleccionadas)]

# ---------------------------------------------------------
# 4. Panel Principal - Métricas Clave (KPIs)
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    total_registros = len(df_filtrado)
    st.metric(label="Total Registros", value=total_registros)

with col2:
    if "Ventas" in df_filtrado.columns:
        total_ventas = df_filtrado["Ventas"].sum()
        st.metric(label="Total Ventas ($)", value=f"${total_ventas:,.2f}")
    else:
        st.metric(label="Total Ventas", value="N/A")

with col3:
    if "Satisfacción" in df_filtrado.columns:
        prom_sat = df_filtrado["Satisfacción"].mean()
        st.metric(label="Promedio Satisfacción", value=f"{prom_sat:.2f} / 5.0")
    else:
        st.metric(label="Promedio Satisfacción", value="N/A")

st.divider()

# ---------------------------------------------------------
# 5. Pestañas de Visualización y Datos
# ---------------------------------------------------------
tab_graficos, tab_tabla, tab_agregar = st.tabs(["📈 Gráficos", "📋 Tabla de Datos", "➕ Agregar Registro"])

with tab_graficos:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        if "Categoría" in df_filtrado.columns and "Ventas" in df_filtrado.columns:
            st.subheader("Ventas por Categoría")
            fig_bar = px.bar(
                df_filtrado, 
                x="Categoría", 
                y="Ventas", 
                color="Categoría",
                text_auto=True
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Faltan las columnas 'Categoría' o 'Ventas' para este gráfico.")
            
    with col_g2:
        if "Satisfacción" in df_filtrado.columns and "Ventas" in df_filtrado.columns:
            st.subheader("Relación Satisfacción vs Ventas")
            fig_scatter = px.scatter(
                df_filtrado, 
                x="Satisfacción", 
                y="Ventas", 
                color="Categoría" if "Categoría" in df_filtrado.columns else None
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Faltan las columnas 'Satisfacción' o 'Ventas' para este gráfico.")

with tab_tabla:
    st.subheader("Vista Previa del Dataset")
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Botón de descarga CSV
    csv_bytes = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv_bytes,
        file_name="datos_filtrados.csv",
        mime="text/csv"
    )

with tab_agregar:
    st.subheader("Agregar un nuevo registro manualmente")
    
    with st.form("form_nuevo_registro"):
        nueva_cat = st.selectbox("Categoría", ["Electrónica", "Ropa", "Hogar", "Juguetes"])
        nuevas_ventas = st.number_input("Monto de Ventas ($)", min_value=1, max_value=10000, value=150)
        nueva_sat = st.slider("Puntaje de Satisfacción", 1.0, 5.0, 4.0, step=0.1)
        
        btn_guardar = st.form_submit_button("Guardar Registro")
        
        if btn_guardar:
            nuevo_row = pd.DataFrame([{
                "Fecha": pd.Timestamp.now(),
                "Categoría": nueva_cat,
                "Ventas": nuevas_ventas,
                "Satisfacción": nueva_sat
            }])
            # Actualizar el DataFrame en sesión
            st.session_state.df = pd.concat([st.session_state.df, nuevo_row], ignore_index=True)
            st.success("¡Registro agregado exitosamente!")
            st.rerun()
