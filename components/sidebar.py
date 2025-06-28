import streamlit as st

def render_sidebar(selected_coordinator, company_name):
    """Render the sidebar with settings and information"""
    
    # Enhanced Sidebar
    with st.sidebar:
        st.header("⚙️ Settings & Info")
        
        # Display selected coordinator info
        if selected_coordinator:
            st.subheader("👤 Selected Coordinator")
            st.write(f"**Name:** {selected_coordinator['name']}")
            st.write(f"**Email:** {selected_coordinator['email']}")
            st.write(f"**Phone:** {selected_coordinator['phone']}")
        
        st.divider()
        
        st.subheader("📊 Session Statistics")
        # Get current session stats (you can enhance this with actual tracking)
        if 'mail_count' not in st.session_state:
            st.session_state.mail_count = 0
        if st.session_state.mail_generated and st.session_state.generated_content:
            if 'last_company' not in st.session_state or st.session_state.last_company != company_name:
                st.session_state.mail_count += 1
                st.session_state.last_company = company_name
        
        st.metric("Mails Generated This Session", st.session_state.mail_count)
        st.metric("Current Model", "Mistral AI")
        st.metric("Personalization Level", "High")
        
        st.divider()
        
        st.subheader("🔗 Quick Links")
        st.markdown("- [JU Placement Portal](#)")
        st.markdown("- [Company Database](#)")
        st.markdown("- [Email Templates](#)")
        st.markdown("- [Contact Management](#)")
        
        st.divider()
        
        st.subheader("ℹ️ How It Works")
        st.markdown("""
        1. **Input**: Company details + context
        2. **AI Processing**: Mistral AI analyzes and personalizes
        3. **Generation**: Tailored email created
        4. **Review & Send**: Review, edit, and send
        5. **Track**: Monitor success rates
        """)
        
        st.divider()
        
        st.subheader("💡 Tips for Better Results")
        st.markdown("""
        - **Be Specific**: Add company industry details
        - **Context Matters**: Mention specific roles/skills
        - **Review**: Always review generated content
        - **Personalize**: Edit if needed before sending
        """)