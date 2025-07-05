import streamlit as st
from db.auth import authenticate_user
from db.database import get_user_by_email as get_user_info
from utils.otp_sender import generate_and_send_otp, get_otp_status
from db.otp import verify_otp, get_otp_times_ist, is_otp_expired
from db.verify import verify_otp as verify_otp_legacy  # For backward compatibility if needed
from utils.session_manager import set_user_session, clear_user_session, is_user_logged_in
import time
from datetime import datetime, timezone, timedelta

def render_login_form():
    st.title("🤝 Coordinator Login")
    st.markdown("*Please enter your credentials to access the system*")
    
    if is_user_logged_in():
        st.success("You are already logged in!")
        if st.button("Logout"):
            clear_user_session()
            st.rerun()
        return
    
    # Initialize session state variables
    if 'login_step' not in st.session_state:
        st.session_state.login_step = 'credentials'
    if 'verified_user' not in st.session_state:
        st.session_state.verified_user = None
    if 'otp_email' not in st.session_state:
        st.session_state.otp_email = ""
    if 'otp_dt' not in st.session_state:
        st.session_state.otp_dt = ""
    
    # Render appropriate form based on login step
    if st.session_state.login_step == 'credentials':
        render_credentials_form()
    elif st.session_state.login_step == 'otp_verification':
        render_otp_verification_form()

def extract_time_from_session_id(session_id):
    """Extract sent time and expiry time from session ID (DDMMYYHHMM format)"""
    if not session_id or len(session_id) < 10:
        return None, None
    
    try:
        # Extract HHMM from session ID (last 4 digits)
        time_str = session_id[-4:]  # Get last 4 digits (HHMM)
        hours = int(time_str[:2])
        minutes = int(time_str[2:])
        
        # Create sent time
        sent_time = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
        
        # Calculate expiry time (sent time + 5 minutes)
        expiry_time = sent_time + timedelta(minutes=5)
        
        return sent_time, expiry_time
    except (ValueError, IndexError):
        return None, None

def render_credentials_form():
    with st.form("credentials_form"):
        st.subheader("Login Credentials")
        
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )
        
        submitted = st.form_submit_button("Verify Credentials", use_container_width=True)
        
        if submitted:
            handle_credentials_verification(email, password)

def render_otp_verification_form():
    email = st.session_state.otp_email
    dt = st.session_state.otp_dt
    
    if not email or not dt:
        st.error("Session expired. Please login again.")
        reset_login_state()
        st.rerun()
        return
    
    st.info(f"OTP sent to: {email}")
    st.write(f"**Session ID:** {dt}")
    
    # Show OTP timing information extracted from session ID
    sent_time, expiry_time = extract_time_from_session_id(dt)
    if sent_time and expiry_time:
        st.write(f"**OTP sent at:** {sent_time.strftime('%I:%M %p')}")
        st.write(f"**OTP expires at:** {expiry_time.strftime('%I:%M %p')}")
    
    # Check if OTP is expired
    if is_otp_expired(email, dt):
        st.error("⏰ OTP has expired!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Request New OTP", use_container_width=True):
                handle_otp_resend(email)
        with col2:
            if st.button("Back to Login", use_container_width=True):
                reset_login_state()
        return
    
    # OTP verification form
    with st.form("otp_verification_form"):
        st.write("Enter the OTP sent to your email")
        
        otp = st.text_input(
            "OTP",
            placeholder="Enter 6-digit OTP",
            max_chars=6
        )
        
        col1, col2 = st.columns(2)
        with col1:
            verify_submitted = st.form_submit_button("Verify OTP", use_container_width=True)
        with col2:
            resend_submitted = st.form_submit_button("Resend OTP", use_container_width=True)
        
        if verify_submitted:
            handle_otp_verification(email, otp, dt)
        
        if resend_submitted:
            handle_otp_resend(email)
    
    # Back to login button
    if st.button("← Back to Login"):
        reset_login_state()

