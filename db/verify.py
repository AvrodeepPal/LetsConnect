import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv
from db.auth import get_user_by_email

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

# Load environment variables from the correct path
load_dotenv(env_path)

DB_URL = os.getenv("SUPABASE_DB_URL")

def verify_otp(email, roll_number, entered_otp):
    """
    Verify the entered OTP against stored OTP and check expiry
    Returns: (success: bool, message: str, user_data: dict or None)
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Fetch the latest OTP and expiry for this user
        cursor.execute("""
            SELECT otp, otp_expiry 
            FROM user_logs 
            WHERE email = %s AND roll_number = %s
            ORDER BY last_login DESC
            LIMIT 1;
        """, (email, roll_number))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result is None:
            return False, "No OTP found for this user", None
        
        stored_otp, otp_expiry = result
        
        # Check if OTP has expired
        if datetime.now() > otp_expiry:
            return False, "OTP has expired. Please request a new one.", None
        
        # Check if OTP matches
        if entered_otp.strip() != stored_otp.strip():
            # Log failed attempt
            log_failed_attempt(email, roll_number, entered_otp)
            return False, "Invalid OTP. Please check and try again.", None
        
        # OTP is valid, get user data
        user_data = get_user_by_email(email)
        
        if user_data is None:
            return False, "User data not found", None
        
        # Mark OTP as used (optional - you can implement this)
        mark_otp_as_used(email, roll_number)
        
        return True, "OTP verified successfully", user_data
        
    except Exception as e:
        return False, f"Verification error: {e}", None

def log_failed_attempt(email, roll_number, entered_otp):
    """
    Log failed OTP attempts for security purposes
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # You can create a separate table for failed attempts or update user_logs
        # For now, we'll just update the last_login timestamp to track activity
        cursor.execute("""
            UPDATE user_logs 
            SET last_login = %s 
            WHERE email = %s AND roll_number = %s;
        """, (datetime.now(), email, roll_number))
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Failed to log failed attempt: {e}")

def mark_otp_as_used(email, roll_number):
    """
    Mark OTP as used by clearing it from the database
    This prevents OTP reuse attacks
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Clear the OTP after successful verification
        cursor.execute("""
            UPDATE user_logs 
            SET otp = NULL, otp_expiry = NULL 
            WHERE email = %s AND roll_number = %s;
        """, (email, roll_number))
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Failed to mark OTP as used: {e}")

def get_otp_status(email, roll_number):
    """
    Get OTP status for a user
    Returns: (has_valid_otp: bool, otp_expiry: datetime or None)
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT otp, otp_expiry 
            FROM user_logs 
            WHERE email = %s AND roll_number = %s
            ORDER BY last_login DESC
            LIMIT 1;
        """, (email, roll_number))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            otp, otp_expiry = result
            
            # Check if OTP exists and is not expired
            if otp and otp_expiry and datetime.now() < otp_expiry:
                return True, otp_expiry
        
        return False, None
        
    except Exception as e:
        print(f"Error checking OTP status: {e}")
        return False, None

def cleanup_expired_otps():
    """
    Clean up expired OTPs from the database
    This can be called periodically or as part of a cleanup job
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Clear expired OTPs
        cursor.execute("""
            UPDATE user_logs 
            SET otp = NULL, otp_expiry = NULL 
            WHERE otp_expiry < %s;
        """, (datetime.now(),))
        
        rows_affected = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Cleaned up {rows_affected} expired OTPs")
        
    except Exception as e:
        print(f"Failed to cleanup expired OTPs: {e}")

def resend_otp_allowed(email, roll_number, cooldown_minutes=1):
    """
    Check if user is allowed to resend OTP (rate limiting)
    Returns: (allowed: bool, message: str)
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT last_login 
            FROM user_logs 
            WHERE email = %s AND roll_number = %s
            ORDER BY last_login DESC
            LIMIT 1;
        """, (email, roll_number))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            last_login = result[0]
            time_since_last = datetime.now() - last_login
            
            if time_since_last.total_seconds() < cooldown_minutes * 60:
                remaining_seconds = cooldown_minutes * 60 - time_since_last.total_seconds()
                return False, f"Please wait {int(remaining_seconds)} seconds before requesting a new OTP"
        
        return True, "Resend allowed"
        
    except Exception as e:
        return False, f"Error checking resend status: {e}"