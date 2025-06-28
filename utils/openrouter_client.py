import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenRouter client
@st.cache_resource
def init_openrouter_client():
    """Initialize OpenRouter client"""
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            st.error("❌ OPENROUTER_API_KEY not found in .env file!")
            return None
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
    except Exception as e:
        st.error(f"Failed to initialize OpenRouter client: {e}")
        return None