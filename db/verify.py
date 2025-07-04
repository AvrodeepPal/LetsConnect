import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import pytz

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

# Load environment variables from the correct path
load_dotenv(env_path)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# IST timezone
IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    """Get current time in IST"""
    return datetime.now(IST)

def get_utc_time():
    """Get current time in UTC"""
    return datetime.now(timezone.utc)

def log_successful_login(email):
    """
    Log a successful login to the user_logs table with IST time
    """
    try:
        # Get current IST time
        ist_time = get_ist_time()
        
        login_record = {
            "email": email,
            "password_hash": "successful_login",
            "last_login": ist_time.isoformat(),  # Store IST time directly
            "otp": None,
            "otp_expiry": None
        }
        
        result = supabase.table("user_logs").insert(login_record).execute()
        print(f"Login logged successfully for {email}")
        print(f"IST time saved: {ist_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"IST time ISO: {ist_time.isoformat()}")
        return True, "Login logged successfully"
        
    except Exception as e:
        print(f"Error logging successful login: {e}")
        return False, f"Error logging login: {e}"

def verify_otp(email, entered_otp):
    """
    Verify OTP against database and check expiry
    Returns: (success: bool, message: str, user_data: dict or None)
    """
    try:
        # Get user data from coord_details table
        from db.auth import get_user_by_email
        user_data = get_user_by_email(email)
        if not user_data:
            return False, "User not found", None
        
        # Get the latest OTP record for this user
        response = supabase.table("user_logs").select("*").eq("email", email).order("last_login", desc=True).limit(1).execute()
        
        if not response.data:
            return False, "No OTP record found. Please request a new OTP.", None
        
        otp_record = response.data[0]
        stored_otp = otp_record.get('otp')
        otp_expiry_str = otp_record.get('otp_expiry')
        
        if not stored_otp or not otp_expiry_str:
            return False, "Invalid OTP record. Please request a new OTP.", None
        
        # Parse expiry time properly
        try:
            # Handle different datetime formats
            if otp_expiry_str.endswith('Z'):
                otp_expiry = datetime.fromisoformat(otp_expiry_str.replace('Z', '+00:00'))
            elif '+' in otp_expiry_str or otp_expiry_str.endswith('+00:00'):
                otp_expiry = datetime.fromisoformat(otp_expiry_str)
            else:
                # Assume UTC if no timezone info
                otp_expiry = datetime.fromisoformat(otp_expiry_str).replace(tzinfo=timezone.utc)
        except:
            return False, "Invalid OTP expiry format. Please request a new OTP.", None
        
        # Check if OTP has expired
        now_utc = get_utc_time()
        
        if now_utc > otp_expiry:
            return False, "OTP has expired. Please request a new OTP.", None
        
        # Verify OTP
        if stored_otp != entered_otp:
            return False, "Invalid OTP. Please check and try again.", None
        
        # OTP is valid - Log successful login
        try:
            # Log the successful login
            log_successful_login(email)
            
            # Clear the OTP from the previous record to prevent reuse
            supabase.table("user_logs").update({
                "otp": None,
                "otp_expiry": None
            }).eq("id", otp_record["id"]).execute()
            
        except Exception as log_error:
            print(f"Warning: Could not log successful login: {log_error}")
            # Continue with login even if logging fails
        
        # Get additional user data from coord_details
        coord_response = supabase.table("coord_details").select("*").eq("email", email).execute()
        if coord_response.data:
            coord_data = coord_response.data[0]
            user_data = {
                'id': coord_data['id'],
                'name': coord_data['name'],
                'email': coord_data['email'],
                'roll_number': coord_data['roll_number']
            }
        
        return True, f"OTP verified successfully. Welcome {user_data['name']}!", user_data
        
    except Exception as e:
        return False, f"Verification error: {str(e)}", None

def is_otp_valid(email):
    """
    Check if there's a valid (non-expired) OTP for the given email
    Returns: (valid: bool, remaining_seconds: int)
    """
    try:
        # Get the latest OTP record
        response = supabase.table("user_logs").select("otp_expiry").eq("email", email).order("last_login", desc=True).limit(1).execute()
        
        if not response.data:
            return False, 0
        
        otp_expiry_str = response.data[0].get('otp_expiry')
        if not otp_expiry_str:
            return False, 0
        
        # Parse expiry time
        try:
            if otp_expiry_str.endswith('Z'):
                otp_expiry = datetime.fromisoformat(otp_expiry_str.replace('Z', '+00:00'))
            elif '+' in otp_expiry_str or otp_expiry_str.endswith('+00:00'):
                otp_expiry = datetime.fromisoformat(otp_expiry_str)
            else:
                otp_expiry = datetime.fromisoformat(otp_expiry_str).replace(tzinfo=timezone.utc)
        except:
            return False, 0
        
        # Check expiry
        now_utc = get_utc_time()
        
        if now_utc < otp_expiry:
            remaining_seconds = int((otp_expiry - now_utc).total_seconds())
            return True, remaining_seconds
        else:
            return False, 0
            
    except Exception as e:
        print(f"Error checking OTP validity: {e}")
        return False, 0

def clear_expired_otps():
    """Clear all expired OTPs from the database"""
    try:
        now_utc = get_utc_time().isoformat()
        
        # Clear expired OTPs
        supabase.table("user_logs").update({
            "otp": None,
            "otp_expiry": None
        }).lt("otp_expiry", now_utc).execute()
        
        return True, "Expired OTPs cleared successfully"
        
    except Exception as e:
        return False, f"Error clearing expired OTPs: {e}"

def revoke_otp(email):
    """Revoke/clear OTP for a specific user"""
    try:
        # Clear OTP for this user
        supabase.table("user_logs").update({
            "otp": None,
            "otp_expiry": None
        }).eq("email", email).execute()
        
        return True, "OTP revoked successfully"
        
    except Exception as e:
        return False, f"Error revoking OTP: {e}"