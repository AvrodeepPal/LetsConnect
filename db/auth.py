import psycopg2
import os
from dotenv import load_dotenv
from passlib.hash import bcrypt
from datetime import datetime
import random
import string

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

# Load environment variables from the correct path
load_dotenv(env_path)

DB_URL = os.getenv("SUPABASE_DB_URL")

def verify_user(email, roll_number, password):
    """
    Verify user credentials against coord_details table
    Returns: (success: bool, message: str, user_data: dict or None)
    """
    try:
        # Connect to Supabase Postgres
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Fetch user data for the given email and roll number
        cursor.execute("""
            SELECT id, name, email, phone, roll_number, password_hash 
            FROM coord_details 
            WHERE email = %s AND roll_number = %s;
        """, (email, roll_number))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result is None:
            return False, "Invalid credentials - user not found", None
        
        user_id, name, email, phone, roll_number, stored_hash = result
        
        # Compare entered password with stored hash
        if bcrypt.verify(password, stored_hash):
            user_data = {
                'id': user_id,
                'name': name,
                'email': email,
                'phone': phone,
                'roll_number': roll_number
            }
            return True, "Login successful", user_data
        else:
            return False, "Invalid credentials - incorrect password", None
            
    except Exception as e:
        return False, f"Database error: {e}", None

def log_user_session(user_id, email, roll_number):
    """
    Log user session to user_logs table
    Returns: (success: bool, message: str)
    """
    try:
        # Connect to Supabase Postgres
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Generate random OTP (you mentioned you'll fix this later)
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Insert login record
        cursor.execute("""
            INSERT INTO user_logs (email, roll_number, password_hash, last_login, otp, otp_expiry)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (
            email,
            roll_number,
            'logged_in',  # Placeholder hash for login record
            datetime.now(),
            otp,
            datetime.now()  # You can adjust OTP expiry logic later
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, "Session logged successfully"
        
    except Exception as e:
        return False, f"Failed to log session: {e}"

def get_user_by_email(email):
    """
    Get user data by email for session management
    Returns: user_data dict or None
    """
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, email, phone, roll_number 
            FROM coord_details 
            WHERE email = %s;
        """, (email,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'email': result[2],
                'phone': result[3],
                'roll_number': result[4]
            }
        return None
        
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None