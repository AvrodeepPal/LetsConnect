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
import re

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

# Enhanced post-processing function to clean AI output and maintain proper spacing
def post_process_mail(generated_mail, coordinator_name, coordinator_phone, selected_coordinator):
    """Post-process the generated mail to replace placeholders and ensure proper formatting with appropriate gaps"""
    
    # Extract content between --- markers if present
    if "---" in generated_mail:
        parts = generated_mail.split("---")
        if len(parts) >= 3:
            # Take the middle part (between first and second ---)
            generated_mail = parts[1].strip()
        elif len(parts) == 2:
            # Take the part after the first ---
            generated_mail = parts[1].strip()
    
    # Remove any leading text like "Here is the corrected email..." or similar
    lines = generated_mail.split('\n')
    cleaned_lines = []
    start_processing = False
    
    for line in lines:
        line = line.strip()
        # Skip introductory lines from AI
        if any(phrase in line.lower() for phrase in [
            "here is the corrected", "here's the corrected", "here is the email",
            "here's the email", "follows all specifications", "that follows all"
        ]):
            continue
        # Start processing when we hit "Dear Recruitment Team"
        if line.startswith("Dear Recruitment Team"):
            start_processing = True
        
        if start_processing and line:
            cleaned_lines.append(line)
    
    # Join the cleaned lines first
    if cleaned_lines:
        generated_mail = '\n'.join(cleaned_lines)
    
    # Replace the placeholders in the AI-generated content
    processed_mail = generated_mail.replace("[COORDINATOR_EMAIL]", selected_coordinator['email'])
    processed_mail = processed_mail.replace("[COORDINATOR_NAME]", coordinator_name)
    processed_mail = processed_mail.replace("[COORDINATOR_PHONE]", coordinator_phone)
    
    # Now apply proper spacing rules for different sections
    lines = processed_mail.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:  # Skip empty lines for now
            continue
            
        formatted_lines.append(line)
        
        # Add gaps after specific sections
        if (line.startswith("Dear Recruitment Team,") or 
            line.startswith("Greetings from the Jadavpur University Placement Cell!") or
            line.endswith("across:") or
            (line.startswith("✅") and i < len(lines) - 1 and not lines[i + 1].strip().startswith("✅")) or
            line.endswith("requirements.") or
            line.endswith("team.") or
            line.endswith("needs.") or
            "collaboration with" in line.lower() or
            line.startswith("📧 CC:") or
            "We look forward to" in line):
            
            formatted_lines.append("")  # Add blank line
    
    # Join with newlines and clean up
    processed_mail = '\n'.join(formatted_lines)
    
    # Clean up any multiple consecutive blank lines
    processed_mail = re.sub(r'\n\s*\n\s*\n+', '\n\n', processed_mail)
    processed_mail = processed_mail.strip()
    
    return processed_mail

# Updated validation prompt with clearer spacing instructions
def create_validation_prompt(generated_email, coordinator_name, coordinator_phone, coordinator_email, company_name):
    """Create a validation prompt to ensure the email follows exact requirements with proper spacing"""
    return f"""
You are a quality assurance specialist for professional emails. Review and refine the following recruitment email to ensure it meets EXACT requirements:

GENERATED EMAIL:
{generated_email}

REQUIRED SPECIFICATIONS:
1. **Email Structure**: Must contain exactly these email addresses:
   - Primary: officer.placement@jadavpuruniversity.in, jupgcsit2026@gmail.com
   - CC: {coordinator_email}

2. **Signature Block**: Must end with exactly:
   Best Regards,
   {coordinator_name}
   Placement Coordinator, MCA
   Jadavpur Placement Cell
   📞 {coordinator_phone}

3. **Length**: Keep it concise and professional (around 200-300 words)

4. **Formatting**: Use proper spacing between sections for readability:
   - Greeting section (Dear + Greetings) - then gap
   - Company invitation paragraph - then gap
   - NAAC/NIRF paragraph - then gap
   - Skills list (6-7 ✅ bullets) - then gap
   - Closing paragraph - then gap
   - Contact information - then gap
   - Signature block

5. **Structure**: Must follow this exact format with proper spacing:
   Dear Recruitment Team,
   Greetings from the Jadavpur University Placement Cell!
   
   [Company-specific invitation paragraph - KEEP SHORT]
   
   [NAAC/NIRF paragraph with rankings]
   
   [Skills list with 6-7 ✅ bullets - each on new line]
   
   [Brief closing paragraph about collaboration]
   
   [Contact information with exact emails]
   
   [Signature block]

6. **Company Name**: Must be "{company_name}" throughout

IMPORTANT: 
- Use blank lines between major sections for better readability
- Keep skills list items on separate lines without gaps between them
- Return ONLY the clean email content without any introductory text, headers, footers, or "---" markers
- Start directly with "Dear Recruitment Team," and end with the signature block
- Ensure proper visual separation between different content sections
"""

