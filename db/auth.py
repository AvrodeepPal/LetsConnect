import bcrypt
import pytz
from datetime import datetime
from .database import get_supabase_client, log_user_activity, generate_dt

IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    return datetime.now(IST)

def get_user_by_email_local(email):
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
                'roll_number': user['roll_number'],
                'password_hash': user['password_hash']
            }
        return None
        
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def verify_password(email, password):
    try:
        user = get_user_by_email_local(email)
        
        if not user:
            return False, "Invalid credentials - user not found", None
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            user_data = {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user.get('phone'),
                'roll_number': user['roll_number']
            }
            return True, "Password verified successfully", user_data
        else:
            return False, "Invalid credentials - incorrect password", None
            
    except Exception as e:
        return False, f"Authentication error: {e}", None

def create_user_session(email, user_data):
    """Create user session with dt tracking"""
    try:
        ist_time = get_ist_time()
        dt = generate_dt()  # Generate dt for this session
        
        success, message, session_dt = log_user_activity(
            email=email,
            activity_type="login_success",
            details={
                "password_hash": "credential_verified",
                "last_login": ist_time.isoformat()
            },
            dt=dt
        )
        
        if success:
            return True, f"Session created for {user_data['name']}", session_dt
        else:
            return False, f"Failed to create session: {message}", None
        
    except Exception as e:
        return False, f"Session creation error: {e}", None

def authenticate_user(email, password):
    """Authenticate user with password verification"""
    success, message, user_data = verify_password(email, password)
    
    if not success:
        return success, message, user_data
    
    # Create session with dt tracking
    session_success, session_message, session_dt = create_user_session(email, user_data)
    
    if not session_success:
        print(f"Warning: {session_message}")
        return True, f"Authentication successful for {user_data['name']}", user_data
    
    return True, f"Authentication successful for {user_data['name']}", user_data

def validate_user_exists(email):
    """Check if user exists in the system"""
    user_data = get_user_by_email_local(email)
    return user_data is not None, user_data

def get_user_info(email):
    """Get user information by email"""
    return get_user_by_email_local(email)

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password_hash(password, hashed_password):
    """Verify password against hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def log_password_verification(email, success=True):
    """Log password verification attempt"""
    try:
        ist_time = get_ist_time()
        dt = generate_dt()
        
        activity_type = "password_verified" if success else "password_failed"
        
        log_success, message, logged_dt = log_user_activity(
            email=email,
            activity_type=activity_type,
            details={
                "password_hash": activity_type,
                "last_login": ist_time.isoformat()
            },
            dt=dt
        )
        
        return log_success, message, logged_dt
        
    except Exception as e:
        return False, f"Error logging password verification: {e}", None