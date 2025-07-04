import streamlit as st
import psycopg2
import os
import smtplib
import random
import string
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

# Load environment variables from the correct path
load_dotenv(env_path, override=True)

DB_URL = os.getenv("SUPABASE_DB_URL")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def generate_otp():
    """
    Generate a 6-digit numeric OTP
    Returns: str
    """
    return ''.join(random.choices(string.digits, k=6))

def store_otp_in_db(email, roll_number, otp):
    """
    Store OTP and expiry time in user_logs table
    Returns: (success: bool, message: str)
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Calculate expiry time (5 minutes from now)
        otp_expiry = datetime.now() + timedelta(minutes=5)
        
        # Check if user already has an entry in user_logs
        cursor.execute("""
            SELECT id FROM user_logs 
            WHERE email = %s AND roll_number = %s
            ORDER BY last_login DESC
            LIMIT 1;
        """, (email, roll_number))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing record
            cursor.execute("""
                UPDATE user_logs 
                SET otp = %s, otp_expiry = %s, last_login = %s
                WHERE email = %s AND roll_number = %s;
            """, (otp, otp_expiry, datetime.now(), email, roll_number))
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO user_logs (email, roll_number, password_hash, last_login, otp, otp_expiry)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (email, roll_number, 'otp_login', datetime.now(), otp, otp_expiry))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, "OTP stored successfully"
        
    except Exception as e:
        return False, f"Database error: {e}"

def send_otp_email(email, otp):
    """
    Send OTP via Gmail SMTP
    Returns: (success: bool, message: str)
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = "Your OTP for Coordinator Login"
        
        # Email body
        body = f"""Dear User,

Your One-Time Password (OTP) for login is: {otp}

This OTP is valid for 5 minutes.

Regards,
Let's Connect Team"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Setup Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, email, text)
        server.quit()
        
        return True, "OTP sent successfully"
        
    except Exception as e:
        return False, f"Email error: {e}"

def generate_and_send_otp(email, roll_number):
    """
    Generate OTP, store in DB, and send via email
    Returns: (success: bool, message: str)
    """
    # Generate OTP
    otp = generate_otp()
    
    # Store in database
    db_success, db_message = store_otp_in_db(email, roll_number, otp)
    if not db_success:
        return False, db_message
    
    # Send via email
    email_success, email_message = send_otp_email(email, otp)
    if not email_success:
        return False, email_message
    
    return True, "OTP generated and sent successfully"

def get_remaining_time(email, roll_number):
    """
    Get remaining time for OTP validity
    Returns: (remaining_seconds: int, expired: bool)
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT otp_expiry FROM user_logs 
            WHERE email = %s AND roll_number = %s
            ORDER BY last_login DESC
            LIMIT 1;
        """, (email, roll_number))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            otp_expiry = result[0]
            now = datetime.now()
            
            if now < otp_expiry:
                remaining_seconds = int((otp_expiry - now).total_seconds())
                return remaining_seconds, False
            else:
                return 0, True
        
        return 0, True
        
    except Exception as e:
        return 0, True

def format_time(seconds):
    """
    Format seconds into minutes and seconds
    Returns: str
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes} minutes {seconds} seconds"

def render_otp_page(email, roll_number):
    """
    Render OTP entry page with countdown timer
    Returns: bool (True if OTP verified successfully)
    """
    st.title("🔐 OTP Verification")
    st.markdown("*Please check your email and enter the OTP below*")
    
    # Simple refresh mechanism using button
    if st.button("🔄 Refresh Timer", key="refresh_timer"):
        st.rerun()
    
    # Get remaining time
    remaining_seconds, expired = get_remaining_time(email, roll_number)
    
    if expired:
        st.error("⏰ OTP has expired!")
        st.markdown("**Please request a new OTP to continue.**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Resend OTP", use_container_width=True):
                with st.spinner("Generating new OTP..."):
                    success, message = generate_and_send_otp(email, roll_number)
                
                if success:
                    st.success("✅ New OTP sent to your email!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to send OTP: {message}")
        
        with col2:
            if st.button("⬅️ Back to Login", use_container_width=True):
                # Clear OTP session state
                for key in ['otp_stage', 'otp_email', 'otp_roll']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        return False
    
    # Show countdown timer
    st.info(f"⏱️ OTP expires in: **{format_time(remaining_seconds)}**")
    st.caption("Click 'Refresh Timer' to update the countdown")
    
    # OTP entry form
    with st.form("otp_form"):
        st.subheader("Enter OTP")
        
        entered_otp = st.text_input(
            "6-Digit OTP",
            type="password",
            placeholder="Enter the OTP from your email",
            help="Check your email for the 6-digit OTP",
            max_chars=6
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            verify_button = st.form_submit_button("✅ Verify OTP", use_container_width=True)
        
        with col2:
            resend_button = st.form_submit_button("🔄 Resend OTP", use_container_width=True)
        
        if verify_button:
            if not entered_otp:
                st.error("Please enter the OTP")
                return False
            
            if len(entered_otp) != 6:
                st.error("OTP must be 6 digits")
                return False
            
            # Import and use verify function
            from db.verify import verify_otp
            
            success, message, user_data = verify_otp(email, roll_number, entered_otp)
            
            if success:
                st.success(f"✅ {message}")
                
                # Set session state for successful login
                st.session_state["logged_in"] = True
                st.session_state["user_data"] = user_data
                st.session_state["user_email"] = user_data['email']
                st.session_state["user_name"] = user_data['name']
                st.session_state["user_roll"] = user_data['roll_number']
                
                # Clear OTP session state
                for key in ['otp_stage', 'otp_email', 'otp_roll']:
                    if key in st.session_state:
                        del st.session_state[key]
                
                # Redirect to main app
                st.rerun()
                return True
            else:
                st.error(f"❌ {message}")
                return False
        
        if resend_button:
            with st.spinner("Sending new OTP..."):
                success, message = generate_and_send_otp(email, roll_number)
            
            if success:
                st.success("✅ New OTP sent to your email!")
                st.rerun()
            else:
                st.error(f"❌ Failed to send OTP: {message}")
    
    # Help section
    st.divider()
    
    with st.expander("ℹ️ Need Help?"):
        st.markdown(f"""
        **OTP sent to:** {email}
        
        **Troubleshooting:**
        - Check your spam/junk folder
        - Make sure you're entering the most recent OTP
        - OTP is valid for 5 minutes only
        - Use the "Resend OTP" button if expired
        - Click "Refresh Timer" to update the countdown
        
        **Security Note:** Each OTP can only be used once and expires automatically.
        """)
    
    return False