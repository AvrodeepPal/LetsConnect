import streamlit as st
import json

# Load data from JSON file
@st.cache_data
def load_data():
    """Load coordinators and base message from data.json"""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ data.json file not found! Please ensure the file exists in the same directory as app.py")
        st.stop()
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON format in data.json file!")
        st.stop()