import streamlit as st
import re
from datetime import datetime
from utils.email_sender import send_email_with_env_credentials, create_download_link
from db.database import log_mail_activity, get_ist_time

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def render_generated_mail_display(company_name, selected_coordinator):
    if st.session_state.get('mail_generated', False) and st.session_state.get('generated_content', ''):
        st.subheader("📧 Generated Invitation Mail")
        
        edited_content = st.text_area(
            "Generated Email Content (Editable):",
            value=st.session_state.generated_content,
            height=400
        )
        
        st.subheader("📨 Send Email")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hr_email = st.text_input(
                "Enter HR / Company Email:",
                placeholder="hr@company.com"
            )
        
        with col2:
            email_subject = st.text_input(
                "Subject:",
                value="Invitation to Jadavpur University Campus Placement 2026"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if edited_content:
                download_link = create_download_link(
                    edited_content,
                    f"invitation_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                )
                st.markdown(download_link, unsafe_allow_html=True)
        
        with col2:
            send_email_clicked = st.button("📨 Send Email", key="send_email_btn")
            
        if send_email_clicked:
            validation_errors = []
            
            if not hr_email.strip():
                validation_errors.append("❌ Please enter the HR/Company email address.")
            elif not is_valid_email(hr_email.strip()):
                validation_errors.append("❌ Please enter a valid email address.")
            
            if not email_subject.strip():
                validation_errors.append("❌ Please enter an email subject.")
            
            if not edited_content.strip():
                validation_errors.append("❌ Email content cannot be empty.")
            
            if not selected_coordinator:
                validation_errors.append("❌ Please ensure coordinator is selected.")
            
            if not company_name:
                validation_errors.append("❌ Please ensure company name is provided.")
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                with st.spinner("Sending email..."):
                    try:
                        coordinator_email = st.session_state.get('user_email', '')
                        
                        success, message = send_email_with_env_credentials(
                            recipient_email=hr_email.strip(),
                            subject=email_subject.strip(),
                            body=edited_content
                        )
                        
                        if success:
                            st.success("✅ Email sent successfully!")
                            
                            try:
                                # Updated to use coordinator name instead of selected_coordinator directly
                                coordinator_name = selected_coordinator['name'] if selected_coordinator else 'Unknown'
                                
                                log_success, log_message = log_mail_activity(
                                    coordinator_name=coordinator_name,
                                    company_name=company_name,
                                    hr_email=hr_email.strip(),
                                    coordinator_email=coordinator_email,
                                    email_subject=email_subject.strip(),
                                    email_body=edited_content
                                )
                                
                                if not log_success:
                                    st.warning(f"⚠️ Email sent but logging failed: {log_message}")
                                    
                            except Exception as log_error:
                                st.warning(f"⚠️ Email sent but logging failed: {str(log_error)}")
                        else:
                            st.error(f"❌ Failed to send email: {message}")
                            
                    except Exception as e:
                        st.error(f"❌ An error occurred while sending email: {str(e)}")
    
    elif st.session_state.get('mail_generated', False):
        st.info("💡 Generate an invitation mail to see it displayed here.")