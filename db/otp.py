from datetime import datetime, timezone
from .database import get_supabase_client, get_user_by_email, get_user_log_by_email_dt, update_user_log, log_user_activity
import pytz

IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    return datetime.now(IST)

def parse_datetime_string(datetime_str):
    if not datetime_str:
        return None
    
    try:
        if datetime_str.endswith('Z'):
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        elif '+' in datetime_str:
            return datetime.fromisoformat(datetime_str)
        else:
            return datetime.fromisoformat(datetime_str).replace(tzinfo=timezone.utc)
    except Exception as e:
        print(f"Error parsing datetime string '{datetime_str}': {e}")
        return None

def is_otp_expired(email, dt):
    try:
        log_entry = get_user_log_by_email_dt(email, dt)
        
        if not log_entry:
            return True
        
        otp_expiry_str = log_entry.get('otp_expiry')
        if not otp_expiry_str:
            return True
        
        otp_expiry = parse_datetime_string(otp_expiry_str)
        if not otp_expiry:
            return True
        
        now_ist = get_ist_time()
        otp_expiry_ist = otp_expiry.astimezone(IST)
        
        return now_ist >= otp_expiry_ist
        
    except Exception as e:
        print(f"Error checking OTP expiry: {e}")
        return True

def get_otp_expiry_time(email, dt):
    try:
        log_entry = get_user_log_by_email_dt(email, dt)
        
        if not log_entry:
            return None
        
        otp_expiry_str = log_entry.get('otp_expiry')
        if not otp_expiry_str:
            return None
        
        return parse_datetime_string(otp_expiry_str)
        
    except Exception as e:
        print(f"Error getting OTP expiry time: {e}")
        return None

def get_otp_times_ist(email, dt):
    try:
        log_entry = get_user_log_by_email_dt(email, dt)
        
        if not log_entry:
            return None, None
        
        last_login_str = log_entry.get('last_login')
        otp_expiry_str = log_entry.get('otp_expiry')
        
        if not last_login_str or not otp_expiry_str:
            return None, None
        
        sent_time = parse_datetime_string(last_login_str)
        expiry_time = parse_datetime_string(otp_expiry_str)
        
        if not sent_time or not expiry_time:
            return None, None
        
        sent_time_ist = sent_time.astimezone(IST)
        expiry_time_ist = expiry_time.astimezone(IST)
        
        return sent_time_ist, expiry_time_ist
        
    except Exception as e:
        print(f"Error getting OTP times: {e}")
        return None, None

def verify_otp(email, entered_otp, dt):
    try:
        user_data = get_user_by_email(email)
        if not user_data:
            return False, "User not found", None
        
        log_entry = get_user_log_by_email_dt(email, dt)
        if not log_entry:
            return False, "No OTP record found. Please request a new OTP.", None
        
        stored_otp = log_entry.get('otp')
        otp_expiry_str = log_entry.get('otp_expiry')
        
        if not stored_otp or not otp_expiry_str:
            return False, "Invalid OTP record. Please request a new OTP.", None
        
        otp_expiry = parse_datetime_string(otp_expiry_str)
        if not otp_expiry:
            return False, "Invalid OTP expiry format. Please request a new OTP.", None
        
        now_ist = get_ist_time()
        otp_expiry_ist = otp_expiry.astimezone(IST)
        
        if now_ist >= otp_expiry_ist:
            return False, "OTP has expired. Please request a new OTP.", None
        
        if stored_otp != entered_otp:
            return False, "Invalid OTP. Please check and try again.", None
        
        try:
            ist_time = get_ist_time()
            
            # Update the existing record to mark as verified instead of clearing
            update_user_log(email, {
                "password_hash": "otp_verified_success",
                "last_login": ist_time.isoformat()
                # KEEP otp and otp_expiry for audit trail
            }, dt)
            
            # Create a new log entry for successful login
            log_user_activity(
                email=email,
                activity_type="login_success",
                details={
                    "password_hash": "otp_login_complete",
                    "last_login": ist_time.isoformat(),
                    "verified_dt": dt  # Reference to the OTP verification session
                }
            )
            
        except Exception as log_error:
            print(f"Warning: Could not log OTP verification: {log_error}")
        
        return True, f"OTP verified successfully. Welcome {user_data['name']}!", user_data
        
    except Exception as e:
        return False, f"OTP verification error: {str(e)}", None

def clear_user_otp(email, dt):
    """Only use this function for manual OTP clearing, not after successful verification"""
    try:
        success, message = update_user_log(email, {
            "otp": None,
            "otp_expiry": None
        }, dt)
        
        if success:
            return True, "OTP cleared successfully"
        else:
            return False, f"Failed to clear OTP: {message}"
        
    except Exception as e:
        return False, f"Error clearing OTP: {e}"

def get_remaining_otp_time(email, dt):
    try:
        expiry_time = get_otp_expiry_time(email, dt)
        if not expiry_time:
            return 0
        
        now_ist = get_ist_time()
        expiry_time_ist = expiry_time.astimezone(IST)
        
        if now_ist >= expiry_time_ist:
            return 0
        
        return max(0, int((expiry_time_ist - now_ist).total_seconds()))
        
    except Exception as e:
        print(f"Error getting remaining OTP time: {e}")
        return 0

def cleanup_expired_otps():
    """Only clear expired OTPs, not successful ones"""
    try:
        supabase = get_supabase_client()
        
        now_ist = get_ist_time()
        
        # Only clear OTPs that are expired AND not yet verified
        supabase.table("user_logs").update({
            "otp": None,
            "otp_expiry": None
        }).lt("otp_expiry", now_ist.isoformat()).neq("password_hash", "otp_verified_success").execute()
        
        return True, "Expired OTPs cleaned up successfully"
        
    except Exception as e:
        return False, f"Error cleaning up expired OTPs: {e}"

def mark_otp_as_used(email, dt):
    """Mark OTP as used without clearing it"""
    try:
        ist_time = get_ist_time()
        success, message = update_user_log(email, {
            "password_hash": "otp_used",
            "last_login": ist_time.isoformat()
        }, dt)
        
        return success, message
        
    except Exception as e:
        return False, f"Error marking OTP as used: {e}"