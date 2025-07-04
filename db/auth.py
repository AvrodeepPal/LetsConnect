import os
from dotenv import load_dotenv
import bcrypt  # Fixed import
from datetime import datetime, timezone, timedelta
import random
import string
from supabase import create_client, Client

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

# Load environment variables from the correct path
load_dotenv(env_path)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def verify_user(email, password):
    """
    Verify user credentials against coord_details table
    Returns: (success: bool, message: str, user_data: dict or None)
    """
    try:
        # Fetch user data for the given email
        response = supabase.table("coord_details").select("*").eq("email", email).execute()
        
        if not response.data:
            return False, "Invalid credentials - user not found", None
        
        user = response.data[0]
        
        # Compare entered password with stored hash
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            user_data = {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'roll_number': user['roll_number']
            }
            return True, "Login successful", user_data
        else:
            return False, "Invalid credentials - incorrect password", None
            
    except Exception as e:
        return False, f"Database error: {e}", None

def log_user_session(user_id, email):
    """
    Log user session to user_logs table
    Returns: (success: bool, message: str)
    """
    try:
        # Generate random OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Set expiry 5 minutes in the future
        otp_expiry_time = datetime.now(timezone.utc) + timedelta(minutes=5)
        
        # Insert login record
        supabase.table("user_logs").insert({
            "email": email,
            "password_hash": "logged_in",
            "last_login": datetime.now(timezone.utc).isoformat(),
            "otp": otp,
            "otp_expiry": otp_expiry_time.isoformat()
        }).execute()
        
        return True, "Session logged successfully"
        
    except Exception as e:
        return False, f"Failed to log session: {e}"

def get_user_by_email(email):
    """
    Get user data by email for session management
    Returns: user_data dict or None
    """
    try:
        response = supabase.table("coord_details").select("*").eq("email", email).execute()
        
        if response.data:
            user = response.data[0]
            return {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'roll_number': user['roll_number']
            }
        return None
        
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None