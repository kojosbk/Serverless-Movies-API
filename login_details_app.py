import streamlit as st
import re
from datetime import datetime

st.set_page_config(page_title="Employee Management Tools", layout="wide")
st.title("🛠️ Employee Management Toolkit")

# Section 1: Job Change Notification Parser
with st.expander("📌 Job Change Notification Parser", expanded=False):
    notification_text = st.text_area("Paste the Employee Job Change Notification here:")

    if st.button("Generate PowerShell Files", key="job_change"):
        if not notification_text:
            st.warning("Please paste the notification text.")
        else:
            match = re.search(r"^(.*?) \(Employee reference #(\d+)\)", notification_text, re.MULTILINE)
            if match:
                employee_name = match.group(1).strip()
                employee_id = match.group(2).strip()
            else:
                st.error("Could not extract employee name.")
                st.stop()

            date_match = re.search(r'effect from (\d{2}/\d{2}/\d{4})', notification_text)

            if date_match:
                effective_date_str = date_match.group(1)
                effective_date = datetime.strptime(effective_date_str, "%d/%m/%Y")
                today = datetime.today()

                new_details_section = notification_text.split("New Job details :")[-1]

                try:
                    new_job_title = re.search(r'Job title\s*:\s*(.+)', new_details_section).group(1).strip()
                    new_department = re.search(r'Department\s*:\s*(.+)', new_details_section).group(1).strip()
                    new_manager_line = re.search(r'Reporting Line\s*:\s*(.+)', new_details_section).group(1).strip()
                    new_manager = new_manager_line.split('-')[-1].strip()
                except AttributeError:
                    st.error("Could not extract all job details. Please check the formatting.")
                    st.stop()

                username = employee_name.replace(" ", ".")
                manager_username = new_manager.replace(" ", ".")

                if effective_date > today:
                    script_filename = f"Update-{employee_name.replace(' ', '-')}-Job.ps1"
                    ps_logic = f'''# Scheduled user update for {employee_name}
$userName = "{employee_name}"
$newTitle = "{new_job_title}"
$newDepartment = "{new_department}"
$newDescription = "{new_job_title}"
$newOffice = "{new_department}"
$managerName = "{new_manager}"
$targetDate = Get-Date "{effective_date.strftime('%Y-%m-%d')}"

$today = Get-Date

if ($today -ge $targetDate) {{
    $user = Get-ADUser -Filter "Name -eq '$userName'" -Properties Title, Department, Description, Office, Manager
    if ($user) {{
        $manager = Get-ADUser -Filter "Name -eq '$managerName'"
        if ($manager) {{
            Set-ADUser -Identity $user.DistinguishedName `` 
                -Title $newTitle `` 
                -Department $newDepartment `` 
                -Description $newDescription `` 
                -Office $newOffice `` 
                -Manager $manager.DistinguishedName
            Write-Host "✅ Successfully updated job details for $userName." -ForegroundColor Green
        }} else {{
            Write-Host "❌ Manager '$managerName' not found." -ForegroundColor Red
        }}
    }} else {{
        Write-Host "❌ User '$userName' not found." -ForegroundColor Red
    }}
}} else {{
$script = @"
# Immediate update for {employee_name}
Set-ADUser -Identity "{username}" ``
    -Title "{new_job_title}" ``
    -Department "{new_department}" ``
    -Description "{new_job_title}" ``
    -Office "{new_department}" ``
    -Manager "{manager_username}"

Write-Host "✅ Job update for {employee_name} completed." -ForegroundColor Green
"@
$filePath = "$env:USERPROFILE\Documents\{script_filename}"
$script | Set-Content -Path $filePath -Encoding UTF8
Write-Host "📁 Script saved to $filePath" -ForegroundColor Cyan
Write-Host "⏳ Not yet $($targetDate.ToShortDateString()). Script will run on the effective date." -ForegroundColor Yellow
}}'''

                    st.subheader("PowerShell Script (.ps1) Content")
                    st.code(ps_logic, language='powershell')

                    escaped_script_path = f"$env:USERPROFILE\Documents\{script_filename}"
                    task_name = f"Update {employee_name} Job Details"
                    run_time = effective_date.strftime('%Y-%m-%d 09:00AM')

                    schedule_task_script = f'''# Define script path and schedule time
$scriptPath = "{escaped_script_path}"
$taskName = "{task_name}"
$runDate = Get-Date "{run_time}"

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `\"$scriptPath`\""
$trigger = New-ScheduledTaskTrigger -Once -At $runDate

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Force

Write-Host "✅ Scheduled task '$taskName' to run on $($runDate.ToString('f'))." -ForegroundColor Green'''

                    st.subheader("Scheduling Task Script")
                    st.code(schedule_task_script, language='powershell')
                else:
                    immediate_script = f'''# Immediate update for {employee_name}
Set-ADUser -Identity "{username}" ``
    -Title "{new_job_title}" ``
    -Department "{new_department}" ``
    -Description "{new_job_title}" ``
    -Office "{new_department}" ``
    -Manager "{manager_username}"

Write-Host "✅ Job update for {employee_name} completed." -ForegroundColor Green'''

                    st.subheader("PowerShell Script (.ps1) Content")
                    st.code(immediate_script, language='powershell')
            else:
                st.error("Could not extract necessary details from notification.")

