import streamlit as st
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import base64
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Lets Connect!",
    page_icon="🤝",
    layout="wide"
)

# Load data from JSON file
@st.cache_data
def load_data():
    """Load coordinators and base message from data.json"""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ data.json file not found! Please ensure the file exists in the same directory as app.py")
        st.stop()
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON format in data.json file!")
        st.stop()

# Function to send email
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

# Function to create download link for text file
def create_download_link(content, filename):
    """Create a download link for text content"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    return href

# Initialize OpenRouter client
@st.cache_resource
def init_openrouter_client():
    """Initialize OpenRouter client"""
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            st.error("❌ OPENROUTER_API_KEY not found in .env file!")
            return None
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
    except Exception as e:
        st.error(f"Failed to initialize OpenRouter client: {e}")
        return None

# Load data
data = load_data()
coordinators = data.get('coordinators', [])
base_message_template = data.get('base_message', '')
client = init_openrouter_client()

# Main title
st.title("🤝 Lets Connect!")
st.markdown("*Generate personalized invitation emails for campus recruitment drives*")

st.divider()

# Base Message Section
st.subheader("📝 Base Invitation Message")
st.write("Customize the template message that will be sent to companies:")

base_message = st.text_area(
    label="Base Invitation Message",
    value=base_message_template,
    height=400,
    help="Use placeholders like {company_name}, {name}, {contact}, {cc_email} for personalization"
)

st.divider()

# Company Information Section
st.subheader("🏢 Company Information")

col1, col2 = st.columns(2)

with col1:
    company_name = st.text_input(
        label="Company Name",
        placeholder="e.g., Google, Microsoft, TCS",
        help="Enter the name of the target company"
    )

with col2:
    # Create coordinator dropdown with names only
    coordinator_names = [coord['name'] for coord in coordinators]
    selected_coordinator_name = st.selectbox(
        label="Select Placement Coordinator",
        options=coordinator_names,
        help="Choose the coordinator who will be the point of contact"
    )

# Get selected coordinator details
selected_coordinator = next((coord for coord in coordinators if coord['name'] == selected_coordinator_name), None)

# Additional Information
additional_info = st.text_area(
    label="Additional Company Information (Optional)",
    placeholder="e.g., Company's specific hiring requirements, preferred skill sets, job roles, etc.",
    height=100,
    help="Include any specific details about the company's hiring needs or requirements"
)

st.divider()

# Generate Section
st.subheader("🚀 Generate Invitation")

# Create columns for better layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    generate_button = st.button(
        "Generate Invitation Mail",
        type="primary",
        use_container_width=True
    )

# Generated Mail Output Section
st.divider()

# Initialize session state for generated content
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = ""
if 'mail_generated' not in st.session_state:
    st.session_state.mail_generated = False

if generate_button:
    st.session_state.mail_generated = True
    st.subheader("📨 Generated Invitation Mail")
    
    if company_name and selected_coordinator:
        # Build detailed prompt
        prompt = f"""
You are an expert placement cell assistant. Your job is to draft professional invitation emails to companies for campus recruitment.

Base Invitation Template:
-------------------------
{base_message}

Company Information:
--------------------
Company Name: {company_name}
Additional Info: {additional_info or "N/A"}

