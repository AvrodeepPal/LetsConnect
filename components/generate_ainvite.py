import streamlit as st
from utils.prompt_generator import create_improved_prompt, create_validation_prompt
from utils.post_processor import post_process_mail, fix_bullet_count

def render_generate_section(company_name, selected_coordinator, additional_info, base_message, client, num_bullet_points):
    """Render the Generate AI-Powered Invitation section"""
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
            prompt = create_improved_prompt(company_name, additional_info, base_message, num_bullet_points)
            
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
                                    "content": f"""You are a professional placement officer at Jadavpur University. 
                                    Write personalized, CONCISE recruitment emails that are tailored to each company's specific industry and needs. 
                                    Always follow the exact structure provided in the prompt. 
                                    Keep emails short, professional, and impactful - around 200-300 words total.
                                    Use proper spacing between sections for better readability.
                                    CRITICAL: Include exactly {num_bullet_points} bullet points highlighting student skills/expertise.
                                    Return ONLY the email content without any introductory text or markers."""
                                },
                                {"role": "user", "content": prompt},
                            ],
                            temperature=0.7,
                            max_tokens=800,
                        )
                        
                        # Enhanced error checking for API response
                        if not response:
                            raise Exception("API returned no response")
                        if not hasattr(response, 'choices') or not response.choices:
                            raise Exception("API response has no choices")
                        if not response.choices[0] or not hasattr(response.choices[0], 'message'):
                            raise Exception("API response choice has no message")
                        if not response.choices[0].message or not hasattr(response.choices[0].message, 'content'):
                            raise Exception("API response message has no content")
                        
                        initial_content = response.choices[0].message.content
                        if not initial_content:
                            raise Exception("API returned empty content")
                        
                        initial_content = initial_content.strip()
                        
                        # Fix bullet count before validation
                        initial_content = fix_bullet_count(initial_content, num_bullet_points, company_name)
                        
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
                                        "content": f"""You are a meticulous email quality checker. Your job is to ensure emails follow exact specifications for professional recruitment communications. Always maintain the personalized content while fixing structure, formatting, and contact details to match requirements exactly. Use proper spacing between sections for better readability. IMPORTANT: Maintain exactly {num_bullet_points} bullet points in the skills section. Return ONLY the clean email content without any introductory text."""
                                    },
                                    {"role": "user", "content": validation_prompt}
                                ],
                                temperature=0.2,
                                max_tokens=800
                            )
                            
                            # Enhanced error checking for validation response
                            if not validation_response:
                                raise Exception("Validation API returned no response")
                            if not hasattr(validation_response, 'choices') or not validation_response.choices:
                                raise Exception("Validation API response has no choices")
                            if not validation_response.choices[0] or not hasattr(validation_response.choices[0], 'message'):
                                raise Exception("Validation API response choice has no message")
                            if not validation_response.choices[0].message or not hasattr(validation_response.choices[0].message, 'content'):
                                raise Exception("Validation API response message has no content")
                            
                            validated_content = validation_response.choices[0].message.content
                            if not validated_content:
                                raise Exception("Validation API returned empty content")
                            
                            validated_content = validated_content.strip()
                            
                            # Fix bullet count again after validation
                            validated_content = fix_bullet_count(validated_content, num_bullet_points, company_name)
                        
                        # Final post-processing for any remaining issues
                        with st.spinner("🔧 Finalizing email format..."):
                            st.session_state.generated_content = post_process_mail(
                                validated_content, 
                                selected_coordinator['name'], 
                                selected_coordinator['phone'],
                                selected_coordinator,
                                company_name,
                                num_bullet_points
                            )
                        
                        st.success(f"✅ Concise and personalized invitation for {company_name} generated successfully with {num_bullet_points} key skills!")
                        
                    else:
                        st.error("❌ OpenRouter client not initialized. Please check your API key.")
                        st.session_state.generated_content = "[Generation failed. Please check API configuration.]"
                    
                except Exception as e:
                    st.error(f"❌ OpenRouter API error: {e}")
                    # Enhanced fallback option with proper bullet count
                    bullet_points = [
                        "✅ Data Science & Analytics",
                        "✅ Machine Learning & AI", 
                        "✅ Web and App Development",
                        "✅ Cloud & DevOps",
                        "✅ Core Engineering & Software Development",
                        "✅ Mobile Application Development",
                        "✅ Database Management & SQL",
                        "✅ Cybersecurity & Network Management",
                        "✅ UI/UX Design & Frontend Development",
                        "✅ API Development & Integration"
                    ]
                    
                    # Select the exact number of bullet points based on slider value
                    selected_bullets = bullet_points[:num_bullet_points]
                    bullet_text = "\n".join(selected_bullets)
                    
                    st.session_state.generated_content = f"""Dear Recruitment Team,
Greetings from the Jadavpur University Placement Cell!

We are excited to invite {company_name} to participate in our Campus Recruitment Drive for the 2026 graduating batch.

Being a NAAC A-Grade Tier-1 institution and consistently ranked among the top engineering and research universities in India (NIRF 2024: 2nd State University, 12th in Engineering), our students bring strong expertise across:

{bullet_text}

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