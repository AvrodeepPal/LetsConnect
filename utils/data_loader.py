import os
import json
import streamlit as st
from supabase import create_client, Client
from typing import Dict, List, Any

def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    return create_client(url, key)

@st.cache_data
def load_coordinators_from_supabase() -> List[Dict[str, Any]]:
    """Load coordinator data from Supabase with caching"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('coord_details').select('*').execute()
        
        if response.data:
            return response.data
        else:
            st.error("❌ No coordinator data found in database")
            return []
            
    except Exception as e:
        st.error(f"❌ Error loading coordinators from Supabase: {str(e)}")
        return []

@st.cache_data
def load_base_message_from_json() -> str:
    """Load base message template from local JSON file with caching"""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('base_message', '')
    except FileNotFoundError:
        st.error("❌ data.json file not found! Please ensure the file exists in the same directory as app.py")
        st.stop()
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON format in data.json file!")
        st.stop()

@st.cache_data
def load_data() -> Dict[str, Any]:
    """Load all application data with caching"""
    coordinators = load_coordinators_from_supabase()
    base_message = load_base_message_from_json()
    
    return {
        'coordinators': coordinators,
        'base_message': base_message
    }

def get_unique_departments(coordinators: List[Dict[str, Any]]) -> List[str]:
    """Get unique departments from coordinators list"""
    departments = set()
    for coord in coordinators:
        dept = coord.get('department', '').strip()
        if dept:
            departments.add(dept)
    return sorted(list(departments))

def get_coordinators_by_department(coordinators: List[Dict[str, Any]], department: str) -> List[Dict[str, Any]]:
    """Filter coordinators by department"""
    return [coord for coord in coordinators if coord.get('department', '').strip() == department]