# Section 3: Manager Change Parser
with st.expander("🔄 Manager Change Parser", expanded=False):
    manager_change_text = st.text_area("Paste Manager Change Notification here:")

    if st.button("Generate Manager Change PowerShell", key="manager_change"):
        if not manager_change_text:
            st.warning("Please paste the manager change notification.")
        else:
            emp_match = re.search(r"Employee Name:\s*(.+)", manager_change_text)
            id_match = re.search(r"Employee ref #\s*(\d+)", manager_change_text)
            date_match = re.search(r"Change effective from:\s*(\d{2}/\d{2}/\d{4})", manager_change_text)
            mgr_match = re.search(r"New Manager:\s*(.+)", manager_change_text)

            if emp_match and id_match and date_match and mgr_match:
                employee_name = emp_match.group(1).strip()
                employee_id = id_match.group(1).strip()
                effective_date = datetime.strptime(date_match.group(1), "%d/%m/%Y")
                new_manager = mgr_match.group(1).strip()

                username = employee_name.replace(" ", ".")
                manager_username = new_manager.replace(" ", ".")
                today = datetime.today()

                if effective_date > today:
                    scheduled_script = f'''# Scheduled manager update for {employee_name}
$userName = "{employee_name}"
$managerName = "{new_manager}"
$targetDate = Get-Date "{effective_date.strftime('%Y-%m-%d')}"
$today = Get-Date

if ($today -ge $targetDate) {{
    $user = Get-ADUser -Filter \"Name -eq '$userName'\" -Properties Manager
    if ($user) {{
        $manager = Get-ADUser -Filter \"Name -eq '$managerName'\"
        if ($manager) {{
            Set-ADUser -Identity $user.DistinguishedName ``
                -Manager $manager.DistinguishedName
            Write-Host \"✅ Updated manager for $userName.\" -ForegroundColor Green
        }} else {{
            Write-Host \"❌ Manager '$managerName' not found.\" -ForegroundColor Red
        }}
    }} else {{
        Write-Host \"❌ User '$userName' not found.\" -ForegroundColor Red
    }}
}}'''
                    st.subheader("PowerShell Script (.ps1) Content")
                    st.code(scheduled_script, language='powershell')

                    script_filename = f"Update-{employee_name.replace(' ', '-')}-Manager.ps1"
                    escaped_script_path = f"$env:USERPROFILE\Documents\{script_filename}"
                    task_name = f"Update {employee_name} Manager"
                    run_time = effective_date.strftime('%Y-%m-%d 09:00AM')

                    schedule_task_script = f'''# Define script path and schedule time
$scriptPath = "{escaped_script_path}"
$taskName = "{task_name}"
$runDate = Get-Date "{run_time}"

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `\"$scriptPath`\""
$trigger = New-ScheduledTaskTrigger -Once -At $runDate

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Force

Write-Host "✅ Scheduled task '$taskName' to run on $($runDate.ToString('f'))." -ForegroundColor Green'''
                    st.subheader("Scheduling Task Script")
                    st.code(schedule_task_script, language='powershell')

                else:
                    immediate_script = f'''# Immediate manager update for {employee_name}
Set-ADUser -Identity "{username}" ``
    -Manager "{manager_username}"

Write-Host "✅ Updated manager for {employee_name}." -ForegroundColor Green'''


                    st.subheader("PowerShell Script (.ps1) Content")
                    st.code(immediate_script, language='powershell')
            else:
                st.error("Could not extract all necessary manager change details.")
