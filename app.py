import streamlit as st
from datetime import datetime

from utils.data_loader import load_data
from utils.email_sender import send_email, create_download_link
from utils.prompt_generator import create_improved_prompt, create_validation_prompt
from utils.post_processor import post_process_mail
from utils.openrouter_client import init_openrouter_client

from components.sidebar import render_sidebar
from components.expander import render_expanders
from components.markdown import render_footer_markdown

# Configure page
st.set_page_config(
    page_title="Lets Connect!",
    page_icon="🤝",
    layout="wide"
)

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
        placeholder="e.g., Amazon, Samsung, Texas, TCS, ...",
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

# Render components
render_sidebar(selected_coordinator, company_name)
render_expanders()
render_footer_markdown()