# Updated improved prompt with better spacing guidance
def create_improved_prompt(company_name, additional_info, base_message):
    """Create an improved prompt for better email generation with proper spacing"""
    return f"""
You are a professional placement officer at Jadavpur University MCA department. Write a complete, personalized invitation email for campus recruitment.

Company: {company_name}
Additional Context: {additional_info or "General recruitment invitation"}

Write a CONCISE email following this EXACT structure with PROPER SPACING (keep it under 300 words):

Dear Recruitment Team,
Greetings from the Jadavpur University Placement Cell!

[Write 1-2 SHORT sentences about inviting {company_name} specifically - be concise]

Being a NAAC A-Grade Tier-1 institution and consistently ranked among the top engineering and research universities in India (NIRF 2024: 2nd State University, 12th in Engineering), our students bring strong expertise across:

✅ [Skill 1 relevant to {company_name}]
✅ [Skill 2 relevant to {company_name}]
✅ [Skill 3 relevant to {company_name}]
✅ [Skill 4 relevant to {company_name}]
✅ [Skill 5 relevant to {company_name}]
✅ [Skill 6 relevant to {company_name}]
✅ [Skill 7 relevant to {company_name}]

[Write 1 SHORT sentence about why our students would be perfect for {company_name}]

For coordination, please feel free to reach out:  
📧 Email: officer.placement@jadavpuruniversity.in, jupgcsit2026@gmail.com 
📧 CC: [COORDINATOR_EMAIL]

We look forward to a fruitful collaboration with {company_name}!

Best Regards,  
[COORDINATOR_NAME]  
Placement Coordinator, MCA  
Jadavpur Placement Cell  
📞 [COORDINATOR_PHONE]

CRITICAL FORMATTING REQUIREMENTS:
- Use blank lines between major sections (greeting, company intro, NAAC paragraph, skills, closing, contact, signature)
- Skills should be listed without gaps between individual items
- Each section should be visually separated for better readability
- Professional spacing that makes the email easy to scan

Requirements:
- Make it specific to {company_name}'s industry but CONCISE
- Keep sentences short and direct
- Professional tone but engaging
- Total length should be around 200-300 words
- Use proper spacing for professional appearance
- Return ONLY the email content, no extra text or markers
"""

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
        placeholder="e.g., Google, Microsoft, TCS, Goldman Sachs",
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
    placeholder="e.g., Company's specific hiring requirements, preferred skill sets, job roles, industry focus, etc.",
    height=100,
    help="Include any specific details about the company's hiring needs, industry focus, or requirements that will help personalize the email"
)

st.divider()

# Generate Section
st.subheader("🚀 Generate AI-Powered Invitation")

# Create columns for better layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    generate_button = st.button(
        "🤖 Generate Personalized Invitation Mail",
        type="primary",
        use_container_width=True
    )

# Initialize session state for generated content
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = ""
if 'mail_generated' not in st.session_state:
    st.session_state.mail_generated = False

