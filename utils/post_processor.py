import re

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