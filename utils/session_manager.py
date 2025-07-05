import streamlit as st
import pytz
from datetime import datetime

IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    return datetime.now(IST)

def set_user_session(user_data):
    st.session_state['user_logged_in'] = True
    st.session_state['user_data'] = user_data
    st.session_state['login_time'] = get_ist_time().isoformat()

def clear_user_session():
    keys_to_clear = [
        'user_logged_in',
        'user_data',
        'login_time',
        'otp_email',
        'otp_sent',
        'otp_send_time',
        'login_step',
        'verified_user'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def is_user_logged_in():
    return st.session_state.get('user_logged_in', False)

def get_current_user():
    if is_user_logged_in():
        return st.session_state.get('user_data')
    return None

def get_user_login_time():
    if is_user_logged_in():
        return st.session_state.get('login_time')
    return None

def update_user_session(updated_data):
    if is_user_logged_in():
        current_data = st.session_state.get('user_data', {})
        current_data.update(updated_data)
        st.session_state['user_data'] = current_data

def get_session_info():
    return {
        'is_logged_in': is_user_logged_in(),
        'user_data': get_current_user(),
        'login_time': get_user_login_time()
    }