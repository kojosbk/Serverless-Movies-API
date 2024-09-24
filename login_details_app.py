import streamlit as st
import re
import secrets
import string

def parse_m1(text):
    data = {}
    lines = text.strip().split('\n')
    for line in lines:
        if line.strip() == '':
            continue
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            data[key] = value
        elif '\t' in line:
            key_value = line.split('\t')
            key = key_value[0].strip()
            value = key_value[-1].strip()
            data[key] = value
        else:
            # It's a section header; we can ignore it or keep track of it if needed
            pass
    return data

def format_m2(data):
    candidate_name = data.get('Candidate Name', '')
    candidate_job_title = data.get('Candidate Job Title', '')
    start_date = data.get('Start Date', '')
    end_date = data.get('End Date', '')
    internal_candidate = data.get('Internal Candidate?', '')
    bank_to_perm = data.get('Is this candidate Bank to perm, per...', '')
    professional_number = data.get('Professional Membership Number:', '')
    user_name = data.get('Username for IT (Max 21 characters)...', '')
    user_email = data.get('User Email for IT (user name will b...', '')

    hiring_manager = data.get('Hiring Manager Name', '')
    reference = data.get('Reference', '')
    company_name = data.get('Company Name', '')
    location = data.get('Location', '')
    cost_code = data.get('Cost Code', '')
    registered_number = data.get('Company Registered Number', '')

    delivery_address = data.get('Delivery address for any hardware:', '')
    scheduled = data.get('Does this person need to be scheduled...','')
    nhs_email = data.get('Does this person need an NHS Email ...', '')
    access_shared = data.get('Does this person need access to a s...', '')
    shared_inbox = data.get('Shared NHS Inbox Details:', '')
    email_distribution = data.get('Please specify any email distributi...', '')
    security_groups = data.get('Please list the security groups req...', '')
    telephone = data.get('Telephone:', '')
    standard_hardware = data.get('Standard Hardware:', '')
    additional_software = data.get('Additional Standard Software Instal...', '')
    non_standard_software = data.get('Non Standard Software Installations...', '')
    non_standard_software_details = data.get('Non Standard Software Installation ...', '')

    # Now format the output
    output = f"""### Offer Details 
**Candidate Name:** {candidate_name}  
**Candidate Job Title:** {candidate_job_title}  
**Start Date:** {start_date}  
**End Date (if applicable):** {end_date}  
**Internal Candidate?** {internal_candidate}  
**Is this candidate Bank to Perm or Perm to Bank:** {bank_to_perm}  
**Professional Membership Number:** {professional_number}  

**User Name:** {user_name}  
**User Email:** {user_email}  

### Company Details 
**Hiring Manager Name:** {hiring_manager}  
**Reference:** {reference}  
**Company Name:** {company_name}  
**Location:** {location}  
**Cost Code:** {cost_code}  
**Company Registered Number:** {registered_number}  

### IT Starter Form 
**Delivery Address for any Hardware:** {delivery_address}  
**Does this person need to be scheduled... :** {scheduled}  
**Does this person need an NHS email.... :** {nhs_email}  
**Does this person need access to a s.... :** {access_shared}  
**Shared NHS Inbox details:** {shared_inbox}  
**Please specify any email distribution.... :** {email_distribution}  
**Please list the security groups req.... :** {security_groups}  
**Telephone:** {telephone}  
**Standard Hardware:** {standard_hardware}  
**Additional Standard Software Instal.... :** {additional_software}  
**Non Standard Software Installation ... :** {non_standard_software}  
**Non Standard Software Installation ....:** {non_standard_software_details}  
**Access to Standard Applications - 2Scedule:**  
**2Scedule Additional Comments:**  
**Access to Standard Applications - Auditbase:**  
**Auditbase Additional Comments:**  
**Access to Standard Applications - CardioPerfect:**  
**CardioPerfect Additional Comments:**  
**Access to Standard Applications - Docman:**  
**Docman Additional Comments:**  
**Access to Standard Applications - Endobase:**  
**Endobase Additional Comments:**  
**Access to Standard Applications - Great Plains:**  
**Great Plains Additional Comments:**  
**Access to Standard Applications - Iris:**  
**Iris Additional Comments:**  
**Access to Standard Applications - Kimera:**  
**Kimera Additional Comments:**  
**Access to Standard Applications - Sectra:**  
**Sectra Additional Comments:**  
**Access to Standard Applications - XRM:**  
**XRM Clinic Portal:**  
**Access Permissions for XRM:**  
**XRM Additional Comments:**  

**Additional Notes for the IT Service Desk:**  
"""
    return output