# Enhanced generation logic
if generate_button:
    st.session_state.mail_generated = True
    
    if company_name and selected_coordinator:
        prompt = create_improved_prompt(company_name, additional_info, base_message)
        
        with st.spinner(f"🤖 Generating personalized invitation for {company_name}..."):
            try:
                if client:
                    # First AI generation call
                    response = client.chat.completions.create(
                        model="mistralai/mistral-small-3.2-24b-instruct:free",
                        extra_headers={
                            "HTTP-Referer": "https://letsconnect.ju.ac.in",
                            "X-Title": "Lets Connect!"
                        },
                        messages=[
                            {
                                "role": "system", 
                                "content": """You are a professional placement officer at Jadavpur University. 
                                Write personalized, CONCISE recruitment emails that are tailored to each company's specific industry and needs. 
                                Always follow the exact structure provided in the prompt. 
                                Keep emails short, professional, and impactful - around 200-300 words total.
                                Use proper spacing between sections for better readability.
                                Return ONLY the email content without any introductory text or markers."""
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.7,
                        max_tokens=800,
                    )
                    
                    initial_content = response.choices[0].message.content.strip()
                    
                    # Second AI call for validation and refinement
                    with st.spinner("🔍 Validating email structure and requirements..."):
                        validation_prompt = create_validation_prompt(
                            initial_content,
                            selected_coordinator['name'],
                            selected_coordinator['phone'], 
                            selected_coordinator['email'],
                            company_name
                        )
                        
                        validation_response = client.chat.completions.create(
                            model="mistralai/mistral-small-3.2-24b-instruct:free",
                            extra_headers={
                                "HTTP-Referer": "https://letsconnect.ju.ac.in",
                                "X-Title": "Lets Connect!"
                            },
                            messages=[
                                {
                                    "role": "system",
                                    "content": """You are a meticulous email quality checker. Your job is to ensure emails follow exact specifications for professional recruitment communications. Always maintain the personalized content while fixing structure, formatting, and contact details to match requirements exactly. Use proper spacing between sections for better readability. Return ONLY the clean email content without any introductory text."""
                                },
                                {"role": "user", "content": validation_prompt}
                            ],
                            temperature=0.2,
                            max_tokens=800
                        )
                        
                        validated_content = validation_response.choices[0].message.content.strip()
                    
                    # Final post-processing for any remaining issues
                    with st.spinner("🔧 Finalizing email format..."):
                        st.session_state.generated_content = post_process_mail(
                            validated_content, 
                            selected_coordinator['name'], 
                            selected_coordinator['phone'],
                            selected_coordinator
                        )
                    
                    st.success(f"✅ Concise and personalized invitation for {company_name} generated successfully!")
                    
                else:
                    st.error("❌ OpenRouter client not initialized. Please check your API key.")
                    st.session_state.generated_content = "[Generation failed. Please check API configuration.]"
                
            except Exception as e:
                st.error(f"❌ OpenRouter API error: {e}")
                # Enhanced fallback option with proper spacing
                st.session_state.generated_content = f"""Dear Recruitment Team,
Greetings from the Jadavpur University Placement Cell!

We are excited to invite {company_name} to participate in our Campus Recruitment Drive for the 2026 graduating batch.

Being a NAAC A-Grade Tier-1 institution and consistently ranked among the top engineering and research universities in India (NIRF 2024: 2nd State University, 12th in Engineering), our students bring strong expertise across:

✅ Data Science & Analytics  
✅ Machine Learning & AI  
✅ Web and App Development  
✅ Cloud & DevOps  
✅ Core Engineering & Software Development
✅ Mobile Application Development

We believe our students align perfectly with {company_name}'s talent requirements.

For coordination, please feel free to reach out:  
📧 Email: officer.placement@jadavpuruniversity.in, jupgcsit2026@gmail.com 
📧 CC: {selected_coordinator['email']}

We look forward to a fruitful collaboration with {company_name}!

Best Regards,  
{selected_coordinator['name']}  
Placement Coordinator, MCA  
Jadavpur Placement Cell  
📞 {selected_coordinator['phone']}"""
        
    else:
        st.error("❌ Please enter both the Company Name and select a Placement Coordinator before generating the mail.")
        st.session_state.generated_content = ""

st.divider()

# Display generated mail section if mail has been generated
if st.session_state.mail_generated and st.session_state.generated_content:
    st.subheader("📨 Generated Personalized Invitation Mail")
    
    # Show a preview box with the generated content
    with st.container():
        st.markdown("### 👀 Preview:")
        st.markdown(f"**Subject:** Campus Recruitment Invitation - Jadavpur University")
        st.text_area(
            label="Generated Invitation Mail",
            value=st.session_state.generated_content,
            height=400,
            help="Review and edit the generated mail if needed before sending",
            key="generated_mail_display"
        )
    
    # Company HR Email Input
    st.markdown("### 📧 Recipient Details")
    company_email = st.text_input(
        label="Company HR Email",
        placeholder="hr@company.com, recruitment@company.com",
        help="Enter the recipient's email address",
        key="company_email_input"
    )
    
    # Action buttons
    st.markdown("### 🎯 Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Copy to Clipboard", help="Copy the generated mail", key="copy_btn"):
            # Create a copy-to-clipboard component using HTML/JavaScript
            st.components.v1.html(f"""
                <script>
                navigator.clipboard.writeText(`{st.session_state.generated_content.replace('`', '\\`')}`).then(function() {{
                    // Success feedback handled by Streamlit
                }}, function(err) {{
                    alert('Failed to copy to clipboard: ' + err);
                }});
                </script>
            """, height=0)
            st.success("✅ Mail content copied to clipboard!")
    
    with col2:
        send_email_clicked = st.button("📧 Send Email", help="Send email directly", key="send_btn")
        
        # Password input appears only when send email is clicked
        if send_email_clicked:
            if not company_email:
                st.error("❌ Please enter the Company HR Email address!")
            elif not company_name:
                st.error("❌ Please enter the Company Name!")
            elif not selected_coordinator:
                st.error("❌ Please select a coordinator!")
            else:
                # Show password input
                st.markdown("##### 🔐 Enter Gmail App Password")
                gmail_password = st.text_input(
                    label="Gmail App Password",
                    type="password",
                    placeholder="Enter your Gmail app password",
                    help="Enter the app password for the coordinator's Gmail account",
                    key="gmail_password_input"
                )
                
                if st.button("🚀 Confirm Send", key="confirm_send_btn"):
                    if not gmail_password:
                        st.error("❌ Please enter your Gmail app password!")
                    else:
                        # Send email
                        subject = f"Campus Recruitment Invitation - Jadavpur University ({company_name})"
                        with st.spinner("Sending personalized email..."):
                            success, message = send_email(
                                sender_email=selected_coordinator['email'],
                                sender_password=gmail_password,
                                recipient_email=company_email,
                                subject=subject,
                                body=st.session_state.generated_content
                            )
                        
                        if success:
                            st.success(f"🎉 {message}")
                            st.balloons()
                        else:
                            st.error(f"❌ {message}")
    
    with col3:
        if st.button("💾 Save Draft", help="Save as draft for later use", key="save_btn"):
            if company_name:
                # Create filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{company_name.replace(' ', '_')}_invitation_{timestamp}.txt"
                
                # Create download link
                download_link = create_download_link(st.session_state.generated_content, filename)
                st.markdown(download_link, unsafe_allow_html=True)
                st.success(f"✅ Draft prepared for download: {filename}")
            else:
                st.error("❌ Please enter a company name to save the draft!")
    
    # Regenerate option
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Generate New Version", help="Generate a different version of the email", key="regenerate_btn"):
            st.session_state.mail_generated = False
            st.rerun()

elif not st.session_state.mail_generated:
    st.info("👆 Fill in the company details above and click 'Generate Personalized Invitation Mail' to create your AI-powered, tailored invitation.")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Developed with ❤️ by the JUMCA Placement 2024/26</p>
        <p><em>AI-Powered Campus Recruitment Communications</em></p>
        <p style='font-size: 12px; margin-top: 10px;'>
            🤖 Powered by Mistral AI for personalized content generation
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Enhanced Sidebar
with st.sidebar:
    st.header("⚙️ Settings & Info")
    
    # Display selected coordinator info
    if selected_coordinator:
        st.subheader("👤 Selected Coordinator")
        st.write(f"**Name:** {selected_coordinator['name']}")
        st.write(f"**Email:** {selected_coordinator['email']}")
        st.write(f"**Phone:** {selected_coordinator['phone']}")
    
    st.divider()
    
    st.subheader("📊 Session Statistics")
    # Get current session stats (you can enhance this with actual tracking)
    if 'mail_count' not in st.session_state:
        st.session_state.mail_count = 0
    if st.session_state.mail_generated and st.session_state.generated_content:
        if 'last_company' not in st.session_state or st.session_state.last_company != company_name:
            st.session_state.mail_count += 1
            st.session_state.last_company = company_name
    
    st.metric("Mails Generated This Session", st.session_state.mail_count)
    st.metric("Current Model", "Mistral AI")
    st.metric("Personalization Level", "High")
    
    st.divider()
    
    st.subheader("🔗 Quick Links")
    st.markdown("- [JU Placement Portal](#)")
    st.markdown("- [Company Database](#)")
    st.markdown("- [Email Templates](#)")
    st.markdown("- [Contact Management](#)")
    
    st.divider()
    
    st.subheader("ℹ️ How It Works")
    st.markdown("""
    1. **Input**: Company details + context
    2. **AI Processing**: Mistral AI analyzes and personalizes
    3. **Generation**: Tailored email created
    4. **Review & Send**: Review, edit, and send
    5. **Track**: Monitor success rates
    """)
    
    st.divider()
    
    st.subheader("💡 Tips for Better Results")
    st.markdown("""
    - **Be Specific**: Add company industry details
    - **Context Matters**: Mention specific roles/skills
    - **Review**: Always review generated content
    - **Personalize**: Edit if needed before sending
    """)

# Display app info
with st.expander("ℹ️ About Lets Connect! - AI Edition"):
    st.markdown("""
    **Lets Connect!** is an AI-powered application designed to help the Jadavpur University MCA Placement Cell 
    generate and send highly personalized recruitment invitation emails to companies.
    
    **🚀 New AI Features:**
    - 🤖 **AI-Powered Personalization**: Each email is uniquely crafted for the target company
    - 🎯 **Industry-Specific Content**: Skills and messaging tailored to company's domain
    - 📊 **Smart Context Analysis**: Uses additional company info for better personalization
    - 🔄 **Multiple Variations**: Generate different versions of the same invitation
    - ✂️ **Clean Output**: Concise, professional emails without unnecessary fluff
    - 📏 **Proper Spacing**: Professional formatting with appropriate gaps between sections
    
    **📧 Core Features:**
    - 📝 Dynamic email generation (no more templates!)
    - 👥 Multiple coordinator profiles
    - 📧 Direct email sending capability
    - 📋 One-click clipboard copying
    - 💾 Draft saving functionality
    - 📊 Session statistics tracking
    
    **🔧 Technical Requirements:**
    - `data.json` file with coordinator information
    - `.env` file with `OPENROUTER_API_KEY`
    - Gmail accounts with app passwords enabled
    - Internet connection for AI generation and email sending
    
    **🔒 Security & Privacy:**
    - Passwords never stored in memory
    - API keys secured in environment variables
    - All generation happens in real-time
    
    **🎨 Personalization Examples:**
    - **Tech Companies**: Focus on AI/ML, cloud, software development
    - **Finance**: Emphasize quantitative analysis, risk management
    - **Consulting**: Highlight problem-solving, analytics
    - **Startups**: Mention agility, full-stack capabilities
    """)