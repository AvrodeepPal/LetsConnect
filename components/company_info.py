import streamlit as st
from utils.data_loader import get_unique_departments, get_coordinators_by_department

def render_company_info_section(coordinators):
    """Render the Company Information section with department-based coordinator filtering"""
    st.subheader("🏢 Company Information & Email Configuration")

    # First row: Company Name, Department, Coordinator
    col1, col2, col3 = st.columns(3)

    with col1:
        company_name = st.text_input(
            label="Company Name",
            placeholder="e.g., Amazon, Samsung, Texas, TCS, ...",
            help="Enter the name of the target company"
        )

    with col2:
        # Department dropdown
        departments = get_unique_departments(coordinators)
        if departments:
            selected_department = st.selectbox(
                label="Select Department",
                options=departments,
                help="Choose the department for coordination"
            )
        else:
            st.error("No departments found in coordinator data")
            selected_department = None

    with col3:
        # Coordinator dropdown filtered by department
        if selected_department:
            department_coordinators = get_coordinators_by_department(coordinators, selected_department)
            if department_coordinators:
                coordinator_names = [coord['name'] for coord in department_coordinators]
                selected_coordinator_name = st.selectbox(
                    label="Select Placement Coordinator",
                    options=coordinator_names,
                    help="Choose the coordinator who will be the point of contact"
                )
                
                # Get selected coordinator details
                selected_coordinator = next(
                    (coord for coord in department_coordinators if coord['name'] == selected_coordinator_name), 
                    None
                )
            else:
                st.error(f"No coordinators found for {selected_department} department")
                selected_coordinator = None
        else:
            selected_coordinator = None

    # Additional Information and Bullet Points Configuration
    col4, col5 = st.columns([3, 1])
    
    with col4:
        additional_info = st.text_area(
            label="Additional Company Information (Optional)",
            placeholder="e.g., Company's specific hiring requirements, preferred skill sets, job roles, industry focus, etc.",
            height=100,
            help="Include any specific details about the company's hiring needs, industry focus, or requirements that will help personalize the email"
        )
    
    with col5:
        num_bullet_points = st.slider(
            label="Skill Bullet Points",
            min_value=4,
            max_value=7,
            value=6,
            step=1,
            help="Choose how many bullet points highlighting student skills/expertise to include in the generated email"
        )
    
    return company_name, selected_coordinator, additional_info, num_bullet_points