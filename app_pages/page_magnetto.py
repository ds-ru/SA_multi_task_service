import asyncio
import streamlit as st

from core.constants import start_prev_month, end_prev_month
from monthly_reports.pg_main import MonthlyReportPG


def render():
    st.title("🧮 Сверка статистики Magnetto")
    st.subheader("https://drive.google.com/drive/u/1/folders/")
    st.markdown(
        f"### :blue-background[Выгрузки и вставки будут за период: {start_prev_month} - {end_prev_month}]"
    )
    st.divider()

    if st.button("Сформировать PG отчет"):
        with st.spinner("Формируем отчет..."):
            try:
                report = MonthlyReportPG()
                file_name, file_bytes = asyncio.run(report.export_pg())
                st.success("Отчет готов")
                st.download_button(
                    label="Скачать файл",
                    data=file_bytes,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            except Exception as e:
                st.error(str(e))