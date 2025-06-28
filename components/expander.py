import streamlit as st

def render_expanders():
    """Render all expandable sections"""
    
    # Main app info expander
    with st.expander("ℹ️ About Lets Connect! - AI Edition"):
        st.markdown("""
        **Lets Connect!** is an AI-powered application designed to help the Jadavpur University MCA Placement Cell 
        generate and send highly personalized recruitment invitation emails to companies.
        
        **🚀 New AI Features:**
        - 🤖 **AI-Powered Personalization**: Each email is uniquely crafted for the target company
        - 🎯 **Industry-Specific Content**: Skills and messaging tailored to company's domain
        - 📊 **Smart Context Analysis**: Uses additional company info for better personalization
        - 🔄 **Multiple Variations**: Generate different versions of the same invitation
        - ✂️ **Clean Output**: Concise, professional emails without unnecessary fluff
        - 📏 **Proper Spacing**: Professional formatting with appropriate gaps between sections
        
        **📧 Core Features:**
        - 📝 Dynamic email generation (no more templates!)
        - 👥 Multiple coordinator profiles
        - 📧 Direct email sending capability
        - 📋 One-click clipboard copying
        - 💾 Draft saving functionality
        - 📊 Session statistics tracking
        
        **🔧 Technical Requirements:**
        - `data.json` file with coordinator information
        - `.env` file with `OPENROUTER_API_KEY`
        - Gmail accounts with app passwords enabled
        - Internet connection for AI generation and email sending
        
        **🔒 Security & Privacy:**
        - Passwords never stored in memory
        - API keys secured in environment variables
        - All generation happens in real-time
        
        **🎨 Personalization Examples:**
        - **Tech Companies**: Focus on AI/ML, cloud, software development
        - **Finance**: Emphasize quantitative analysis, risk management
        - **Consulting**: Highlight problem-solving, analytics
        - **Startups**: Mention agility, full-stack capabilities
        """)

    
    # FAQ expander
    with st.expander("❓ Frequently Asked Questions"):
        st.markdown("""
        **Q: How does the AI personalization work?**
        A: The AI analyzes the company name and additional context you provide to generate industry-specific content, relevant skills, and tailored messaging.
        
        **Q: Can I edit the generated email before sending?**
        A: Yes! The generated email appears in an editable text area where you can make any modifications before sending or copying.
        
        **Q: What if the AI generation fails?**
        A: The app includes a fallback template that ensures you always get a professional email, even if the AI service is temporarily unavailable.
        
        **Q: How do I get a Gmail app password?**
        A: Go to Google Account Settings → Security → 2-Step Verification → App passwords, then generate a password for "Mail" application.
        
        **Q: Can I save emails for later use?**
        A: Yes! Use the "Save Draft" button to download the generated email as a text file with timestamp.
        
        **Q: Is my data secure?**
        A: Yes, all passwords are handled securely, API keys are stored in environment variables, and no sensitive data is permanently stored.
        """)

    # Troubleshooting expander
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Email sending fails:**
        - Verify Gmail app password is correct
        - Ensure 2-factor authentication is enabled
        - Check internet connection
        - Confirm recipient email format is valid
        
        **AI generation not working:**
        - Check if OPENROUTER_API_KEY is set in .env file
        - Verify internet connection
        - Try again - sometimes API calls may timeout
        
        **App won't start:**
        - Ensure data.json file exists in the same directory
        - Check JSON format is valid
        - Verify all required packages are installed
        
        **Generated email looks wrong:**
        - Review the additional company information provided
        - Try regenerating with more specific context
        - Manual editing is always available
        
        **Coordinator information missing:**
        - Check data.json file structure
        - Ensure all coordinator fields (name, email, phone) are present
        - Restart the app after making changes to data.json
        """)