with st.expander("🛑 Leaver Notification Parser", expanded=False):
    leaver_text = st.text_area("Paste Leaver Notification here:")

    if st.button("Generate Disable User PowerShell", key="disable_user"):
        if not leaver_text:
            st.warning("Please paste the leaver notification.")
        else:
            emp_match = re.search(r"^(.*?) has been made a leaver", leaver_text)
            id_match = re.search(r"Employee Reference #:\s*(\d+)", leaver_text)
            date_match = re.search(r"Leaving Date:\s*(\d{2}/\d{2}/\d{4})", leaver_text)
            mgr_match = re.search(r"Reporting Manager:\s*(.+)", leaver_text)

            if emp_match and id_match and date_match and mgr_match:
                employee_name = emp_match.group(1).strip()
                leaving_date = datetime.strptime(date_match.group(1), "%d/%m/%Y")
                sam_account_name = employee_name.lower().replace(" ", ".")
                today = datetime.today()
                date_string = leaving_date.strftime("%d/%m/%Y")
                filename_suffix = employee_name.replace(" ", "-")
                script_filename = f"Disable-{filename_suffix}.ps1"
                ou_path = "OU=Disabled to Delete,OU=IHGD HouseKeeping,OU=IHGD Internal,DC=ihgd,DC=inhealthgroup,DC=com"
                description_suffix = f"Leaving Date: {date_string}"

                ps_script_content = rf"""$samAccountName = "{sam_account_name}"

try {{
    $user = Get-ADUser -Identity $samAccountName -Properties Description, DistinguishedName

    if ($user) {{
        $existingDesc = $user.Description
        $leavingNote = "{description_suffix}"

        if ([string]::IsNullOrWhiteSpace($existingDesc)) {{
            $updatedDesc = $leavingNote
        }} else {{
            $updatedDesc = "$existingDesc - $leavingNote"
        }}

        Set-ADUser -Identity $user.DistinguishedName -Description $updatedDesc
        Set-ADUser -Identity $user.DistinguishedName -Enabled $false
        Move-ADObject -Identity $user.DistinguishedName -TargetPath "{ou_path}"

        Write-Host "✅ User '$samAccountName' disabled and moved." -ForegroundColor Green
    }}
}}
catch {{
    Write-Host "❌ User '$samAccountName' not found or an error occurred." -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor DarkRed
}}"""

                if leaving_date > today:
                    st.subheader("PowerShell Script (.ps1) Content")
                    st.code(ps_script_content, language='powershell')

                    schedule_script = rf"""# Save script and schedule for future execution
$scriptContent = @"
{ps_script_content}
"@

$scriptPath = "$env:USERPROFILE\Documents\{script_filename}"
$scriptContent | Set-Content -Path $scriptPath -Encoding UTF8

$taskName = "Disable {employee_name} Account"
$runDate = Get-Date "{leaving_date.strftime('%Y-%m-%d')} 20:00"

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Once -At $runDate

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Force

Write-Host "✅ Scheduled disable task for {employee_name} on $($runDate.ToString('f'))" -ForegroundColor Green"""

                    st.subheader("Task Scheduler Script")
                    st.code(schedule_script, language='powershell')

                else:
                    st.subheader("PowerShell Script (.ps1) Content")
                    st.code(ps_script_content, language='powershell')

            else:
                st.error("Could not extract all necessary leaver details.")
# ------------------------------
# Section 4: m1
# ------------------------------

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

# Spectra PM Username: {first_name.lower()}{last_name[0].lower()}super
# Spectra PM Password: {spectra_pm_password}

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
