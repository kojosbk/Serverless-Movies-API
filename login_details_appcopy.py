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
            pass
    return data

def capitalize_name(name):
    return " ".join(word.capitalize() for word in name.split())

def generate_password_from_name(first_name, last_name):
    first_part = first_name.lower()[:3]
    last_part = last_name.lower()[:3]
    password = generate_password_from_env()
    return password.capitalize()

def generate_message(data):
    manager_name = capitalize_name(data.get("Hiring Manager Name", ""))
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
    default_password = generate_password_from_name(first_name, last_name)
    spectra_pm_password = SPECTRA_DEFAULT_PASSWORD

    manager_parts = manager_name.split()
    manager_username = f"{manager_parts[0].lower()}.{manager_parts[-1].lower()}" if len(manager_parts) >= 2 else manager_parts[0].lower()

    permissions = []
    if data.get("Access Permissions for XRM", "").lower() != "no" and data.get("Access Permissions for XRM", "").strip():
        permissions.append("XRM")
    if data.get("Access to Standard Applications - Iris", "").lower() != "no" and data.get("Access to Standard Applications - Iris", "").strip():
        permissions.append("IRIS")

    ad_create_script = ""
    ad_update_script = ""

    if "Health Intelligence" in data.get("Company Registered Number", ""):
        user_email = f"{username}@inhealthgroup.com"
        company_display = "Health Intelligence"
        ad_create_script = f"""```powershell
if (-not (Get-ADUser -Filter {{SamAccountName -eq '{username}'}})) {{
    New-ADUser -Name \"{name}\" `
        -SamAccountName \"{username}\" `
        -GivenName \"{first_name}\" `
        -Surname \"{last_name}\" `
        -DisplayName \"{name}\" `
        -Description \"{job_title}\" `
        -Title \"{job_title}\" `
        -Department \"{company_name}\" `
        -Office \"{location}\" `
        -EmailAddress \"{username}@inhealthgroup.com\" `
        -Path \"OU=AHW DESP,OU=HIUsers,DC=hi,DC=int\" `
        -Company \"Health-Intelligence\" `
        -Manager \"{manager_username}\" `
        -AccountPassword (ConvertTo-SecureString \"{default_password}\" -AsPlainText -Force) `
        -employeeNumber \"{data.get('Unique Identifier - Candidate ID', '')}\" `
        -Enabled $true
}} else {{ Write-Host \"User {username} already exists.\" }}
```
```"""
        ad_update_script = f"""```powershell
Set-ADUser -Identity \"{username}\" `
    -employeeNumber \"{data.get('Unique Identifier - Candidate ID', '')}\" `
    -employeeNumber \"{data.get('Unique Identifier - Candidate ID', '')}\" `\"{username}\" `
    -Title \"{job_title}\" `
    -Department \"{company_name}\" `
    -Manager \"{manager_username}\" `
    -Description \"{job_title}\" `
    -Office \"{location}\" `
    -EmailAddress \"{username}@inhealthgroup.com\" `
    -employeeNumber \"{data.get('Unique Identifier - Candidate ID', '')}\" `
    -Company \"Inhealthgroup\"
```"""
        sections = [
            "VPN Account", 
            "Office 365 Account", 
            "Ad Account",            
            "Spectra PM", 
            "8x8 VCC Account"
        ]
    elif "TAC Healthcare" in data.get("Company Registered Number", ""):
        user_email = f"{username}@tachealthcare.com"
        company_display = "TAC Healthcare"
        ad_update_script = f"""```powershell
Set-ADUser -Identity \"{username}\" `
    -Title \"{job_title}\" `
    -Department \"{company_name}\" `
    -Manager \"{manager_username}\" `
    -Description \"{job_title}\" `
    -employeeNumber \"{data.get('Unique Identifier - Candidate ID', '')}\" `
    -Office \"{location}\" `
    -EmailAddress \"{username}@tachealthcare.com\" `
    -Company \"{company_display}\"
```"""
        sections = ["Office 365 Account", "Ad Account"]
    else:
        user_email = f"{username}@inhealthgroup.com"
        company_display = "InHealth Group"
        ad_update_script = f"""```powershell
Set-ADUser -Identity \"{username}\" `
    -Title \"{job_title}\" `
    -Department \"{company_name}\" `
    -Manager \"{manager_username}\" `
    -Description \"{job_title}\" `
    -Office \"{location}\" `
    -employeeNumber \"{data.get('Unique Identifier - Candidate ID', '')}\" `
    -EmailAddress \"{username}@inhealthgroup.com\" `
    -Company \"{company_display}\"
```"""
        sections = ["Office 365 Account", "Ad Account"]

    if permissions:
        sections.append("Permissions")

    article = "an" if job_title and job_title[0].lower() in 'aeiou' else "a"

    message_to_send_manager = f"""Hello {manager_name.split()[0]},

Please find the login details for the new starter, {name}, who will be joining as {article} {job_title} on {start_date}.

Username: {username}
User Email: {user_email}
Password: {default_password}

Spectra PM Username: {first_name.lower()}{last_name[0].lower()}super
Spectra PM Password: {spectra_pm_password}

Best regards,
Your IT Team"""

    jira_reply = f"""Hello {manager_name.split()[0]},

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
        "Manager": manager_name,
        "PowerShell script to Update the attributes create": ad_create_script,
        "PowerShell script to Update the attributes update": ad_update_script,
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
        "Jira Reply": jira_reply,
        "Sections": sections
    }

def main():
    st.title("M1 to User Onboarding Details Generator")

    st.write("Paste your M1 formatted data below:")
    m1_input = st.text_area("M1 Input", height=400)

    if st.button("Convert and Generate Details"):
        if m1_input.strip():
            data = parse_m1(m1_input)
            generated_data = generate_message(data)
            sections = generated_data["Sections"]

            for section in sections:
                with st.expander(section, expanded=False):
                    keys_to_display = []
                    if section == "Office 365 Account":
                        keys_to_display = [
                            "Candidates First Name", "Candidates Last Name", "Username", "Password", "Candidate's Full Name", "Job Title"
                        ]
                    elif section == "Ad Account":
                        keys_to_display = [
                            "Candidate's Full Name", "Description", "Office", "Job Title", "Department", "Company",
                            "Manager", "PowerShell script to Update the attributes update", "User Email"
                        ]
                        if generated_data.get("PowerShell script to Update the attributes create"):
                            keys_to_display.insert(7, "PowerShell script to Update the attributes create")
                    elif section == "VPN Account":
                        keys_to_display = [
                            "Candidates First Name", "Candidates Last Name", "Username", "Password", 
                            "Candidate's Full Name", "Description", "Office", "Job Title", "Company", 
                            "Manager", "User Email"
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
                        keys_to_display = ["Permissions"]

                    for key in keys_to_display:
                        if key in generated_data:
                            st.markdown(f"**{key} :**")
                            if "PowerShell script to Update the attributes" in key:
                                st.markdown(generated_data[key])
                            else:
                                st.code(generated_data[key], language='plaintext')

            st.markdown("### Manager")
            st.code(generated_data["Manager"], language='plaintext')

            st.markdown("### Message to Send Manager")
            st.code(generated_data["Message to Send Manager"], language='plaintext')

            st.markdown("### Jira Reply")
            st.code(generated_data["Jira Reply"], language='plaintext')
        else:
            st.error("Please enter the required details")

if __name__ == "__main__":
    main()
