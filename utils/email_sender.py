import smtplib
import base64
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

# Function to send email (original function preserved)
def send_email(sender_email, sender_password, recipient_email, subject, body):
    """Send email using SMTP"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Gmail SMTP configuration
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable security
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        return True, "Email sent successfully! ✅"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

# New function that uses environment variables
def send_email_with_env_credentials(recipient_email, subject, body):
    """
    Send email using credentials from environment variables
    Uses EMAIL_ADDRESS and EMAIL_PASSWORD from .env file
    """
    try:
        # Get email credentials from environment
        sender_email = os.getenv("EMAIL_ADDRESS")
        sender_password = os.getenv("EMAIL_PASSWORD")
        
        # Validate credentials
        if not sender_email or not sender_password:
            return False, "Email credentials not configured. Please check EMAIL_ADDRESS and EMAIL_PASSWORD in .env file."
        
        if not recipient_email:
            return False, "Recipient email is required."
        
        if not subject:
            return False, "Email subject is required."
        
        if not body:
            return False, "Email body is required."
        
        # Use the original send_email function
        return send_email(sender_email, sender_password, recipient_email, subject, body)
        
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

# Function to create download link for text file (original function preserved)
def create_download_link(content, filename):
    """Create a download link for text content"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    return href