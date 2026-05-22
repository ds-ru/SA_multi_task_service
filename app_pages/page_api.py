import asyncio
import streamlit as st

from core.constants import start_prev_month, end_prev_month
from monthly_reports.ch_main import MonthlyReportCH


def render():
    st.title("📊 Сверка статистики API + Загрузка бенчей")

    st.subheader("https://drive.google.com/drive/u/1/folders/")
    st.subheader("https://datalens.yandex/")
    st.markdown(f"### :blue-background[Выгрузки и вставки будут за период: {start_prev_month} - {end_prev_month}]")
    st.divider()

    if st.button("Сформировать CH bench отчет"):

        with st.spinner("Формируем отчет..."):
            try:
                report = MonthlyReportCH()

                file_name, file_bytes = asyncio.run(
                    report.export_ch_bench()
                )

                st.success("Отчет готов")

                st.download_button(
                    label="Скачать файл",
                    data=file_bytes,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(str(e))

    if st.button("Сформировать CH PLACEHOLDER отчет"):

        with st.spinner("Формируем отчет..."):
            try:
                report = MonthlyReportCH()

                file_name, file_bytes = asyncio.run(
                    report.export_ch_PLACEHOLDER()
                )

                st.success("Отчет готов")

                st.download_button(
                    label="Скачать файл",
                    data=file_bytes,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(str(e))

    if "confirm_insert" not in st.session_state:
        st.session_state.confirm_insert = False

    if not st.session_state.confirm_insert:

        if st.button("Вставить бенчи"):
            st.session_state.confirm_insert = True
            st.rerun()

    else:

        st.warning("⚠️ Вы уверены, что хотите вставить бенчи в БД?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Да, выполнить", icon="✔️"):
                with st.spinner("Вставка данных..."):
                    try:
                        report = MonthlyReportCH()
                        asyncio.run(report.insert_bench())

                        st.success("Бенчи успешно вставлены")

                    except Exception as e:
                        st.error(str(e))

                st.session_state.confirm_insert = False
                st.rerun()

        with col2:
            if st.button("Отмена", type="primary", icon="❌"):
                st.session_state.confirm_insert = False
                st.rerun()
