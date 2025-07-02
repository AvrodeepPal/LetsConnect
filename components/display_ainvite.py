import streamlit as st
from datetime import datetime
from utils.email_sender import send_email, create_download_link

def render_generated_mail_display(company_name, selected_coordinator):
    """Render the generated mail display section"""
    if st.session_state.get('mail_generated', False) and st.session_state.get('generated_content', ''):
        st.subheader("📧 Generated Invitation Mail")
        
        # Display the generated mail in a text area for easy copying
        st.text_area(
            "Generated Email Content:",
            value=st.session_state.generated_content,
            height=400,
            help="You can copy this content and paste it into your email client"
        )
        
        # Download and email options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download as text file
            if st.session_state.generated_content:
                download_link = create_download_link(
                    st.session_state.generated_content,
                    f"invitation_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                )
                st.markdown(download_link, unsafe_allow_html=True)
        
        with col2:
            # Send email button
            if st.button("📨 Send Email", key="send_email_btn"):
                if selected_coordinator and company_name:
                    success = send_email(
                        st.session_state.generated_content,
                        company_name,
                        selected_coordinator
                    )
                    if success:
                        st.success("✅ Email sent successfully!")
                    else:
                        st.error("❌ Failed to send email. Please check your email configuration.")
                else:
                    st.error("❌ Please ensure company name and coordinator are selected.")
        
        with col3:
            # Copy to clipboard info
            st.info("💡 Use Ctrl+A then Ctrl+C to copy the email content above")
    
    elif st.session_state.get('mail_generated', False):
        st.info("💡 Generate an invitation mail to see it displayed here.")