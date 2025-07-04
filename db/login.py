import streamlit as st
from db.auth import verify_user, log_user_session
from db.otp import generate_and_send_otp, render_otp_page

def render_login_page():
    """
    Render the login page UI and handle authentication with OTP
    """
    # Check if we're in OTP verification stage
    if st.session_state.get("otp_stage", False):
        email = st.session_state.get("otp_email", "")
        
        if email:
            # Render OTP page
            render_otp_page(email)
            return
    
    # Regular login page
    st.title("🤝 Coordinator Login")
    st.markdown("*Please enter your credentials to access the system*")
    
    # Create login form
    with st.form("login_form"):
        st.subheader("Login Details")
        
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address",
            help="Use the email address registered in the system"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="Enter your account password"
        )
        
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
                return False
            
            # Verify credentials
            with st.spinner("Verifying credentials..."):
                success, message, user_data = verify_user(email, password)
            
            if success:
                st.success(f"✅ Credentials verified for {user_data['name']}!")
                
                # Generate and send OTP
                with st.spinner("Generating OTP..."):
                    otp_success, otp_message = generate_and_send_otp(email)
                
                if otp_success:
                    st.success("📧 OTP sent to your email!")
                    st.info("Please check your email and enter the OTP to complete login.")
                    
                    # Set OTP stage in session state
                    st.session_state["otp_stage"] = True
                    st.session_state["otp_email"] = email
                    st.session_state["temp_user_data"] = user_data
                    
                    # Rerun to show OTP page
                    st.rerun()
                else:
                    st.error(f"❌ Failed to send OTP: {otp_message}")
                    st.error("Please try again or contact support.")
                
            else:
                st.error(f"❌ {message}")
    
    # Additional UI elements
    st.divider()
    
    with st.expander("ℹ️ Need Help?"):
        st.markdown("""
        **Having trouble logging in?**
        
        - Make sure you're using the correct email address
        - Check that your password is entered correctly
        - Contact the system administrator if you've forgotten your credentials
        
        **Two-Factor Authentication:**
        - After successful credential verification, you'll receive an OTP via email
        - Enter the OTP to complete your login
        - OTP is valid for 5 minutes only
        
        **Security Note:** Your session will be logged for security purposes.
        """)
    
    return False

def handle_logout():
    """
    Handle user logout by clearing session state
    """
    # Clear all session state related to login
    keys_to_clear = [
        "logged_in", 
        "user_data", 
        "user_email", 
        "user_name", 
        "user_roll",
        "otp_stage",
        "otp_email",
        "temp_user_data"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Logged out successfully!")
    st.rerun()

def check_authentication():
    """
    Check if user is authenticated
    Returns: bool
    """
    return st.session_state.get("logged_in", False)

def get_current_user():
    """
    Get current logged-in user data
    Returns: dict or None
    """
    if check_authentication():
        return st.session_state.get("user_data", None)
    return None

def clear_otp_session():
    """
    Clear OTP-related session state
    """
    keys_to_clear = [
        "otp_stage", 
        "otp_email",
        "temp_user_data"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]