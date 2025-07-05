import random
import string
from datetime import datetime, timedelta
from .email_sender import send_email
from db.database import get_supabase_client
import os
from dotenv import load_dotenv
import pytz

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    return datetime.now(IST)

def generate_dt():
    """Generate dt in DDMMYYHHMM format"""
    now = get_ist_time()
    return now.strftime("%d%m%y%H%M")

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def create_otp_email_body(otp, recipient_name=None):
    greeting = f"Dear {recipient_name}," if recipient_name else "Dear User,"
    
    return f"""{greeting}

Your One-Time Password (OTP) for login is: {otp}

This OTP is valid for 5 minutes.

Please do not share this OTP with anyone.

Regards,
Let's Connect Team"""

def store_otp_in_database(email, otp, dt, expiry_minutes=5):
    try:
        supabase = get_supabase_client()
        
        now_ist = get_ist_time()
        otp_expiry_ist = now_ist + timedelta(minutes=expiry_minutes)
        
        # Check if entry with same email and dt exists
        response = supabase.table("user_logs").select("*").eq("email", email).eq("dt", dt).execute()
        
        if response.data:
            # Update existing entry
            supabase.table("user_logs").update({
                "otp": otp,
                "otp_expiry": otp_expiry_ist.isoformat(),
                "last_login": now_ist.isoformat()
            }).eq("email", email).eq("dt", dt).execute()
        else:
            # Insert new entry
            supabase.table("user_logs").insert({
                "email": email,
                "dt": dt,
                "password_hash": "otp_login",
                "last_login": now_ist.isoformat(),
                "otp": otp,
                "otp_expiry": otp_expiry_ist.isoformat()
            }).execute()
        
        return True, "OTP stored successfully", dt
        
    except Exception as e:
        return False, f"Database error: {e}", None

def send_otp_email(email, otp, recipient_name=None):
    try:
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            return False, "Email configuration not found"
        
        subject = "Your OTP for Coordinator Login"
        body = create_otp_email_body(otp, recipient_name)
        
        success, message = send_email(
            sender_email=EMAIL_ADDRESS,
            sender_password=EMAIL_PASSWORD,
            recipient_email=email,
            subject=subject,
            body=body
        )
        
        return success, message
        
    except Exception as e:
        return False, f"Email sending error: {e}"

def generate_and_send_otp(email, recipient_name=None, expiry_minutes=5):
    try:
        otp = generate_otp()
        dt = generate_dt()
        
        db_success, db_message, stored_dt = store_otp_in_database(email, otp, dt, expiry_minutes)
        if not db_success:
            return False, db_message, None, None
        
        email_success, email_message = send_otp_email(email, otp, recipient_name)
        if not email_success:
            return False, email_message, None, None
        
        return True, "OTP generated and sent successfully", otp, stored_dt
        
    except Exception as e:
        return False, f"OTP generation/sending error: {e}", None, None

def resend_otp(email, recipient_name=None):
    return generate_and_send_otp(email, recipient_name)

def get_otp_status(email, dt):
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("user_logs").select("otp, otp_expiry").eq("email", email).eq("dt", dt).execute()
        
        if not response.data:
            return {
                'has_otp': False,
                'is_expired': True,
                'expires_at': None,
                'time_remaining': None
            }
        
        otp_data = response.data[0]
        otp = otp_data.get('otp')
        otp_expiry_str = otp_data.get('otp_expiry')
        
        if not otp or not otp_expiry_str:
            return {
                'has_otp': False,
                'is_expired': True,
                'expires_at': None,
                'time_remaining': None
            }
        
        try:
            if otp_expiry_str.endswith('Z'):
                otp_expiry = datetime.fromisoformat(otp_expiry_str.replace('Z', '+00:00'))
            elif '+' in otp_expiry_str:
                otp_expiry = datetime.fromisoformat(otp_expiry_str)
            else:
                otp_expiry = datetime.fromisoformat(otp_expiry_str)
        except:
            return {
                'has_otp': False,
                'is_expired': True,
                'expires_at': None,
                'time_remaining': None
            }
        
        now_ist = get_ist_time()
        otp_expiry_ist = otp_expiry.astimezone(IST) if otp_expiry.tzinfo else otp_expiry.replace(tzinfo=IST)
        
        is_expired = now_ist >= otp_expiry_ist
        time_remaining = max(0, int((otp_expiry_ist - now_ist).total_seconds())) if not is_expired else 0
        
        return {
            'has_otp': True,
            'is_expired': is_expired,
            'expires_at': otp_expiry_ist,
            'time_remaining': time_remaining
        }
        
    except Exception as e:
        print(f"Error getting OTP status: {e}")
        return {
            'has_otp': False,
            'is_expired': True,
            'expires_at': None,
            'time_remaining': None
        }

def clear_user_otp(email, dt):
    try:
        supabase = get_supabase_client()
        
        supabase.table("user_logs").update({
            "otp": None,
            "otp_expiry": None
        }).eq("email", email).eq("dt", dt).execute()
        
        return True, "OTP cleared successfully"
        
    except Exception as e:
        return False, f"Error clearing OTP: {e}"

def cleanup_expired_otps():
    try:
        supabase = get_supabase_client()
        
        now_ist = get_ist_time()
        
        supabase.table("user_logs").update({
            "otp": None,
            "otp_expiry": None
        }).lt("otp_expiry", now_ist.isoformat()).execute()
        
        return True, "Expired OTPs cleaned up successfully"
        
    except Exception as e:
        return False, f"Error cleaning up expired OTPs: {e}"