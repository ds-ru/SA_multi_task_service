import asyncio
from io import BytesIO

import pandas as pd
import streamlit as st

from for_decline.decline_all_ads import get_ads_list, main as decline_all_main
from for_decline.reasons_registry import DeclineReasonsRegistry


def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()


def render_reasons_reference():
    st.subheader("Справочник причин отклонения")

    reasons = DeclineReasonsRegistry.all()

    with st.expander("Популярные причины", expanded=True):
        popular_ids = {2, 18, 31, 33, 32, 23}
        for reason in reasons:
            if reason.id in popular_ids:
                st.markdown(f"**{reason.id} — {reason.title}**")
                st.caption(reason.description_html)
                st.divider()

    with st.expander("Все причины"):
        for reason in reasons:
            st.markdown(f"**{reason.id} — {reason.title}**")
            st.caption(reason.description_html)
            st.divider()


def render():
    st.title("Модуль для отклонения всех объявлений кабинета")
    st.subheader("Предназначен для применения одной причины на весь кабинет")

    st.session_state.setdefault("decline_ads_df", None)
    st.session_state.setdefault("decline_result", None)

    reasons = DeclineReasonsRegistry.all()
    reason_options = {
        f"{reason.id} — {reason.title}": reason.id
        for reason in reasons
    }

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Шаг 1. Данные кабинета")
        account = st.text_input("Введите account_id или account_name")

        st.markdown("### Шаг 2. Выбор причины отклонения")
        selected_reason_label = st.selectbox(
            "Выберите причину из справочника",
            options=list(reason_options.keys()),
            index=0,
        )
        selected_reason_id = reason_options[selected_reason_label]

        manual_reason_id = st.text_input(
            "Или введите reason_id вручную",
            value=str(selected_reason_id),
        )

        try:
            decline_reason_id = int(manual_reason_id)
            selected_reason = DeclineReasonsRegistry.get(decline_reason_id)
            st.info(f"Выбрана причина: {selected_reason.id} — {selected_reason.title}")
        except Exception:
            decline_reason_id = None
            st.error("Некорректный reason_id")

        st.divider()

        if st.button("Загрузить объявления"):
            if not account:
                st.error("Укажите account_id или title")
            else:
                with st.spinner("Загружаем объявления..."):
                    try:
                        ads_df = asyncio.run(get_ads_list(account))
                        st.session_state["decline_ads_df"] = ads_df
                        st.session_state["decline_result"] = None
                        st.success(f"Загружено объявлений: {len(ads_df)}")
                    except Exception as e:
                        st.error(f"Ошибка загрузки: {e}")

        ads_df = st.session_state.get("decline_ads_df")

        if ads_df is not None:
            st.markdown("### Шаг 3. Проверка списка")
            st.write(f"Найдено объявлений к обработке: {len(ads_df)}")
            st.dataframe(ads_df, width="stretch")

            if decline_reason_id is not None:
                st.warning(
                    f"Будет применена причина {decline_reason_id} "
                    f"ко всем объявлениям из списка."
                )

            st.markdown("### Шаг 4. Запуск отклонения")
            if st.button("Запустить отклонение", type="primary"):
                if not account:
                    st.error("Укажите account")
                elif decline_reason_id is None:
                    st.error("Укажите корректную причину отклонения")
                else:
                    with st.spinner("Выполняем отклонение объявлений..."):
                        try:
                            result = asyncio.run(
                                decline_all_main(
                                    account=account,
                                    decline_reason_id=decline_reason_id,
                                )
                            )
                            st.session_state["decline_result"] = result
                            st.success("Обработка завершена")
                        except Exception as e:
                            st.error(f"Ошибка выполнения: {e}")

        result = st.session_state.get("decline_result")
        if result:
            st.divider()
            st.subheader("Результат")

            st.write(f"Всего: {result['total']}")
            st.write(f"Успешно: {result['success']}")
            st.write(f"С ошибкой: {result['failed']}")

            failed_df = result["failed_df"]
            if not failed_df.empty:
                st.warning(f"Неудачных вызовов: {len(failed_df)}")
                st.dataframe(failed_df, width="stretch")

                st.download_button(
                    label="Скачать failed_decline.xlsx",
                    data=df_to_excel_bytes(failed_df),
                    file_name="failed_decline.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

    with col2:
        render_reasons_reference()