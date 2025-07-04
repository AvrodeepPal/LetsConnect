import streamlit as st
import os
import smtplib
import random
import string
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from supabase import create_client, Client
import pytz

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

# Load environment variables from the correct path
load_dotenv(env_path, override=True)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# IST timezone
IST = pytz.timezone('Asia/Kolkata')

def generate_otp():
    """Generate a 6-digit numeric OTP"""
    return ''.join(random.choices(string.digits, k=6))

def get_ist_time():
    """Get current time in IST"""
    return datetime.now(IST)

def store_otp_in_db(email, otp):
    """Store OTP and expiry time in user_logs table"""
    try:
        # Calculate times in UTC for database storage
        now_utc = datetime.now(timezone.utc)
        otp_expiry_utc = now_utc + timedelta(minutes=5)
        
        # Check if user already has an entry
        response = supabase.table("user_logs").select("*").eq("email", email).order("last_login", desc=True).limit(1).execute()
        
        if response.data:
            # Update existing record
            supabase.table("user_logs").update({
                "otp": otp,
                "otp_expiry": otp_expiry_utc.isoformat(),
                "last_login": now_utc.isoformat()
            }).eq("email", email).execute()
        else:
            # Insert new record
            supabase.table("user_logs").insert({
                "email": email,
                "password_hash": "otp_login",
                "last_login": now_utc.isoformat(),
                "otp": otp,
                "otp_expiry": otp_expiry_utc.isoformat()
            }).execute()
        
        return True, "OTP stored successfully"
        
    except Exception as e:
        return False, f"Database error: {e}"

def send_otp_email(email, otp):
    """Send OTP via Gmail SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = "Your OTP for Coordinator Login"
        
        body = f"""Dear User,

Your One-Time Password (OTP) for login is: {otp}

This OTP is valid for 5 minutes.

Regards,
Let's Connect Team"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
        server.quit()
        
        return True, "OTP sent successfully"
        
    except Exception as e:
        return False, f"Email error: {e}"

def generate_and_send_otp(email):
    """Generate OTP, store in DB, and send via email"""
    otp = generate_otp()
    
    # Store in database
    db_success, db_message = store_otp_in_db(email, otp)
    if not db_success:
        return False, db_message
    
    # Send via email
    email_success, email_message = send_otp_email(email, otp)
    if not email_success:
        return False, email_message
    
    return True, "OTP generated and sent successfully"

def get_otp_times(email):
    """Get OTP sent and expiry times in IST"""
    try:
        response = supabase.table("user_logs").select("last_login, otp_expiry").eq("email", email).order("last_login", desc=True).limit(1).execute()
        
        if response.data:
            last_login_str = response.data[0]['last_login']
            otp_expiry_str = response.data[0]['otp_expiry']
            
            if last_login_str and otp_expiry_str:
                try:
                    # Parse sent time
                    if last_login_str.endswith('Z'):
                        sent_time_utc = datetime.fromisoformat(last_login_str.replace('Z', '+00:00'))
                    elif '+' in last_login_str:
                        sent_time_utc = datetime.fromisoformat(last_login_str)
                    else:
                        sent_time_utc = datetime.fromisoformat(last_login_str).replace(tzinfo=timezone.utc)
                    
                    # Parse expiry time
                    if otp_expiry_str.endswith('Z'):
                        expiry_time_utc = datetime.fromisoformat(otp_expiry_str.replace('Z', '+00:00'))
                    elif '+' in otp_expiry_str:
                        expiry_time_utc = datetime.fromisoformat(otp_expiry_str)
                    else:
                        expiry_time_utc = datetime.fromisoformat(otp_expiry_str).replace(tzinfo=timezone.utc)
                    
                    # Convert to IST
                    sent_time_ist = sent_time_utc.astimezone(IST)
                    expiry_time_ist = expiry_time_utc.astimezone(IST)
                    
                    return sent_time_ist, expiry_time_ist
                except Exception as parse_error:
                    print(f"Error parsing OTP times: {parse_error}")
                    return None, None
        
        return None, None
        
    except Exception as e:
        print(f"Error getting OTP times: {e}")
        return None, None

