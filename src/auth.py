import streamlit as st
import bcrypt

def check_password():
    """Returns `True` if the user had the correct password."""
    
    # Load users from secrets safely
    if "passwords" not in st.secrets:
        st.error("Secrets not found. Please check .streamlit/secrets.toml")
        return False
        
    USERS = st.secrets["passwords"]

    def password_entered():
        if st.session_state["username"] in USERS and st.session_state["password"]:
            stored_hash = USERS[st.session_state["username"]]
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            if bcrypt.checkpw(st.session_state["password"].encode(), stored_hash):
                st.session_state["password_correct"] = True
                del st.session_state["password"]
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        return True
