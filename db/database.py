import os
from dotenv import load_dotenv
from supabase import create_client, Client
import pytz
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')

load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

IST = pytz.timezone('Asia/Kolkata')

_supabase_client = None

def get_supabase_client() -> Client:
    global _supabase_client
    
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase URL and KEY must be set in environment variables")
        
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    return _supabase_client

def get_ist_time():
    return datetime.now(IST)

def generate_dt():
    now = get_ist_time()
    return now.strftime("%d%m%y%H%M")

def test_connection():
    try:
        supabase = get_supabase_client()
        result = supabase.table("coord_details").select("count").execute()
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {e}"

def get_user_by_email(email):
    try:
        supabase = get_supabase_client()
        response = supabase.table("coord_details").select("*").eq("email", email).execute()
        
        if response.data:
            user = response.data[0]
            return {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user.get('phone'),
                'roll_number': user['roll_number']
            }
        return None
        
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def get_user_by_id(user_id):
    try:
        supabase = get_supabase_client()
        response = supabase.table("coord_details").select("*").eq("id", user_id).execute()
        
        if response.data:
            user = response.data[0]
            return {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user.get('phone'),
                'roll_number': user['roll_number']
            }
        return None
        
    except Exception as e:
        print(f"Error fetching user by ID: {e}")
        return None

def log_user_activity(email, activity_type, details=None, dt=None):
    try:
        supabase = get_supabase_client()
        
        ist_time = get_ist_time()
        if not dt:
            dt = generate_dt()
        
        log_entry = {
            "email": email,
            "dt": dt,
            "password_hash": activity_type,
            "last_login": ist_time.isoformat(),
        }
        
        if details:
            log_entry.update(details)
        
        supabase.table("user_logs").insert(log_entry).execute()
        
        return True, "Activity logged successfully", dt
        
    except Exception as e:
        return False, f"Error logging activity: {e}", None

def get_latest_user_log(email, dt=None):
    try:
        supabase = get_supabase_client()
        
        if dt:
            response = supabase.table("user_logs").select("*").eq("email", email).eq("dt", dt).execute()
        else:
            response = supabase.table("user_logs").select("*").eq("email", email).order("last_login", desc=True).limit(1).execute()
        
        if response.data:
            return response.data[0]
        return None
        
    except Exception as e:
        print(f"Error fetching latest user log: {e}")
        return None

def update_user_log(email, updates, dt=None):
    try:
        supabase = get_supabase_client()
        
        if dt:
            supabase.table("user_logs").update(updates).eq("email", email).eq("dt", dt).execute()
        else:
            latest_log = get_latest_user_log(email)
            if not latest_log:
                return False, "No log entry found to update"
            
            supabase.table("user_logs").update(updates).eq("id", latest_log["id"]).execute()
        
        return True, "User log updated successfully"
        
    except Exception as e:
        return False, f"Error updating user log: {e}"

def get_user_log_by_email_dt(email, dt):
    try:
        supabase = get_supabase_client()
        response = supabase.table("user_logs").select("*").eq("email", email).eq("dt", dt).execute()
        
        if response.data:
            return response.data[0]
        return None
        
    except Exception as e:
        print(f"Error fetching user log by email and dt: {e}")
        return None

def log_mail_activity(coordinator_name, company_name, hr_email, coordinator_email=None, email_subject=None, email_body=None):
    try:
        supabase = get_supabase_client()
        
        ist_time = get_ist_time()
        
        mail_log_entry = {
            "coordinator_name": coordinator_name,
            "company_name": company_name,
            "hr_email": hr_email,
            "timestamp": ist_time.isoformat(),
        }
        
        response = supabase.table("mail_logs").insert(mail_log_entry).execute()
        
        return True, "Mail activity logged successfully"
        
    except Exception as e:
        return False, f"Error logging mail activity: {e}"

def get_mail_logs_by_coordinator(coordinator_email=None, coordinator_name=None):
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("mail_logs").select("*")
        
        if coordinator_email:
            query = query.eq("coordinator_email", coordinator_email)
        elif coordinator_name:
            query = query.eq("coordinator_name", coordinator_name)
        else:
            return None, "Either coordinator_email or coordinator_name must be provided"
        
        response = query.order("timestamp", desc=True).execute()
        
        return response.data, "Mail logs retrieved successfully"
        
    except Exception as e:
        return None, f"Error fetching mail logs: {e}"

def get_mail_logs_by_company(company_name):
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("mail_logs").select("*").eq("company_name", company_name).order("timestamp", desc=True).execute()
        
        return response.data, "Mail logs retrieved successfully"
        
    except Exception as e:
        return None, f"Error fetching mail logs for company: {e}"