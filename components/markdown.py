import streamlit as st

def render_header():
    st.title("🤝 Lets Connect!")
    st.markdown("*Generate personalized invitation emails for campus recruitment drives*")
    st.divider()

def render_footer_markdown():
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>Developed with ❤️ by the JUMCA Placement 2024-26</p>
            <p><em>AI-Powered Campus Recruitment Communications</em></p>
            <p style='font-size: 12px; margin-top: 10px;'>
                🤖 Powered by Mistral AI for personalized content generation
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_section_header(title, subtitle=None):
    st.subheader(title)
    if subtitle:
        st.markdown(f"*{subtitle}*")

def render_info_message(message_type="info", message=""):
    if message_type == "info":
        st.info(message)
    elif message_type == "success":
        st.success(message)
    elif message_type == "warning":
        st.warning(message)
    elif message_type == "error":
        st.error(message)

def render_instructions():
    st.markdown("""
    ### 📋 How to Use:
    
    1. **📝 Customize Base Message**: Edit the template message in the text area above
    2. **🏢 Enter Company Details**: Fill in the company name and select a coordinator
    3. **📝 Add Context**: Provide additional company information for better personalization
    4. **🤖 Generate**: Click the generate button to create an AI-powered invitation
    5. **📧 Review & Send**: Review the generated email and send it directly or copy to clipboard
    
    ### ✨ Pro Tips:
    - Be specific about company industry and hiring needs
    - Include relevant technologies or skill requirements
    - Review and edit the generated content before sending
    - Save drafts for future reference
    """)

def render_features_showcase():
    """Render the features showcase section"""
    st.markdown("""
    ### 🌟 Key Features:
    
    | Feature | Description |
    |---------|-------------|
    | 🤖 **AI-Powered** | Generate personalized emails using advanced AI |
    | 🎯 **Industry-Specific** | Content tailored to company's domain and needs |
    | 📧 **Direct Sending** | Send emails directly from the app |
    | 📋 **Easy Copying** | One-click copy to clipboard |
    | 💾 **Draft Management** | Save and download email drafts |
    | 👥 **Multi-Coordinator** | Support for multiple placement coordinators |
    | 🔄 **Regeneration** | Generate multiple versions of the same email |
    | 📊 **Session Tracking** | Track your email generation activity |
    """)

def render_loading_message(message="Processing..."):
    with st.spinner(message):
        pass

def render_stats_cards(stats_data):
    """Render statistics cards"""
    cols = st.columns(len(stats_data))
    for i, (label, value) in enumerate(stats_data.items()):
        with cols[i]:
            st.metric(label=label, value=value)

def render_company_info_help():
    st.markdown("""
    ### 💡 Company Information Tips:
    
    **Company Name:**
    - Use the official company name as it appears on their website
    - Examples: "Google", "Microsoft", "Goldman Sachs", "Tata Consultancy Services"
    
    **Additional Information:**
    - Mention specific job roles they typically hire for
    - Include preferred technologies or skill sets
    - Note any special requirements or preferences
    - Add information about company culture or values
    
    **Example Additional Info:**
    *"Leading fintech company focusing on digital payments and blockchain technology. 
    Typically hires for software engineering, data science, and product management roles. 
    Strong preference for candidates with Python, React, and cloud computing experience."*
    """)

def render_email_preview_header():
    st.markdown("### 👀 Email Preview:")
    st.markdown("**Subject:** Campus Recruitment Invitation - Jadavpur University")

def render_action_buttons_help():
    st.markdown("""
    ### 🎯 Available Actions:
    
    - **📋 Copy to Clipboard**: Copy the email content for pasting elsewhere
    - **📧 Send Email**: Send the email directly using coordinator's Gmail account
    - **💾 Save Draft**: Download the email as a text file for future use
    - **🔄 Generate New Version**: Create a different variation of the email
    """)

def render_security_notice():
    st.markdown("""
    ### 🔒 Security & Privacy Notice:
    
    - Gmail passwords are never stored in the application
    - All API keys are securely stored in environment variables
    - Email generation happens in real-time without data retention
    - Your data is processed securely and not shared with third parties
    """)

def render_api_status(status="active"):
    if status == "active":
        st.success("🟢 AI Service: Active")
    elif status == "inactive":
        st.error("🔴 AI Service: Inactive")
    elif status == "unknown":
        st.warning("🟡 AI Service: Status Unknown")