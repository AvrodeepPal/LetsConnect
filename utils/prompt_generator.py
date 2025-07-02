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
   - Skills list (5-7 ✅ short and concise (2-4 words) bullets) - then gap
   - Closing paragraph - then gap
   - Contact information - then gap
   - Signature block

5. **Structure**: Must follow this exact format with proper spacing:
   Dear Recruitment Team,
   Greetings from the Jadavpur University Placement Cell!
   
   [Company-specific invitation paragraph - KEEP SHORT]
   
   [NAAC/NIRF paragraph with rankings]
   
   [Skills list with 5-7 ✅ bullets - each on new line]
   
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

# Updated improved prompt with better spacing guidance and num_bullet_points parameter
def create_improved_prompt(company_name, additional_info, base_message, num_bullet_points=6):
    """Create an improved prompt for better email generation with proper spacing"""
    
    # Generate the bullet point template based on num_bullet_points
    bullet_template = "\n".join([f"✅ [Skill {i+1} relevant to {company_name}]" for i in range(num_bullet_points)])
    
    return f"""
You are a professional placement officer at Jadavpur University MCA department. Write a complete, personalized invitation email for campus recruitment.

Company: {company_name}
Additional Context: {additional_info or "General recruitment invitation"}

CRITICAL INSTRUCTION: You MUST include exactly {num_bullet_points} bullet points in the skills section. No more, no less.

Write a CONCISE email following this EXACT structure with PROPER SPACING (keep it under 300 words):

Dear Recruitment Team,
Greetings from the Jadavpur University Placement Cell!

[Write 1-2 SHORT sentences about inviting {company_name} specifically - be concise]

Being a NAAC A-Grade Tier-1 institution and consistently ranked among the top engineering and research universities in India (NIRF 2024: 2nd State University, 12th in Engineering), our students bring strong expertise across:

{bullet_template}

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

MANDATORY REQUIREMENTS:
- EXACTLY {num_bullet_points} bullet points starting with ✅ in the skills section
- Use blank lines between major sections for readability
- Skills should be listed without gaps between individual items
- Professional spacing that makes the email easy to scan
- Make skills specific to {company_name}'s industry
- Keep sentences short and direct
- Professional tone but engaging
- Total length around 200-300 words
- Return ONLY the email content, no extra text or markers

REMEMBER: The skills section must contain exactly {num_bullet_points} bullet points. Count them carefully!
"""