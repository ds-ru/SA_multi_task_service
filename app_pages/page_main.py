import streamlit as st

def render():
    st.title("🧩 Мультисервис")

    st.subheader("Доступные сервисы")
    st.write("1. Сверка статистики API")
    st.write("2. Сверка статистики Magnetto + загрузка бенчей")
    st.write("3. Выгрузка бэкапов")
    st.write("4. Полное отклонение кабинета")
    st.write("5. Проверка текущей статистики в базах")
