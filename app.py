        st.write("💰 **Ofrendas Totales por Célula**")
        if not df_cell.empty:
            ofrendas_por_celula = df_cell.groupby('cell_name')['offering'].sum().reset_index()
            st.bar_chart(data=ofrendas_por_celula, x='cell_name', y='offering')
        else:
            st.info("Agrega reportes de células para visualizar métricas financieras.")

    st.markdown("---")

    # --- 3. VISTA Y DESCARGA DE DATOS ---
    st.markdown("### 📥 Tablas de Datos y Exportación")
    
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Reportes de Células", "🌱 Nuevos Convertidos", "👥 Miembros"])

    with sub_tab1:
        st.dataframe(df_cell, use_container_width=True)
        if not df_cell.empty:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_cell.to_excel(writer, index=False, sheet_name='Celulas')
            st.download_button(
                label="📥 Descargar Reportes de Células (Excel)",
                data=output.getvalue(),
                file_name="reportes_celulas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with sub_tab2:
        st.dataframe(df_converts, use_container_width=True)
        if not df_converts.empty:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_converts.to_excel(writer, index=False, sheet_name='Convertidos')
            st.download_button(
                label="📥 Descargar Nuevos Convertidos (Excel)",
                data=output.getvalue(),
                file_name="nuevos_convertidos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with sub_tab3:
        st.dataframe(df_members, use_container_width=True)
        if not df_members.empty:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_members.to_excel(writer, index=False, sheet_name='Miembros')
            st.download_button(
                label="📥 Descargar Miembros (Excel)",
                data=output.getvalue(),
                file_name="miembros.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
