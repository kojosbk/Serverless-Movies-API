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

def generate_password_from_name(first_name, last_name):
    first_part = first_name.lower()[:3]
    last_part = last_name.lower()[:3]
    return generate_password_from_env()

def generate_message(data):
    manager = capitalize_name(data.get("Hiring Manager Name", ""))
    name = capitalize_name(data.get("Candidate Name", ""))
    job_title = data.get("candidate Job Title", "") or data.get("Candidate Job Title", "")  # Handle both variations
    location = data.get("Location", "")
    telephone = data.get("Candidate Mobile Number", "")
    address = data.get("Candidate Address", "")
    company_name = data.get("Company Name", "")
    start_date = data.get("Start Date", "")

    names = name.split()
    first_name = names[0]
    last_name = names[-1]
    
    username = f"{first_name.lower()}.{last_name.lower()}"
    
    # Generate passwords using the first 3 letters of first and last name plus #24
    default_password = generate_password_from_name(first_name, last_name)
    spectra_pm_password = generate_password_from_name(first_name, last_name)

    permissions = []
    if data.get("Access Permissions for XRM", "").lower() != "no" and data.get("Access Permissions for XRM", "").strip():
        permissions.append("XRM")
    if data.get("Access to Standard Applications - Iris", "").lower() != "no" and data.get("Access to Standard Applications - Iris", "").strip():
        permissions.append("IRIS")

    # Determine the user email based on Company Registered Number
    if "Health Intelligence" in data.get("Company Registered Number", ""):
        user_email = f"{username}@health-intelligence.com"
        internal_note = f"""An account for {name} has been created on the following platforms:
- M365
- Blackstar VPN
- Guest account
- Shared mailbox/Distribution Lists
- Active Directory user account updated with necessary details
- Spectra PM
- 8x8"""
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
        internal_note = f"""An account for {name} has been created on the following platforms:
- Exchange admin center
- Active Directory user account updated with necessary details"""
        sections = [
            "Office 365 Account", 
            "Ad Account",    
        ]
    else:
        user_email = f"{username}@inhealthgroup.com"
        company_display = "InHealth Group"
        internal_note = f"""An account for {name} has been created on the following platforms:
- Exchange admin center
- Active Directory user account updated with necessary details"""
        sections = [
            "Office 365 Account", 
            "Ad Account"
        ]
    
    if permissions:
        sections.append("Permissions")
        internal_note += f"\n- {' and '.join(permissions)} permissions added"

    internal_note += f"\n\nA message containing the account details has been sent to {manager.split()[0]} via Teams."

    groups = {
        "Patient Care Advisor": [
            "SEC_PRC_FILE_COMMUNITY", "SEC_G_License_F3", "Sec_G_No_Proxy", "Sec_G_PRC_Printer_PRC_Battery_Printer",
            "Sec_G_InTune_PRC_BlkActSync_MAM", "SEC_G_PRC_ARCHIVENONMANAGEMENT_TRIAGE_FOLDER_SECURITY_RW_IHGD",
            "SEC_G_KnowHow_Visitors", "SEC_G_PRC_FOLDER_MEMBERS_RW_IHGD", "SEC_G_PRC_FOLDER_MEMBERS_RW_INHEALTH",
            "Domain Users", "Know How Shortcut deployment", "SEC_G_AOVPN_Users", "SEC_G_PRC_MANAGEMENT_FOLDER_MEMBERS_RW_INHEALTH",
            "SEC_G_EGRESS_PRC", "Sec_g_8x8_Sync", "SEC_G_PRC_FOLDER", "SEC_PRC_PRINT_ROCHDALE",
            "SEC_G_folder_redirection_IHGD-PS-VP-001", "SEC_G_CTX_PRC_Roch", "ReportingGroup_test",
            "ReportingGroup {d0fc2c1d-7893-4860-b23b-36a9d695a7b2}", "ReportingGroup {32ba4025-aa86-40b4-ac49-688f83484209}"
        ],
        "Adaptation Nurse": [
            "ihgd.inhealthgroup.com/IHGD Internal/IHGD Users/Clinical/Endoscopy/Folder redirection - Endoscopy/Schelma Rivas",
            "SEC_G_License_F3", "Domain Users", "SEC_G_AOVPN_Users"
        ],
        "Triage Nurse": [
            "SEC_G_OPERATIONS_NWCATS_SPOA FOLDER_SECURITY_RW_IHGD", "SEC_G_ALLCLINICAL_RW_IHGD", "SEC_G_Sentinel_SSO",
            "SEC_G_License_E3", "SEC_G_KnowHow_Visitors", "Domain Users", "Sec_PDL_Allow", "Know How Shortcut deployment",
            "SEC_G_AOVPN_Users", "Sec_G_Clinical_Reviewer", "Sec_G_InTune_BlkActSync_MDM", "SEC_G_OPERATIONS_NWCATS_STOCKPORT_FOLDER_SECURITY_RW_IHGD",
            "SEC_G_Clinical_Endoscopy_Reports", "Sec_G_InTune_MDM_MTD_Compliant", "Sec_g_8x8_Sync", "SEC_G_Egress_POC",
            "SEC_G_OPERATIONS_NWCATS_FOLDER_SECURITY_RW_IHGD", "SEC_G_folder_redirection_IHGD-PS-VP-001", "Sec_G_Endobase_nonexam_IHGD",
            "ReportingGroup_test"
        ],
        "Receptionist BLS/MHP": [
            "SEC_G_License_F3", "Domain Users", "SEC_G_License_F3_TAC", "SEC_G_AOVPN_Users"
        ],
        "Service Manager": [
            "Sec_G_MRI", "SEC_G_License_E3", "SEC_G_OPERATIONS_DEPT_INSPECTION_FOLDER_STRATFORD_IHGD_RW",
            "Domain Users", "SEC_G_ALL_CLINICAL_STAFF_FOLDER_MEMBERS_RW_IHGD", "SEC_G_OPERATIONS_LONDON_RW_IHGD",
            "SEC_G_AOVPN_Users", "Sec_G_InTune_BYOD_Compliant", "SEC_G_Azure_AD_Laudio", "Sec_G_InTune_MDM_MTD_Compliant",
            "Sec_G_Clinical_Enhanced", "SEC_G_folder_redirection_IHGD-PS-VP-001", "DL_All_eReq_Users", "ReportingGroup_test"
        ],
        "Administrator and Health Care Assistant": [
            "SEC_G_Sentinel_SSO", "SEC_G_License_E3", "Domain Users", "SEC_G_AOVPN_Users", "Sec_G_Clinical_Reviewer",
            "SEC_G_OPERATIONS_UOMRI_FOLDER_SECURITY_RW_IHGD", "SEC_G_Egress_POC", "DL_All_eReq_Users", "SEC_G_UPRIGHT_BIRMINGHAM_RW"
        ],
        "Clinical Assistant": [
            "SEC_G_Sentinel_SSO", "SEC_G_License_E3", "SEC_G_MAYDAY_RW", "Domain Users", "SEC_G_AOVPN_Users", "Sec_G_InTune_BYOD_Compliant",
            "SEC_G_All_Clinical_Staff", "Sec_G_InTune_MDM_MTD_Compliant", "Sec_G_Clinical_Enhanced", "SEC_G_folder_redirection_IHGD-PS-VP-001"
        ],
        "Bank Offshore Medic": [
            "Domain Users", "SEC_G_AOVPN_Users", "SEC_G_License_EOL_Plan2"
        ]
    }

    group_list = groups.get(job_title, [])
    if group_list:
        sections.append("Groups")

    # Determine if we need to use "a" or "an"
    article = "an" if job_title and job_title[0].lower() in 'aeiou' else "a"

    # Generate the message to send to the manager
    if "@inhealthgroup.com" in user_email:
        message_to_send_manager = f"""Hello {manager.split()[0]},

Please find the login details for the new starter, {name}, who will be joining as {article} {job_title} on {start_date}.

Username: {username}
User Email: {user_email}
Password: {default_password}

Best regards,
Your IT Team"""
    else:
        message_to_send_manager = f"""Hello {manager.split()[0]},

Please find the login details for the new starter, {name}, who will be joining as {article} {job_title} on {start_date}.

Username: {username}
User Email: {user_email}
Password: {default_password}

Spectra PM Username: {first_name.lower()}{last_name[0].lower()}super
Spectra PM Password: {spectra_pm_password}

Best regards,
Your IT Team"""

    # Generate the Jira Reply message
    jira_reply = f"""Hello {manager.split()[0]},

An account for {name} has been created, and the account details have been sent to you via Teams.

Best regards,
Your IT Team"""

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
        "Groups": "\n".join(group_list),
        "Message to Send Manager": message_to_send_manager,
        "Internal Note": internal_note,
        "Jira Reply": jira_reply,
        "Sections": sections
    }

