import asyncio

import pandas as pd
import streamlit as st

from obj_storage.main import download_s3_object
from utils import prepare_download_files


def render():
    st.title("🗂️ Работа с объектным хранилищем")

    # try:
    #     # objects_list = asyncio.run(get_s3_objects())
    #     objects_list = None
    #     if not objects_list:
    #         st.info("Объекты не найдены")
    #         return
    #
    #     rows = []
    #     for obj in objects_list:
    #         rows.append({
    #             "key": obj.get("Key"),
    #             "size": obj.get("Size"),
    #             "last_modified": obj.get("LastModified"),
    #         })
    #
    #     st.dataframe(rows, width='stretch')
    #
    # except Exception as e:
    #     st.error(f"Ошибка при получении списка объектов: {e}")

    st.divider()

    zip_date = st.text_input("Введите дату вида: YYYY-MM-DD")

    zip_period = st.selectbox(
        "Тип архива",
        ("schema", "schema")
    )

    zip_schema = st.selectbox(
        "Из какой схемы нужны данные?",
        ("schema", "schema", "schema", "schema", "schema")
    )

    zip_table = None

    # CLICKHOUSE DAILY
    if zip_period == "schema" and zip_schema == "schema":

        zip_table = st.selectbox(
            "Какая таблица?",
            (
                "account_info",
                "account_list",
                "account_report",
                "account_stats",
                "ads_list",
            )
        )


    elif zip_period == "schema" and zip_schema == "schema":

        zip_table = st.selectbox(
            "Какая таблица?",
            (
                "account_info",
                "account_list",
                "account_report",
                "account_stats",
                "ads_list",
                "ads_list_raw",
            )
        )


    elif zip_period == "schema" and zip_schema == "schema":

        zip_table = st.selectbox(
            "Какая таблица?",
            (
                "ads_moder_api_2",
                "ads_moder_api_cli",
            )
        )


    elif zip_period == "schema" and zip_schema == "schema":

        zip_table = st.selectbox(
            "Какая таблица?",
            (
                "audit",
                "bench_temp",
            )
        )


    # POSTGRES DAILY
    elif zip_period == "schema" and zip_schema == "schema":

        zip_table = st.selectbox(
            "Какая таблица?",
            (
                "account_report",
                "account_stats",
                "ads_list",
                "ads_list_raw",
                "related_accounts",
            )
        )


    # MONTHLY CLICKHOUSE
    elif zip_period == "schema" and zip_schema in ("schema", "schema"):

        zip_table = st.selectbox(
            "Какая таблица?",
            (
                "ad_stats",
            )
        )


    # MONTHLY POSTGRES
    elif zip_period == "schema" and zip_schema == "schema":

        zip_table = st.selectbox(
            "Какая таблица?",
            (
                "ad_stats",
                "ad_stats_vitrina",
            )
        )

    if zip_table and zip_date:
        zip_key = f"{zip_period}/{zip_schema}_{zip_table}_{zip_date}.zip"

        st.info(f"Файл будет загружен из:\n{zip_key}")

        if st.button("Подготовить файлы"):
            try:
                with st.spinner("Скачиваем архив из object storage..."):
                    zip_bytes = asyncio.run(download_s3_object(zip_key))

                with st.spinner("Распаковываем и конвертируем..."):
                    df, xlsx_buffer, csv_buffer = prepare_download_files(zip_bytes)

                st.session_state["zip_bytes"] = zip_bytes
                st.session_state["xlsx_bytes"] = xlsx_buffer.getvalue()
                st.session_state["csv_bytes"] = csv_buffer.getvalue()
                st.session_state["preview_df"] = df

                st.success("Файлы подготовлены")

            except Exception as e:
                st.error(f"Ошибка загрузки: {e}")

        if "zip_bytes" in st.session_state:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.download_button(
                    label="Скачать архив",
                    data=st.session_state["zip_bytes"],
                    file_name=f"{zip_schema}_{zip_table}_{zip_date}.zip",
                    mime="application/zip",
                    width='stretch',
                )

            with col2:
                st.download_button(
                    label="Скачать xlsx",
                    data=st.session_state["xlsx_bytes"],
                    file_name=f"{zip_schema}_{zip_table}_{zip_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width='stretch',
                )

            with col3:
                st.download_button(
                    label="Скачать csv",
                    data=st.session_state["csv_bytes"],
                    file_name=f"{zip_schema}_{zip_table}_{zip_date}.csv",
                    mime="text/csv",
                    width='stretch',
                )

        if "preview_df" in st.session_state:
            st.divider()
            st.subheader("Предпросмотр данных")

            df_preview = st.session_state["preview_df"]

            filter_value = st.text_input("Фильтр по всем текстовым колонкам")

            if filter_value:
                text_cols = df_preview.select_dtypes(include=["object", "string"]).columns
                if len(text_cols) > 0:
                    mask = pd.Series(False, index=df_preview.index)
                    for col in text_cols:
                        mask = mask | df_preview[col].astype(str).str.contains(filter_value, case=False, na=False)
                    df_preview = df_preview[mask]

            st.dataframe(df_preview, width='stretch')