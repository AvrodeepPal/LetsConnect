import streamlit as st

def render_base_invitation_section(base_message_template):
    """Render the Base Invitation Message section"""
    st.subheader("📝 Base Invitation Message")
    st.write("Customize the template message that will be sent to companies:")

    base_message = st.text_area(
        label="Base Invitation Message",
        value=base_message_template,
        height=400,
        help="Use placeholders like {company_name}, {name}, {contact}, {cc_email} for personalization"
    )
    
    return base_message