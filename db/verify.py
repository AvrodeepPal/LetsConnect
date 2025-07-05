import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client
import pytz

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

load_dotenv(env_path)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    return datetime.now(IST)

def get_utc_time():
    return datetime.now(timezone.utc)

def generate_dt():
    """Generate dt in DDMMYYHHMM format"""
    now = get_ist_time()
    return now.strftime("%d%m%y%H%M")

def log_successful_login(email, dt=None):
    try:
        ist_time = get_ist_time()
        
        if not dt:
            dt = generate_dt()
        
        login_record = {
            "email": email,
            "dt": dt,
            "password_hash": "final_login_success",
            "last_login": ist_time.isoformat()
            # Do not set otp and otp_expiry to None here
        }
        
        result = supabase.table("user_logs").insert(login_record).execute()
        print(f"Final login logged successfully for {email} with dt: {dt}")
        print(f"IST time saved: {ist_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"IST time ISO: {ist_time.isoformat()}")
        return True, "Login logged successfully", dt
        
    except Exception as e:
        print(f"Error logging successful login: {e}")
        return False, f"Error logging login: {e}", None

def verify_otp(email, entered_otp, dt):
    """Verify OTP using email and dt combination"""
    try:
        from db.auth import get_user_by_email_local
        user_data = get_user_by_email_local(email)
        if not user_data:
            return False, "User not found", None
        
        # Get specific OTP record by email and dt
        response = supabase.table("user_logs").select("*").eq("email", email).eq("dt", dt).execute()
        
        if not response.data:
            return False, "No OTP record found. Please request a new OTP.", None
        
        otp_record = response.data[0]
        stored_otp = otp_record.get('otp')
        otp_expiry_str = otp_record.get('otp_expiry')
        
        if not stored_otp or not otp_expiry_str:
            return False, "Invalid OTP record. Please request a new OTP.", None
        
        # Parse OTP expiry time
        try:
            if otp_expiry_str.endswith('Z'):
                otp_expiry = datetime.fromisoformat(otp_expiry_str.replace('Z', '+00:00'))
            elif '+' in otp_expiry_str or otp_expiry_str.endswith('+00:00'):
                otp_expiry = datetime.fromisoformat(otp_expiry_str)
            else:
                otp_expiry = datetime.fromisoformat(otp_expiry_str).replace(tzinfo=timezone.utc)
        except Exception as parse_error:
            print(f"Error parsing OTP expiry: {parse_error}")
            return False, "Invalid OTP expiry format. Please request a new OTP.", None
        
        # Check if OTP is expired
        now_ist = get_ist_time()
        otp_expiry_ist = otp_expiry.astimezone(IST)
        
        if now_ist >= otp_expiry_ist:
            return False, "OTP has expired. Please request a new OTP.", None
        
        # Check if OTP matches
        if stored_otp != entered_otp:
            return False, "Invalid OTP. Please check and try again.", None
        
        # OTP is valid, update the record to mark as verified
        try:
            ist_time = get_ist_time()
            
            # Update the existing record to mark as verified, keep OTP data
            supabase.table("user_logs").update({
                "password_hash": "otp_verified_success",
                "last_login": ist_time.isoformat()
                # Keep otp and otp_expiry for audit trail
            }).eq("email", email).eq("dt", dt).execute()
            
            # Create a new log entry for final successful login
            success, message, login_dt = log_successful_login(email)
            
        except Exception as log_error:
            print(f"Warning: Could not log successful login: {log_error}")
        
        # Get user data from coord_details table
        coord_response = supabase.table("coord_details").select("*").eq("email", email).execute()
        if coord_response.data:
            coord_data = coord_response.data[0]
            user_data = {
                'id': coord_data['id'],
                'name': coord_data['name'],
                'email': coord_data['email'],
                'phone': coord_data.get('phone'),
                'roll_number': coord_data['roll_number']
            }
        
        return True, f"OTP verified successfully. Welcome {user_data['name']}!", user_data
        
    except Exception as e:
        return False, f"Verification error: {str(e)}", None

def is_otp_valid(email, dt):
    """Check if OTP is valid for specific email and dt combination"""
    try:
        response = supabase.table("user_logs").select("otp, otp_expiry, password_hash").eq("email", email).eq("dt", dt).execute()
        
        if not response.data:
            return False, 0
        
        otp_data = response.data[0]
        otp = otp_data.get('otp')
        otp_expiry_str = otp_data.get('otp_expiry')
        password_hash = otp_data.get('password_hash')
        
        # If already verified, consider it invalid for new attempts
        if password_hash == "otp_verified_success":
            return False, 0
        
        if not otp or not otp_expiry_str:
            return False, 0
        
        try:
            if otp_expiry_str.endswith('Z'):
                otp_expiry = datetime.fromisoformat(otp_expiry_str.replace('Z', '+00:00'))
            elif '+' in otp_expiry_str or otp_expiry_str.endswith('+00:00'):
                otp_expiry = datetime.fromisoformat(otp_expiry_str)
            else:
                otp_expiry = datetime.fromisoformat(otp_expiry_str).replace(tzinfo=timezone.utc)
        except Exception as parse_error:
            print(f"Error parsing OTP expiry: {parse_error}")
            return False, 0
        
        now_ist = get_ist_time()
        otp_expiry_ist = otp_expiry.astimezone(IST)
        
        if now_ist < otp_expiry_ist:
            remaining_seconds = int((otp_expiry_ist - now_ist).total_seconds())
            return True, remaining_seconds
        else:
            return False, 0
            
    except Exception as e:
        print(f"Error checking OTP validity: {e}")
        return False, 0

def clear_expired_otps():
    """Clear only expired OTPs that haven't been verified"""
    try:
        now_ist = get_ist_time()
        
        # Only clear OTPs that are expired AND not verified
        supabase.table("user_logs").update({
            "otp": None,
            "otp_expiry": None
        }).lt("otp_expiry", now_ist.isoformat()).neq("password_hash", "otp_verified_success").execute()
        
        return True, "Expired OTPs cleared successfully"
        
    except Exception as e:
        return False, f"Error clearing expired OTPs: {e}"

def revoke_otp(email, dt):
    """Revoke OTP for specific email and dt combination"""
    try:
        supabase.table("user_logs").update({
            "otp": None,
            "otp_expiry": None,
            "password_hash": "otp_revoked"
        }).eq("email", email).eq("dt", dt).execute()
        
        return True, "OTP revoked successfully"
        
    except Exception as e:
        return False, f"Error revoking OTP: {e}"

def get_otp_info(email, dt):
    """Get OTP information for specific email and dt combination"""
    try:
        response = supabase.table("user_logs").select("*").eq("email", email).eq("dt", dt).execute()
        
        if not response.data:
            return None
        
        return response.data[0]
        
    except Exception as e:
        print(f"Error getting OTP info: {e}")
        return None

def get_verified_otp_records(email):
    """Get all verified OTP records for audit purposes"""
    try:
        response = supabase.table("user_logs").select("*").eq("email", email).eq("password_hash", "otp_verified_success").execute()
        return response.data
        
    except Exception as e:
        print(f"Error getting verified OTP records: {e}")
        return []