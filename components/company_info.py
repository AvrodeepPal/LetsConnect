import streamlit as st

def render_company_info_section(coordinators):
    """Render the Company Information section"""
    st.subheader("🏢 Company Information & Email Configuration")

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

    # Additional Information and Bullet Points Configuration
    col3, col4 = st.columns([3, 1])
    
    with col3:
        additional_info = st.text_area(
            label="Additional Company Information (Optional)",
            placeholder="e.g., Company's specific hiring requirements, preferred skill sets, job roles, industry focus, etc.",
            height=100,
            help="Include any specific details about the company's hiring needs, industry focus, or requirements that will help personalize the email"
        )
    
    with col4:
        num_bullet_points = st.slider(
            label="Skill Bullet Points",
            min_value=4,
            max_value=7,
            value=6,
            step=1,
            help="Choose how many bullet points highlighting student skills/expertise to include in the generated email"
        )
    
    return company_name, selected_coordinator, additional_info, num_bullet_points