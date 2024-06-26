import streamlit as st
import secrets
import string

def capitalize_name(name):
    return " ".join(word.capitalize() for word in name.split())

def parse_input(data):
    lines = data.split('\n')
    parsed_data = {}
    
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            parsed_data[key] = value
    
    return parsed_data

def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_message(data):
    manager = capitalize_name(data.get("Hiring Manager Name", ""))
    name = capitalize_name(data.get("Candidate Name", ""))
    job_title = data.get("candidate Job Title", "") or data.get("Candidate Job Title", "")  # Handle both variations
    location = data.get("Location", "")
    telephone = data.get("Candidate Mobile Number", "")
    address = data.get("Candidate Address", "")
    company_name = data.get("Company Name", "")

    names = name.split()
    first_name = names[0]
    last_name = names[-1]
    
    username = f"{first_name.lower()}.{last_name.lower()}"
    
    # Generate random passwords
    default_password = generate_password()
    spectra_pm_password = generate_password()

    permissions = []
    if data.get("Access Permissions for XRM", "").lower() != "no" and data.get("Access Permissions for XRM", "").strip():
        permissions.append("XRM")
    if data.get("Access to Standard Applications - Iris", "").lower() != "no" and data.get("Access to Standard Applications - Iris", "").strip():
        permissions.append("IRIS")

    # Determine the user email based on Company Registered Number
    if "Health Intelligence" in data.get("Company Registered Number", ""):
        user_email = f"{username}@health-intelligence.com"
        internal_note = f"""An account for {name} was created on the following platforms:
- M365
- Blackstar VPN
- Guest account
- Shared mailbox/Distribution Lists
- Active Directory user account updated with necessary details"""
        company_display = "Health Intelligence"
        sections = [
            "VPN Account", 
            "Office 365 Account", 
            "Ad Account",            
            "InHealth Guest Account", 
            "Mail Distribution", 
            "Spectra PM", 
            "8x8 VCC Account"
        ]
    elif "TAC Healthcare" in data.get("Company Registered Number", ""):
        user_email = f"{username}@tachealthcare.com"
        company_display = "TAC Healthcare"
        internal_note = f"""An account for {name} was created on the following platforms:
- Exchange admin center
- Active Directory user account updated with necessary details"""
        sections = [
            "Office 365 Account", 
            "Ad Account",    
        ]
    else:
        user_email = f"{username}@inhealthgroup.com"
        company_display = "InHealth Group"
        internal_note = f"""An account for {name} was created on the following platforms:
- Exchange admin center
- Active Directory user account updated with necessary details"""
        sections = [
            "Office 365 Account", 
            "Ad Account"
        ]
    
    if permissions:
        sections.append("Permissions")
        internal_note += f"\n- {' and '.join(permissions)} permissions added"

    internal_note += f"\n\nA message containing the account details was sent to {manager} via Teams."

    return {
        "Candidates First Name": first_name,
        "Candidates Last Name": last_name,
        "Username": username,
        "Password": default_password,
        "Candidate's Full Name": name,
        "Description": job_title,
        "Office": location,
        "Job Title": job_title,
        "Company": company_display,
        "Manager": manager,
        "\\Documents": f"\\\\IHGD\\Homefolder\\Profiles\\{username}",
        "Mobile": telephone,
        "Address": address,
        "User Email": user_email,
        "Department": company_name,
        "Spectra PM Username": f"{first_name.lower()}{last_name[0].lower()}super",
        "Spectra PM Password": spectra_pm_password,
        "NHS Email": "nomail@nhs.net",
        "Permissions": ", ".join(permissions),
        "Message to Send Manager": f"""Hello {manager},

Please find the login details for the new starter, {name}, who will be joining as a {job_title}.

Username: {username}
User Email: {user_email}
Password: {default_password}

Best regards,
Your IT Team""",
        "Internal Note": internal_note,
        "Sections": sections
    }

st.title('Generate User Onboarding Details')

data = st.text_area("Paste the full details here:", height=300)

if st.button('Generate Details'):
    if data:
        parsed_data = parse_input(data)
        st.session_state.generated_data = generate_message(parsed_data)
    else:
        st.error("Please enter the required details")

if "generated_data" in st.session_state:
    sections = st.session_state.generated_data["Sections"]

    for section in sections:
        with st.expander(section, expanded=False):
            keys_to_display = []
            if section == "VPN Account":
                keys_to_display = [
                    "Candidates First Name", "Candidates Last Name", "Username", "Password", 
                    "Candidate's Full Name", "Description", "Office", "Job Title", "Company", 
                    "Manager", "User Email"
                ]
            elif section == "Office 365 Account":
                keys_to_display = [
                    "Candidates First Name", "Candidates Last Name", "Username", "Password", 
                    "Candidate's Full Name", "Description","Job Title", "Department","Office",
                    "Manager", "Mobile", "Address", "User Email"
                ]
            elif section == "InHealth Guest Account":
                keys_to_display = [
                    "User Email", "Candidate's Full Name"
                ]
            elif section == "Ad Account":
                keys_to_display = [
                    "Candidates First Name", "Candidates Last Name", "Username", "Password", 
                    "Candidate's Full Name", "Description", "Office", "Job Title", "Department", "Company",
                    "Manager", "\\Documents", "User Email"
                ]
            elif section == "Mail Distribution":
                keys_to_display = [
                    "User Email"
                ]
            elif section == "Spectra PM":
                keys_to_display = [
                    "Candidates First Name", "Candidates Last Name","Spectra PM Username", "Spectra PM Password", "NHS Email"
                ]
            elif section == "8x8 VCC Account":
                keys_to_display = [
                    "Candidates First Name", "Candidates Last Name", "Username", "Job Title", "Department", "User Email", "Office"
                ]
            elif section == "Permissions":
                keys_to_display = [
                    "Permissions"
                ]
            
            for key in keys_to_display:
                if key in st.session_state.generated_data:
                    st.markdown(f"**{key} :**")
                    st.code(st.session_state.generated_data[key], language='plaintext')

    # Display Internal Note, Manager, and Message to Send Manager
    st.markdown("### Internal Note")
    st.code(st.session_state.generated_data["Internal Note"], language='plaintext')
    
    st.markdown("### Manager")
    st.code(st.session_state.generated_data["Manager"], language='plaintext')
    
    st.markdown("### Message to Send Manager")
    st.code(st.session_state.generated_data["Message to Send Manager"], language='plaintext')
