import streamlit as st

from core.auth import check_password, logout_button
from core.navigation import PAGES

st.set_page_config(
    page_title="Мультисервис",
    page_icon="🧩",
    layout="wide",
)

if not check_password():
    st.stop()

logout_button()

st.sidebar.title("Навигация")
selected_page = st.sidebar.radio("Выберите страницу", list(PAGES.keys()))
PAGES[selected_page]()