st.title('Generate User Onboarding Details')

data = st.text_area("Paste the full details here:", height=300)

if st.button('Generate Details'):
    if data:
        parsed_data = parse_input(data)
        # st.write(parsed_data)  # Debugging statement
        st.session_state.generated_data = generate_message(parsed_data)
    else:
        st.error("Please enter the required details")

if "generated_data" in st.session_state:
    sections = st.session_state.generated_data["Sections"]

    for section in sections:
        if section == "Office 365 Account":
            with st.expander(section, expanded=False):
                keys_to_display = []
                user_email = st.session_state.generated_data.get("User Email", "")
                if "@inhealthgroup.com" in user_email or "@tachealthcare.com" in user_email:
                    keys_to_display = [
                        "Candidates First Name", "Candidates Last Name", "Username", "Password", "Candidate's Full Name", "Job Title"
                    ]
                else:
                    keys_to_display = [
                        "Candidates First Name", "Candidates Last Name", "Username", "Password", 
                        "Candidate's Full Name", "Description","Job Title", "Department","Office",
                        "Manager", "Mobile", "Address", "User Email"
                    ]

                for key in keys_to_display:
                    if key in st.session_state.generated_data:
                        st.markdown(f"**{key} :**")
                        st.code(st.session_state.generated_data[key], language='plaintext')
        elif section == "Ad Account":
            with st.expander(section, expanded=False):
                keys_to_display = []
                user_email = st.session_state.generated_data.get("User Email", "")
                if "@health-intelligence.com" in user_email:
                    keys_to_display = [
                        "Candidates First Name", "Candidates Last Name", "Username", "Password", 
                        "Candidate's Full Name", "Description", "User Email", "Office", "Job Title", "Department", "Company",
                        "Manager", "\\Documents"
                    ]
                elif "@inhealthgroup.com" in user_email or "@tachealthcare.com" in user_email:
                    keys_to_display = [
                        "Candidate's Full Name", "Description", "Office", "Job Title", "Department", "Company",
                        "Manager", "\\Documents", "User Email"
                    ]
                else:
                    keys_to_display = [
                        "Candidates First Name", "Candidates Last Name", "Username", "Password", 
                        "Candidate's Full Name", "Description", "Office", "Job Title", "Department", "Company",
                        "Manager", "\\Documents", "User Email"
                    ]

                for key in keys_to_display:
                    if key in st.session_state.generated_data:
                        st.markdown(f"**{key} :**")
                        st.code(st.session_state.generated_data[key], language='plaintext')
                
                if "Groups" in st.session_state.generated_data:
                    st.markdown(f"**Groups :**")
                    st.code(st.session_state.generated_data["Groups"], language='plaintext')
        else:
            with st.expander(section, expanded=False):
                keys_to_display = []
                if section == "VPN Account":
                    keys_to_display = [
                        "Candidates First Name", "Candidates Last Name", "Username", "Password", 
                        "Candidate's Full Name", "Description", "Office", "Job Title", "Company", 
                        "Manager", "User Email"
                    ]
                elif section == "InHealth Guest Account":
                    keys_to_display = [
                        "User Email", "Candidate's Full Name"
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

    # Display Internal Note, Manager, Message to Send Manager, and Jira Reply
    st.markdown("### Manager")
    st.code(st.session_state.generated_data["Manager"], language='plaintext')

    st.markdown("### Message to Send Manager")
    st.code(st.session_state.generated_data["Message to Send Manager"], language='plaintext')

    st.markdown("### Jira Reply")
    st.code(st.session_state.generated_data["Jira Reply"], language='plaintext')

    st.markdown("### Internal Note")
    st.code(st.session_state.generated_data["Internal Note"], language='plaintext')