def is_otp_expired(email):
    """Check if OTP is expired"""
    try:
        response = supabase.table("user_logs").select("otp_expiry").eq("email", email).order("last_login", desc=True).limit(1).execute()
        
        if response.data:
            otp_expiry_str = response.data[0]['otp_expiry']
            if otp_expiry_str:
                # Parse expiry time with proper timezone handling
                try:
                    if otp_expiry_str.endswith('Z'):
                        otp_expiry_utc = datetime.fromisoformat(otp_expiry_str.replace('Z', '+00:00'))
                    elif '+' in otp_expiry_str:
                        otp_expiry_utc = datetime.fromisoformat(otp_expiry_str)
                    else:
                        # Assume UTC if no timezone info
                        otp_expiry_utc = datetime.fromisoformat(otp_expiry_str).replace(tzinfo=timezone.utc)
                    
                    now_utc = datetime.now(timezone.utc)
                    return now_utc > otp_expiry_utc
                except Exception as parse_error:
                    print(f"Error parsing OTP expiry time: {parse_error}")
                    return True
        
        return True  # No OTP found, consider expired
        
    except Exception as e:
        print(f"Error checking OTP expiry: {e}")
        return True

def render_otp_page(email):
    """Render OTP entry page with sent/expiry times"""
    st.title("🔐 OTP Verification")
    st.markdown("*Please check your email and enter the OTP below*")
    
    # Get OTP times
    sent_time, expiry_time = get_otp_times(email)
    
    if sent_time and expiry_time:
        st.info(f"📧 **OTP Sent at:** {sent_time.strftime('%I:%M %p IST')}")
        st.info(f"⏰ **OTP Expires at:** {expiry_time.strftime('%I:%M %p IST')}")
    
    # Check if OTP is expired
    if is_otp_expired(email):
        st.error("⏰ **OTP has expired!**")
        st.warning("**New OTP sent automatically.**")
        
        # Automatically generate new OTP
        with st.spinner("Generating new OTP..."):
            success, message = generate_and_send_otp(email)
        
        if success:
            st.success("✅ **New OTP sent to your email!**")
            st.rerun()
        else:
            st.error(f"❌ Failed to send OTP: {message}")
        
        return False
    
    # OTP entry form
    with st.form("otp_form"):
        st.subheader("Enter OTP")
        
        entered_otp = st.text_input(
            "6-Digit OTP",
            type="password",
            placeholder="Enter the OTP from your email",
            max_chars=6
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            verify_button = st.form_submit_button("✅ Verify OTP", use_container_width=True)
        
        with col2:
            resend_button = st.form_submit_button("🔄 Resend OTP", use_container_width=True)
        
        if verify_button:
            if not entered_otp or len(entered_otp) != 6:
                st.error("Please enter a valid 6-digit OTP")
                return False
            
            # Check expiry again before verification
            if is_otp_expired(email):
                st.error("⏰ **OTP has expired! New OTP sent.**")
                
                # Generate new OTP
                with st.spinner("Generating new OTP..."):
                    success, message = generate_and_send_otp(email)
                
                if success:
                    st.success("✅ **New OTP sent to your email!**")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to send OTP: {message}")
                
                return False
            
            # Verify OTP
            from db.verify import verify_otp
            success, message, user_data = verify_otp(email, entered_otp)
            
            if success:
                st.success(f"✅ {message}")
                
                # Set session state for successful login
                st.session_state["logged_in"] = True
                st.session_state["user_data"] = user_data
                st.session_state["user_email"] = user_data['email']
                st.session_state["user_name"] = user_data['name']
                st.session_state["user_roll"] = user_data['roll_number']
                
                # Clear OTP session state
                for key in ['otp_stage', 'otp_email', 'temp_user_data']:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.rerun()
                return True
            else:
                st.error(f"❌ {message}")
                return False
        
        if resend_button:
            with st.spinner("Sending new OTP..."):
                success, message = generate_and_send_otp(email)
            
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
        - New OTP will be sent automatically if expired
        """)
    
    return False