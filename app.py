import streamlit as st

from utils.data_loader import load_data
from utils.openrouter_client import init_openrouter_client

from components.sidebar import render_sidebar
from components.expander import render_expanders
from components.markdown import render_footer_markdown
from components.base_invitation import render_base_invitation_section
from components.company_info import render_company_info_section
from components.generate_ainvite import render_generate_section, render_generated_mail_display

# Configure page
st.set_page_config(
    page_title="Lets Connect!",
    page_icon="🤝",
    layout="wide"
)

# Load data
data = load_data()
coordinators = data.get('coordinators', [])
base_message_template = data.get('base_message', '')
client = init_openrouter_client()

# Main title
st.title("🤝 Lets Connect!")
st.markdown("*Generate personalized invitation emails for campus recruitment drives*")

st.divider()

# Base Message Section
base_message = render_base_invitation_section(base_message_template)

st.divider()

# Company Information Section
company_name, selected_coordinator, additional_info, num_bullet_points = render_company_info_section(coordinators)

st.divider()

# Generate Section
render_generate_section(company_name, selected_coordinator, additional_info, base_message, client, num_bullet_points)

st.divider()

# Display generated mail section
render_generated_mail_display(company_name, selected_coordinator)

# Render components
render_sidebar(selected_coordinator, company_name)
render_expanders()
render_footer_markdown()