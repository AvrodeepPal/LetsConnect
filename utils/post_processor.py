import re

def fix_bullet_count(content, num_bullet_points, company_name):
    lines = content.split('\n')
    bullet_lines = [line for line in lines if line.strip().startswith('✅')]
    
    default_skills = [
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
    
    if len(bullet_lines) == num_bullet_points:
        return content
    
    if len(bullet_lines) < num_bullet_points:
        needed = num_bullet_points - len(bullet_lines)
        additional_skills = default_skills[len(bullet_lines):len(bullet_lines) + needed]
        bullet_lines.extend(additional_skills)
    elif len(bullet_lines) > num_bullet_points:
        bullet_lines = bullet_lines[:num_bullet_points]
    
    new_lines = []
    in_bullet_section = False
    bullet_added = False
    
    for line in lines:
        if line.strip().startswith('✅'):
            if not bullet_added:
                new_lines.extend(bullet_lines)
                bullet_added = True
            continue
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines)

def post_process_mail(generated_mail, coordinator_name, coordinator_phone, selected_coordinator, company_name=None, num_bullet_points=6):
    if "---" in generated_mail:
        parts = generated_mail.split("---")
        if len(parts) >= 3:
            generated_mail = parts[1].strip()
        elif len(parts) == 2:
            generated_mail = parts[1].strip()
    
    lines = generated_mail.split('\n')
    cleaned_lines = []
    start_processing = False
    
    for line in lines:
        line = line.strip()
        if any(phrase in line.lower() for phrase in [
            "here is the corrected", "here's the corrected", "here is the email",
            "here's the email", "follows all specifications", "that follows all"
        ]):
            continue
        if line.startswith("Dear Recruitment Team"):
            start_processing = True
        
        if start_processing and line:
            cleaned_lines.append(line)
    
    if cleaned_lines:
        generated_mail = '\n'.join(cleaned_lines)
    
    if company_name:
        generated_mail = fix_bullet_count(generated_mail, num_bullet_points, company_name)
    
    processed_mail = generated_mail.replace("[COORDINATOR_EMAIL]", selected_coordinator['email'])
    processed_mail = processed_mail.replace("[COORDINATOR_NAME]", coordinator_name)
    processed_mail = processed_mail.replace("[COORDINATOR_PHONE]", coordinator_phone)
    
    # Get department from selected_coordinator, fallback to 'Department' if not found
    department = selected_coordinator.get('department', 'Department')
    processed_mail = processed_mail.replace("[COORDINATOR_DEPARTMENT]", department)
    
    lines = processed_mail.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        formatted_lines.append(line)
        
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
            
            formatted_lines.append("")
    
    processed_mail = '\n'.join(formatted_lines)
    processed_mail = re.sub(r'\n\s*\n\s*\n+', '\n\n', processed_mail)
    processed_mail = processed_mail.strip()
    
    return processed_mail