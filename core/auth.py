import hashlib
import hmac
import time
import streamlit as st

from config.service import APP_PASSWORD

MAX_ATTEMPTS = 5
LOCK_SECONDS = 600

def verify_password(password: str) -> bool:
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return hmac.compare_digest(password_hash, APP_PASSWORD)

def init_auth_state():
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("login_attempts", 0)
    st.session_state.setdefault("locked_until", 0.0)

def check_password():
    init_auth_state()

    if st.session_state.authenticated:
        return True

    now = time.time()
    locked_until = st.session_state.locked_until

    if now < locked_until:
        remaining = int(locked_until - now)
        st.title("Вход")
        st.error(f"Слишком много попыток. Повторите через {remaining} сек.")
        return False

    st.title("Вход")
    password = st.text_input("Введите пароль", type="password", key="password_input")

    if st.button("Войти"):
        if verify_password(password):
            st.session_state.authenticated = True
            st.session_state.login_attempts = 0
            st.session_state.locked_until = 0.0
            st.success("Вход выполнен")
            st.rerun()
        else:
            st.session_state.login_attempts += 1
            attempts_left = MAX_ATTEMPTS - st.session_state.login_attempts

            time.sleep(min(st.session_state.login_attempts, 3))

            if st.session_state.login_attempts >= MAX_ATTEMPTS:
                st.session_state.locked_until = time.time() + LOCK_SECONDS
                st.error(
                    f"Слишком много попыток. Вход заблокирован на {LOCK_SECONDS // 60} мин."
                )
            else:
                st.error(f"Неверный пароль. Осталось попыток: {attempts_left}")

    return False

def logout_button():
    if st.sidebar.button("Выйти"):
        st.session_state.authenticated = False
        st.rerun()