def capitalize_name(name):
    return " ".join(word.capitalize() for word in name.split())

def generate_password_from_name(first_name, last_name):
    first_part = first_name.lower()[:3]
    last_part = last_name.lower()[:3]
    password = generate_password_from_env()
    return password.capitalize()

def generate_spectra_pm_password(first_name, last_name):
    first3_first = first_name.lower()[:3]
    last3_last = last_name.lower()[-3:]
    last3_first = first_name.lower()[-3:]
    first3_last = last_name.lower()[:3]
    password = f"{first3_first}{last3_last}#2024{last3_first}{first3_last}"
    return password.capitalize()

def generate_message(data):
    manager = capitalize_name(data.get("Hiring Manager Name", ""))
    name = capitalize_name(data.get("Candidate Name", ""))
    job_title = data.get("candidate Job Title", "") or data.get("Candidate Job Title", "")
    location = data.get("Location", "")
    telephone = data.get("Candidate Mobile Number", "")
    address = data.get("Candidate Address", "")
    company_name = data.get("Company Name", "")
    start_date = data.get("Start Date", "")

    names = name.split()
    first_name = names[0] if names else ""
    last_name = names[-1] if names else ""
    
    username = f"{first_name.lower()}.{last_name.lower()}"
    
    # Generate passwords with the first letter capitalized
    default_password = generate_password_from_name(first_name, last_name)
    spectra_pm_password = generate_spectra_pm_password(first_name, last_name)

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
        "Users Organization": "O0 - InHealth Intelligence Ltd",
        "Spectra PM Password": spectra_pm_password,
        "NHS Email": "nomail@nhs.net",
        "Permissions": ", ".join(permissions),
        "Message to Send Manager": message_to_send_manager,
        "Internal Note": internal_note,
        "Jira Reply": jira_reply,
        "Sections": sections
    }

def main():
    st.title("M1 to M2 Format Converter and User Onboarding Details")

    st.write("Paste your M1 formatted data below:")
    m1_input = st.text_area("M1 Input", height=400)

    if st.button("Convert and Generate Details"):
        if m1_input.strip():
            data = parse_m1(m1_input)
            m2_output = format_m2(data)
            st.write("Converted M2 format:")
            # st.markdown(m2_output)

            generated_data = generate_message(data)
            sections = generated_data["Sections"]

            for section in sections:
                if section == "Office 365 Account":
                    with st.expander(section, expanded=False):
                        keys_to_display = []
                        user_email = generated_data.get("User Email", "")
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
                            if key in generated_data:
                                st.markdown(f"**{key} :**")
                                st.code(generated_data[key], language='plaintext')
                elif section == "Ad Account":
                    with st.expander(section, expanded=False):
                        keys_to_display = []
                        user_email = generated_data.get("User Email", "")
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
                            if key in generated_data:
                                st.markdown(f"**{key} :**")
                                st.code(generated_data[key], language='plaintext')
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
                                "Candidates First Name", "Candidates Last Name", "Spectra PM Username", "Users Organization", "Spectra PM Password", "NHS Email"
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
                            if key in generated_data:
                                st.markdown(f"**{key} :**")
                                st.code(generated_data[key], language='plaintext')

            # Display Internal Note, Manager, Message to Send Manager, and Jira Reply
            st.markdown("### Manager")
            st.code(generated_data["Manager"], language='plaintext')

            st.markdown("### Message to Send Manager")
            st.code(generated_data["Message to Send Manager"], language='plaintext')

            st.markdown("### Jira Reply")
            st.code(generated_data["Jira Reply"], language='plaintext')

            st.markdown("### Internal Note")
            st.code(generated_data["Internal Note"], language='plaintext')
        else:
            st.error("Please enter the required details")

if __name__ == "__main__":
    main()