def handle_credentials_verification(email, password):
    """Handle credentials verification and OTP sending"""
    if not email or not password:
        st.error("Please fill in all fields")
        return
    
    # Verify credentials
    with st.spinner("Verifying credentials..."):
        success, message, user_data = authenticate_user(email, password)
    
    if success:
        st.success(f"✅ Credentials verified for {user_data['name']}!")
        
        # Store verified user data
        st.session_state.verified_user = user_data
        st.session_state.otp_email = email
        
        # Send OTP
        with st.spinner("Sending OTP..."):
            otp_success, otp_message, otp, dt = generate_and_send_otp(
                email=email,
                recipient_name=user_data.get('name')
            )
        
        if otp_success:
            st.success("✅ OTP sent to your email")
            st.info("Please check your email for the OTP (check spam folder if not found)")
            
            # Store dt for OTP verification
            st.session_state.otp_dt = dt
            st.session_state.login_step = 'otp_verification'
            
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"❌ Failed to send OTP: {otp_message}")
    else:
        st.error(f"❌ Login failed: {message}")

def handle_otp_verification(email, otp, dt):
    """Handle OTP verification"""
    if not otp:
        st.error("Please enter the OTP")
        return
    
    if len(otp) != 6 or not otp.isdigit():
        st.error("Please enter a valid 6-digit OTP")
        return
    
    if not dt:
        st.error("Session expired. Please login again.")
        reset_login_state()
        st.rerun()
        return
    
    # Verify OTP using the dt parameter
    with st.spinner("Verifying OTP..."):
        success, message, user_data = verify_otp(email, otp, dt)
    
    if success:
        st.success(f"✅ {message}")
        
        # Use verified user data from session or from OTP verification
        verified_user = st.session_state.verified_user
        if verified_user:
            set_user_session(verified_user)
        else:
            set_user_session(user_data)
        
        # Clear login state
        reset_login_state()
        
        st.balloons()
        time.sleep(1)
        st.rerun()
    else:
        st.error(f"❌ {message}")

def handle_otp_resend(email):
    """Handle OTP resending"""
    verified_user = st.session_state.verified_user
    if not verified_user:
        st.error("Session expired. Please login again.")
        reset_login_state()
        st.rerun()
        return
    
    # Generate and send new OTP
    with st.spinner("Sending OTP..."):
        success, message, otp, dt = generate_and_send_otp(
            email=email,
            recipient_name=verified_user.get('name')
        )
    
    if success:
        st.success(f"✅ OTP sent to {email}")
        st.info("Please check your email for the OTP (check spam folder if not found)")
        
        # Update the dt for the new OTP
        st.session_state.otp_dt = dt
        
        time.sleep(1)
        st.rerun()
    else:
        st.error(f"❌ Failed to send OTP: {message}")

def reset_login_state():
    """Reset all login-related session state variables"""
    st.session_state.login_step = 'credentials'
    st.session_state.verified_user = None
    st.session_state.otp_email = ""
    st.session_state.otp_dt = ""

def render_login_status():
    """Render login status in sidebar"""
    if is_user_logged_in():
        user_data = st.session_state.get('user_data', {})
        user_name = user_data.get('name', 'User')
        user_email = user_data.get('email', '')
        
        st.sidebar.success(f"Welcome, {user_name}!")
        st.sidebar.write(f"Email: {user_email}")
        
        with st.sidebar:
            if st.button("Logout", key="sidebar_logout"):
                clear_user_session()
                st.success("Logged out successfully!")
                time.sleep(1)
                st.rerun()

def show_debug_info():
    """Show debug information (for development only)"""
    if st.checkbox("Show Debug Info"):
        st.write("**Session State Debug:**")
        st.write(f"Login Step: {st.session_state.get('login_step', 'Not set')}")
        st.write(f"OTP Email: {st.session_state.get('otp_email', 'Not set')}")
        st.write(f"OTP DT: {st.session_state.get('otp_dt', 'Not set')}")
        st.write(f"Verified User: {st.session_state.get('verified_user', 'Not set')}")
        st.write(f"User Logged In: {is_user_logged_in()}")

def main():
    """Main function to render login interface"""
    render_login_form()
    render_login_status()
    
    # Uncomment for debugging
    # show_debug_info()

if __name__ == "__main__":
    main()