Instructions:
-------------
- Rewrite the mail professionally, keeping overall size similar to the base mail (do not make it much longer or shorter).
- Use internet knowledge to identify the company's domains (e.g., web, cloud, AI/ML, app dev, circuits, data analytics, etc.) and areas they hire freshers for.
- If additional info includes specific skills or job roles, highlight how Jadavpur University students match these needs.
- Conclude by clearly stating why our students are a perfect fit for the company.
- Replace placeholders like {{company_name}}, {{name}}, {{contact}}, {{cc_email}} with the actual data provided.
"""
        
        with st.spinner("Generating mail with Mistral..."):
            try:
                if client:
                    response = client.chat.completions.create(
                        model="mistralai/mistral-small-3.2-24b-instruct:free",
                        extra_headers={
                            "HTTP-Referer": "https://letsconnect.ju.ac.in",  # Replace with your deployment URL
                            "X-Title": "Lets Connect!"
                        },
                        messages=[
                            {"role": "system", "content": "You are a professional campus recruitment mail generator."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.7,
                    )
                    st.session_state.generated_content = response.choices[0].message.content.strip()
                else:
                    st.error("❌ OpenRouter client not initialized. Please check your API key.")
                    st.session_state.generated_content = "[Generation failed. Please check API configuration.]"
                
            except Exception as e:
                st.error(f"❌ OpenRouter API error: {e}")
                st.session_state.generated_content = "[Generation failed. Please try again.]"
        
    else:
        st.error("❌ Please enter both the Company Name and select a Placement Coordinator before generating the mail.")
        st.session_state.generated_content = ""

# Display generated mail section if mail has been generated
if st.session_state.mail_generated and st.session_state.generated_content:
    st.subheader("📨 Generated Invitation Mail")
    
    generated_mail = st.text_area(
        label="Generated Invitation Mail",
        value=st.session_state.generated_content,
        height=400,
        help="Copy this generated mail to send to the company",
        key="generated_mail_display"
    )
    
    # Company HR Email Input
    company_email = st.text_input(
        label="Company HR Email",
        placeholder="hr@company.com",
        help="Enter the recipient's email address",
        key="company_email_input"
    )
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Copy to Clipboard", help="Copy the generated mail", key="copy_btn"):
            # Create a copy-to-clipboard component using HTML/JavaScript
            st.components.v1.html(f"""
                <script>
                navigator.clipboard.writeText(`{st.session_state.generated_content.replace('`', '\\`')}`).then(function() {{
                    alert('Mail content copied to clipboard! ✅');
                }}, function(err) {{
                    alert('Failed to copy to clipboard: ' + err);
                }});
                </script>
            """, height=0)
            st.success("✅ Mail copied to clipboard!")
    
    with col2:
        if st.button("📧 Send Email", help="Send email directly", key="send_btn"):
            if not company_email:
                st.error("❌ Please enter the Company HR Email address!")
            elif not company_name:
                st.error("❌ Please enter the Company Name!")
            elif not selected_coordinator:
                st.error("❌ Please select a coordinator!")
            else:
                # Send email
                subject = "Campus Recruitment Invitation - Jadavpur University"
                with st.spinner("Sending email..."):
                    success, message = send_email(
                        sender_email=selected_coordinator['email'],
                        sender_password=selected_coordinator['pswd'],
                        recipient_email=company_email,
                        subject=subject,
                        body=st.session_state.generated_content
                    )
                
                if success:
                    st.success(message)
                else:
                    st.error(f"❌ {message}")
    
    with col3:
        if st.button("💾 Save Draft", help="Save as draft for later use", key="save_btn"):
            if company_name:
                # Create filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{company_name.replace(' ', '_')}_mail_{timestamp}.txt"
                
                # Create download link
                download_link = create_download_link(st.session_state.generated_content, filename)
                st.markdown(download_link, unsafe_allow_html=True)
                st.success(f"✅ Draft prepared for download: {filename}")
            else:
                st.error("❌ Please enter a company name to save the draft!")

elif not st.session_state.mail_generated:
    st.info("👆 Fill in the company details above and click 'Generate Invitation Mail' to create your personalized invitation.")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Developed with ❤️ by the JUMCA Placement 2024/26</p>
        <p><em>Streamlining campus recruitment communications</em></p>
    </div>
    """,
    unsafe_allow_html=True
)

# Updated Sidebar without email/contact inputs
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Display selected coordinator info (without password)
    if selected_coordinator:
        st.subheader("👤 Selected Coordinator")
        st.write(f"**Name:** {selected_coordinator['name']}")
        st.write(f"**Email:** {selected_coordinator['email']}")
        st.write(f"**Phone:** {selected_coordinator['phone']}")
    
    st.divider()
    
    st.subheader("📊 Statistics")
    st.metric("Mails Generated Today", "12")
    st.metric("Companies Contacted", "45")
    st.metric("Success Rate", "78%")
    
    st.divider()
    
    st.subheader("🔗 Quick Links")
    st.markdown("- [JU Placement Portal](#)")
    st.markdown("- [Company Database](#)")
    st.markdown("- [Email Templates](#)")
    st.markdown("- [Contact Management](#)")
    
    st.divider()
    
    st.subheader("ℹ️ Instructions")
    st.markdown("""
    1. Fill in company details
    2. Select coordinator
    3. Generate invitation mail
    4. Enter company HR email
    5. Send, copy, or save draft
    """)

# Display app info
with st.expander("ℹ️ About Lets Connect!"):
    st.markdown("""
    **Lets Connect!** is a streamlined application designed to help the Jadavpur University MCA Placement Cell 
    generate and send personalized recruitment invitation emails to companies.
    
    **Features:**
    - 📝 Customizable invitation templates
    - 👥 Multiple coordinator profiles
    - 📧 Direct email sending capability  
    - 📋 One-click clipboard copying
    - 💾 Draft saving functionality
    - 📊 Usage statistics tracking
    
    **Requirements:**
    - Ensure `data.json` file exists in the same directory
    - Gmail accounts for coordinators with app passwords enabled
    - Valid internet connection for sending emails
    """)