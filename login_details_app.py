"""
Employee Management Toolkit - Improved Version
===============================================
A Streamlit application for automating HR and IT tasks including:
- Job change notifications
- Manager changes  
- Employee offboarding
- New employee onboarding

Key Improvements:
- Better code organization with helper functions
- Enhanced error handling and validation
- Improved security features
- Better UI/UX with download buttons
- Comprehensive documentation
- Fixed logic bugs

Author: Employee Management Team
Last Updated: October 2025
"""

import streamlit as st
import re
from datetime import datetime
from typing import Dict, Optional, Tuple, List
import secrets
import string
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# ============================================================================
# CONSTANTS
# ============================================================================

# Helper function to get config from either .env or Streamlit secrets
def get_config(key: str, default: str = "") -> str:
    """Get configuration from environment variables or Streamlit secrets."""
    # Try environment variable first (from .env)
    value = os.getenv(key)
    if value:
        return value
    
    # Try Streamlit secrets (for Streamlit Cloud deployment)
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    
    # Return default if neither found
    return default

# Active Directory Configuration
AD_DISABLED_OU = get_config("AD_DISABLED_OU", "OU=Disabled to Delete,OU=IHGD HouseKeeping,OU=IHGD Internal,DC=ihgd,DC=inhealthgroup,DC=com")
AD_HI_USER_PATH = get_config("AD_HI_USER_PATH", "OU=AHW DESP,OU=HIUsers,DC=hi,DC=int")
AD_IHI_DISABLED_OU = get_config("AD_IHI_DISABLED_OU", "OU=Leavers,OU=Disabled,OU=HIUsers,DC=hi,DC=int")

# Password Configuration (loaded from environment variables or Streamlit secrets)
XRM_DEFAULT_PASSWORD = get_config("XRM_DEFAULT_PASSWORD", "****")
SPECTRA_DEFAULT_PASSWORD = get_config("SPECTRA_DEFAULT_PASSWORD", "****")
DEFAULT_PASSWORD_SUFFIX = get_config("DEFAULT_PASSWORD_SUFFIX", "#24")

# Company Configuration
COMPANY_CONFIGS = {
    "Health Intelligence": {
        "email_domain": "@inhealthgroup.com",
        "display_name": "InHealth Group",
        "ad_path": AD_HI_USER_PATH,
        "sections": ["Office 365 Account", "Ad Account", "Spectra PM", "8x8 VCC Account"]
    },
    "TAC Healthcare": {
        "email_domain": "@tachealthcare.com",
        "display_name": "TAC Healthcare",
        "ad_path": None,
        "sections": ["Office 365 Account", "Ad Account"]
    },
    "InHealth Group": {
        "email_domain": "@inhealthgroup.com",
        "display_name": "InHealth Group",
        "ad_path": None,
        "sections": ["Office 365 Account", "Ad Account"]
    }
}

# Default scheduling times for automated tasks
DEFAULT_TASK_TIME = "09:00AM"
LEAVER_TASK_TIME = "20:00"

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Employee Management Toolkit",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
    }
    .stDownloadButton button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🛠️ Employee Management Toolkit</h1>', unsafe_allow_html=True)
st.markdown("*Automate employee lifecycle management with ease*")
st.markdown("---")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def sanitize_username(name: str) -> str:
    """Convert a full name to a username format (firstname.lastname), using only first and last name."""
    if not name:
        return ""
    name_parts = name.strip().split()
    if len(name_parts) == 0:
        return ""
    elif len(name_parts) == 1:
        return name_parts[0].lower()
    else:
        # Only use first and last name, ignore middle names
        return f"{name_parts[0]}.{name_parts[-1]}".lower()

def validate_date_format(date_str: str, format_str: str = "%d/%m/%Y") -> Optional[datetime]:
    """Validate and parse a date string."""
    try:
        return datetime.strptime(date_str, format_str)
    except (ValueError, TypeError):
        return None

def create_download_button(content: str, filename: str, label: str, file_type: str = "text") -> None:
    """Create a download button for script content."""
    st.download_button(
        label=f"⬇️ {label}",
        data=content,
        file_name=filename,
        mime="text/plain" if file_type == "text" else "application/octet-stream",
        use_container_width=True
    )

def display_script_with_download(script_content: str, title: str, filename: str) -> None:
    """Display PowerShell script with syntax highlighting and download button."""
    st.subheader(title)
    st.code(script_content, language='powershell')
    create_download_button(script_content, filename, f"Download {filename}")

def generate_secure_password(length: int = 12) -> str:
    """Generate a secure random password."""
    characters = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(characters) for _ in range(length))

def capitalize_name(name: str) -> str:
    """Properly capitalize a person's name."""
    if not name:
        return ""
    return " ".join(word.capitalize() for word in name.split())

# ============================================================================
# JOB CHANGE NOTIFICATION PARSER
# ============================================================================

def parse_job_change_notification(notification_text: str) -> Optional[Dict]:
    """
    Parse job change notification and extract relevant details.
    
    Args:
        notification_text: Raw notification text
        
    Returns:
        Dictionary with parsed details or None if parsing fails
    """
    try:
        # Extract employee name and ID
        employee_match = re.search(r"^(.*?) \(Employee reference #(\d+)\)", notification_text, re.MULTILINE)
        if not employee_match:
            return None
        
        employee_name = employee_match.group(1).strip()
        employee_id = employee_match.group(2).strip()
        
        # Extract first and last name only (ignore middle names)
        employee_name_parts = employee_name.split()
        if len(employee_name_parts) > 2:
            employee_name = f"{employee_name_parts[0]} {employee_name_parts[-1]}"
        
        # Extract effective date
        date_match = re.search(r'effect from (\d{2}/\d{2}/\d{4})', notification_text)
        if not date_match:
            return None
        
        effective_date = validate_date_format(date_match.group(1))
        if not effective_date:
            return None
        
        # Extract new job details
        new_details_section = notification_text.split("New Job details :")[-1]
        
        job_title_match = re.search(r'Job title\s*:\s*(.+)', new_details_section)
        department_match = re.search(r'Department\s*:\s*(.+)', new_details_section)
        manager_match = re.search(r'Reporting Line\s*:\s*(.+)', new_details_section)
        
        if not all([job_title_match, department_match, manager_match]):
            return None
        
        new_job_title = job_title_match.group(1).strip()
        new_department = department_match.group(1).strip()
        manager_line = manager_match.group(1).strip()
        new_manager = manager_line.split('-')[-1].strip()
        
        # Extract first and last name only for manager (ignore middle names)
        manager_name_parts = new_manager.split()
        if len(manager_name_parts) > 2:
            new_manager = f"{manager_name_parts[0]} {manager_name_parts[-1]}"
        
        return {
            'employee_name': employee_name,
            'employee_id': employee_id,
            'effective_date': effective_date,
            'new_job_title': new_job_title,
            'new_department': new_department,
            'new_manager': new_manager,
            'username': sanitize_username(employee_name),
            'manager_username': sanitize_username(new_manager)
        }
    except Exception as e:
        st.error(f"Error parsing notification: {str(e)}")
        return None

def generate_job_change_script(details: Dict, is_scheduled: bool = False) -> str:
    """Generate PowerShell script for job change."""
    if is_scheduled:
        return f'''# Scheduled user update for {details['employee_name']}
$userName = "{details['employee_name']}"
$newTitle = "{details['new_job_title']}"
$newDepartment = "{details['new_department']}"
$newDescription = "{details['new_job_title']}"
$newOffice = "{details['new_department']}"
$managerName = "{details['new_manager']}"
$targetDate = Get-Date "{details['effective_date'].strftime('%Y-%m-%d')}"

$today = Get-Date

if ($today -ge $targetDate) {{
    try {{
        $user = Get-ADUser -Filter "Name -eq '$userName'" -Properties Title, Department, Description, Office, Manager -ErrorAction Stop
        
        if ($user) {{
            $manager = Get-ADUser -Filter "Name -eq '$managerName'" -ErrorAction Stop
            
            if ($manager) {{
                Set-ADUser -Identity $user.DistinguishedName `
                    -Title $newTitle `
                    -Department $newDepartment `
                    -Description $newDescription `
                    -Office $newOffice `
                    -Manager $manager.DistinguishedName `
                    -ErrorAction Stop
                    
                Write-Host "✅ Successfully updated job details for $userName." -ForegroundColor Green
            }} else {{
                Write-Host "❌ Manager '$managerName' not found." -ForegroundColor Red
            }}
        }} else {{
            Write-Host "❌ User '$userName' not found." -ForegroundColor Red
        }}
    }} catch {{
        Write-Host "❌ Error updating user: $_" -ForegroundColor Red
    }}
}} else {{
    Write-Host "⏳ Not yet $($targetDate.ToShortDateString()). Current date: $($today.ToShortDateString())" -ForegroundColor Yellow
}}'''
    else:
        return f'''# Immediate update for {details['employee_name']}
try {{
    $user = Get-ADUser -Filter "SamAccountName -eq '{details['username']}'" -ErrorAction Stop
    
    if ($user) {{
        $manager = Get-ADUser -Filter "SamAccountName -eq '{details['manager_username']}'" -ErrorAction Stop
        
        if ($manager) {{
            Set-ADUser -Identity $user.DistinguishedName `
                -Title "{details['new_job_title']}" `
                -Department "{details['new_department']}" `
                -Description "{details['new_job_title']}" `
                -Office "{details['new_department']}" `
                -Manager $manager.DistinguishedName `
                -ErrorAction Stop
                
            Write-Host "✅ Job update for {details['employee_name']} completed." -ForegroundColor Green
        }} else {{
            Write-Host "❌ Manager not found." -ForegroundColor Red
        }}
    }} else {{
        Write-Host "❌ User not found." -ForegroundColor Red
    }}
}} catch {{
    Write-Host "❌ Error: $_" -ForegroundColor Red
}}'''

def generate_scheduled_task_script(script_filename: str, task_name: str, run_time: str) -> str:
    """Generate PowerShell script to create a scheduled task."""
    return f'''# Create scheduled task for automated execution
$scriptPath = "$env:USERPROFILE\\Documents\\{script_filename}"
$taskName = "{task_name}"
$runDate = Get-Date "{run_time}"

try {{
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""
    $trigger = New-ScheduledTaskTrigger -Once -At $runDate
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Force -ErrorAction Stop
    
    Write-Host "✅ Scheduled task '$taskName' created successfully." -ForegroundColor Green
    Write-Host "📅 Task will run on: $($runDate.ToString('f'))" -ForegroundColor Cyan
}} catch {{
    Write-Host "❌ Error creating scheduled task: $_" -ForegroundColor Red
}}'''

# Section 1: Job Change Notification Parser
with st.expander("📌 Job Change Notification Parser", expanded=False):
    st.markdown("""
    **Instructions:** Paste the employee job change notification text below.
    The system will extract details and generate the appropriate PowerShell scripts.
    """)
    
    notification_text = st.text_area(
        "Paste the Employee Job Change Notification here:",
        height=200,
        help="Copy and paste the entire job change notification email or document",
        key="job_change_text"
    )

    if st.button("🚀 Generate PowerShell Scripts", key="job_change", type="primary"):
        if not notification_text.strip():
            st.warning("⚠️ Please paste the notification text before generating scripts.")
        else:
            with st.spinner("🔄 Parsing notification..."):
                details = parse_job_change_notification(notification_text)
            
            if not details:
                st.error("❌ Could not extract employee details. Please check the notification format.")
                st.info("""
                **Expected format:**
                - Employee name and reference number
                - Effective date (DD/MM/YYYY format)
                - New Job details section with Job title, Department, and Reporting Line
                """)
            else:
                today = datetime.today()
                is_future = details['effective_date'] > today
                
                # Display extracted information
                st.success("✅ Successfully parsed notification!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Employee", details['employee_name'])
                    st.metric("Employee ID", details['employee_id'])
                with col2:
                    st.metric("New Job Title", details['new_job_title'])
                    st.metric("Department", details['new_department'])
                with col3:
                    st.metric("New Manager", details['new_manager'])
                    st.metric("Effective Date", details['effective_date'].strftime('%d/%m/%Y'))
                
                st.markdown("---")
                
                # Generate appropriate scripts
                script_filename = f"Update-{details['employee_name'].replace(' ', '-')}-Job.ps1"
                job_script = generate_job_change_script(details, is_scheduled=is_future)
                
                if is_future:
                    days_until = (details['effective_date'] - today).days
                    st.info(f"📅 This change is scheduled for the future ({days_until} days from now)")
                    
                    display_script_with_download(
                        job_script,
                        "📄 Job Update PowerShell Script",
                        script_filename
                    )
                    
                    st.markdown("---")
                    
                    task_name = f"Update {details['employee_name']} Job Details"
                    run_time = details['effective_date'].strftime(f'%Y-%m-%d {DEFAULT_TASK_TIME}')
                    schedule_script = generate_scheduled_task_script(script_filename, task_name, run_time)
                    
                    display_script_with_download(
                        schedule_script,
                        "⏰ Task Scheduler Script",
                        f"Schedule-{details['employee_name'].replace(' ', '-')}-Job.ps1"
                    )
                    
                    st.warning("⚠️ **Important:** Save the job update script to your Documents folder first, then run the scheduler script.")
                else:
                    st.info("⚡ This change is effective immediately")
                    display_script_with_download(
                        job_script,
                        "📄 Immediate Job Update Script",
                        script_filename
                    )

# ============================================================================
# MANAGER CHANGE PARSER
# ============================================================================

def parse_manager_change_notification(text: str) -> Optional[Dict]:
    """Parse manager change notification and extract details."""
    try:
        emp_match = re.search(r"Employee Name:\s*(.+)", text)
        id_match = re.search(r"Employee ref #\s*(\d+)", text)
        date_match = re.search(r"Change effective from:\s*(\d{2}/\d{2}/\d{4})", text)
        mgr_match = re.search(r"New Manager:\s*(.+)", text)

        if not all([emp_match, id_match, date_match, mgr_match]):
            return None

        effective_date = validate_date_format(date_match.group(1))
        if not effective_date:
            return None

        employee_name = emp_match.group(1).strip()
        new_manager = mgr_match.group(1).strip()
        
        # Extract first and last name only (ignore middle names)
        employee_name_parts = employee_name.split()
        if len(employee_name_parts) > 2:
            employee_name = f"{employee_name_parts[0]} {employee_name_parts[-1]}"
        
        manager_name_parts = new_manager.split()
        if len(manager_name_parts) > 2:
            new_manager = f"{manager_name_parts[0]} {manager_name_parts[-1]}"
        
        return {
            'employee_name': employee_name,
            'employee_id': id_match.group(1).strip(),
            'effective_date': effective_date,
            'new_manager': new_manager,
            'username': sanitize_username(employee_name),
            'manager_username': sanitize_username(new_manager)
        }
    except Exception as e:
        st.error(f"Error parsing manager change: {str(e)}")
        return None

def generate_manager_change_script(details: Dict, is_scheduled: bool = False) -> str:
    """Generate PowerShell script for manager change."""
    if is_scheduled:
        return f'''# Scheduled manager update for {details['employee_name']}
$userName = "{details['employee_name']}"
$managerName = "{details['new_manager']}"
$targetDate = Get-Date "{details['effective_date'].strftime('%Y-%m-%d')}"
$today = Get-Date

if ($today -ge $targetDate) {{
    try {{
        $user = Get-ADUser -Filter "Name -eq '$userName'" -Properties Manager -ErrorAction Stop
        
        if ($user) {{
            $manager = Get-ADUser -Filter "Name -eq '$managerName'" -ErrorAction Stop
            
            if ($manager) {{
                Set-ADUser -Identity $user.DistinguishedName `
                    -Manager $manager.DistinguishedName `
                    -ErrorAction Stop
                    
                Write-Host "✅ Updated manager for $userName." -ForegroundColor Green
            }} else {{
                Write-Host "❌ Manager '$managerName' not found." -ForegroundColor Red
            }}
        }} else {{
            Write-Host "❌ User '$userName' not found." -ForegroundColor Red
        }}
    }} catch {{
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }}
}} else {{
    Write-Host "⏳ Not yet $($targetDate.ToShortDateString()). Current date: $($today.ToShortDateString())" -ForegroundColor Yellow
}}'''
    else:
        return f'''# Immediate manager update for {details['employee_name']}
try {{
    $user = Get-ADUser -Filter "SamAccountName -eq '{details['username']}'" -ErrorAction Stop
    
    if ($user) {{
        $manager = Get-ADUser -Filter "SamAccountName -eq '{details['manager_username']}'" -ErrorAction Stop
        
        if ($manager) {{
            Set-ADUser -Identity $user.DistinguishedName `
                -Manager $manager.DistinguishedName `
                -ErrorAction Stop
                
            Write-Host "✅ Updated manager for {details['employee_name']}." -ForegroundColor Green
        }} else {{
            Write-Host "❌ Manager not found." -ForegroundColor Red
        }}
    }} else {{
        Write-Host "❌ User not found." -ForegroundColor Red
    }}
}} catch {{
    Write-Host "❌ Error: $_" -ForegroundColor Red
}}'''

# Section 2: Manager Change Parser
with st.expander("🔄 Manager Change Parser", expanded=False):
    st.markdown("""
    **Instructions:** Paste the manager change notification text below.
    The parser will extract employee and manager information to generate update scripts.
    """)
    
    manager_change_text = st.text_area(
        "Paste Manager Change Notification here:",
        height=200,
        help="Include Employee Name, Employee ref #, Change effective date, and New Manager",
        key="manager_change_text"
    )

    if st.button("🚀 Generate Manager Change Scripts", key="manager_change", type="primary"):
        if not manager_change_text.strip():
            st.warning("⚠️ Please paste the manager change notification.")
        else:
            with st.spinner("🔄 Parsing notification..."):
                details = parse_manager_change_notification(manager_change_text)
            
            if not details:
                st.error("❌ Could not extract manager change details. Please check the notification format.")
                st.info("""
                **Expected format:**
                - Employee Name: [Name]
                - Employee ref #: [ID]
                - Change effective from: DD/MM/YYYY
                - New Manager: [Manager Name]
                """)
            else:
                today = datetime.today()
                is_future = details['effective_date'] > today
                
                st.success("✅ Successfully parsed manager change notification!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Employee", details['employee_name'])
                    st.metric("Employee ID", details['employee_id'])
                with col2:
                    st.metric("New Manager", details['new_manager'])
                    st.metric("Effective Date", details['effective_date'].strftime('%d/%m/%Y'))
                
                st.markdown("---")
                
                script_filename = f"Update-{details['employee_name'].replace(' ', '-')}-Manager.ps1"
                manager_script = generate_manager_change_script(details, is_scheduled=is_future)
                
                if is_future:
                    days_until = (details['effective_date'] - today).days
                    st.info(f"📅 This change is scheduled for the future ({days_until} days from now)")
                    
                    display_script_with_download(
                        manager_script,
                        "📄 Manager Update PowerShell Script",
                        script_filename
                    )
                    
                    st.markdown("---")
                    
                    task_name = f"Update {details['employee_name']} Manager"
                    run_time = details['effective_date'].strftime(f'%Y-%m-%d {DEFAULT_TASK_TIME}')
                    schedule_script = generate_scheduled_task_script(script_filename, task_name, run_time)
                    
                    display_script_with_download(
                        schedule_script,
                        "⏰ Task Scheduler Script",
                        f"Schedule-{details['employee_name'].replace(' ', '-')}-Manager.ps1"
                    )
                else:
                    st.info("⚡ This change is effective immediately")
                    display_script_with_download(
                        manager_script,
                        "📄 Immediate Manager Update Script",
                        script_filename
                    )

# ============================================================================
# XRM ACCOUNT PASSWORD RESETER
# ============================================================================

def generate_xrm_messages(employee_name: str) -> Dict[str, str]:
    """Generate XRM password reset messages."""
    try:
        # Capitalize the name properly
        employee_name = capitalize_name(employee_name)
        
        # Extract first name
        name_parts = employee_name.split()
        first_name = name_parts[0] if name_parts else employee_name
        
        # Generate email address (first.lastname@inhealthgroup.com)
        username = sanitize_username(employee_name)
        email = f"{username}@inhealthgroup.com"
        
        # Generate messages
        teams_message = f"""Hi {first_name},

I've reset your XRM password for you.

Please close the XRM page, reopen it, and use the following password to log in: {XRM_DEFAULT_PASSWORD}

Let me know if you have any issues or need further help!

Thanks"""

        resolving_message = f"""Hi {first_name},

Your account has been unlocked, and I've sent the new password to you on MS Teams.

Please check your Teams messages and let me know if you need any further assistance.

Thanks!"""

        return {
            'employee_name': employee_name,
            'first_name': first_name,
            'email': email,
            'teams_message': teams_message,
            'resolving_message': resolving_message
        }
    except Exception as e:
        st.error(f"Error generating XRM messages: {str(e)}")
        return None

# Section 3: XRM Account Password Reseter
with st.expander("🔑 XRM Account Password Reseter", expanded=False):
    st.markdown("""
    **Instructions:** Enter the employee's full name to generate password reset messages.
    The system will create both the Teams message and the resolution message.
    """)
    
    xrm_employee_name = st.text_input(
        "Employee Full Name:",
        placeholder="e.g., John Smith",
        help="Enter the full name of the employee requiring XRM password reset",
        key="xrm_name_input"
    )

    if st.button("🚀 Generate XRM Reset Messages", key="xrm_reset", type="primary"):
        if not xrm_employee_name.strip():
            st.warning("⚠️ Please enter the employee's name.")
        else:
            with st.spinner("🔄 Generating messages..."):
                messages = generate_xrm_messages(xrm_employee_name)
            
            if not messages:
                st.error("❌ Could not generate messages. Please try again.")
            else:
                st.success(f"✅ Successfully generated XRM reset messages for {messages['employee_name']}!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Employee", messages['employee_name'])
                with col2:
                    st.metric("First Name", messages['first_name'])
                with col3:
                    st.metric("Email", messages['email'])
                
                st.markdown("---")
                
                # Email Address Section
                st.markdown("### 📧 Employee Email")
                st.code(messages['email'], language='text')
                
                st.markdown("---")
                
                # Teams Message
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 💬 Message to Teams")
                    st.code(messages['teams_message'], language='text')
                    create_download_button(
                        messages['teams_message'],
                        f"XRM-Teams-Message-{messages['employee_name'].replace(' ', '-')}.txt",
                        "Download Teams Message"
                    )
                
                with col2:
                    st.markdown("### ✅ Resolving Message")
                    st.code(messages['resolving_message'], language='text')
                    create_download_button(
                        messages['resolving_message'],
                        f"XRM-Resolving-Message-{messages['employee_name'].replace(' ', '-')}.txt",
                        "Download Resolving Message"
                    )
                
                st.markdown("---")
                
                # Quick copy section
                st.markdown("### 📋 Quick Copy")
                st.info("Click the copy icon in the top-right corner of each code block to copy the message.")

# ============================================================================
# SPECTRA ACCOUNT CREATOR
# ============================================================================

def generate_spectra_account_details(employee_name: str, account_type: str) -> Dict[str, str]:
    """Generate Spectra account details for PM or Client."""
    try:
        # Capitalize the name properly
        employee_name = capitalize_name(employee_name)
        
        # Extract first and last names
        name_parts = employee_name.split()
        if len(name_parts) < 2:
            return None
            
        first_name = name_parts[0]
        last_name = name_parts[-1]
        
        # Generate username based on account type
        if account_type == "PM":
            # Format: firstnamefirstletteroflastnamesuper (e.g., lorrainegsuper)
            username = f"{first_name.lower()}{last_name[0].lower()}super"
        else:  # Client
            # Format: firstletterfirstnamelastname (e.g., lgardener)
            username = f"{first_name[0].lower()}{last_name.lower()}"
        
        return {
            'employee_name': employee_name,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'nhs_email': 'nomail@nhs.net',
            'password': SPECTRA_DEFAULT_PASSWORD,
            'account_type': account_type
        }
    except Exception as e:
        st.error(f"Error generating Spectra account details: {str(e)}")
        return None

# Section 4: Spectra Account Creator
with st.expander("🔧 Spectra Account Creator", expanded=False):
    st.markdown("""
    **Instructions:** Select the account type (PM or Client) and enter the employee's full name 
    to generate Spectra account details.
    """)
    
    # Account type selection
    account_type = st.radio(
        "Select Account Type:",
        options=["PM", "Client"],
        horizontal=True,
        key="spectra_account_type"
    )
    
    spectra_employee_name = st.text_input(
        "Employee Full Name:",
        placeholder="e.g., Lorraine Gardener",
        help="Enter the full name of the employee",
        key="spectra_name_input"
    )

    if st.button("🚀 Generate Spectra Account Details", key="spectra_create", type="primary"):
        if not spectra_employee_name.strip():
            st.warning("⚠️ Please enter the employee's name.")
        else:
            with st.spinner("🔄 Generating account details..."):
                details = generate_spectra_account_details(spectra_employee_name, account_type)
            
            if not details:
                st.error("❌ Could not generate account details. Please ensure you entered a full name (first and last name).")
            else:
                st.success(f"✅ Successfully generated Spectra {details['account_type']} account details for {details['employee_name']}!")
                
                st.markdown("---")
                
                # Display account details in a clean format
                st.markdown(f"### 📋 Spectra {details['account_type']} Account Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**First Name:**")
                    st.code(details['first_name'], language='text')
                    
                    st.markdown("**Last Name:**")
                    st.code(details['last_name'], language='text')
                    
                    st.markdown("**Username:**")
                    st.code(details['username'], language='text')
                
                with col2:
                    st.markdown("**NHS Email:**")
                    st.code(details['nhs_email'], language='text')
                    
                    st.markdown("**Password:**")
                    st.code(details['password'], language='text')
                    
                    st.markdown("**Account Type:**")
                    st.code(details['account_type'], language='text')
                
                st.markdown("---")
                
                # Summary for easy copying
                st.markdown("### 📄 Complete Account Summary")
                summary = f"""First Name: {details['first_name']}
Last Name: {details['last_name']}
Username: {details['username']}
NHS Email: {details['nhs_email']}
Password: {details['password']}
Account Type: Spectra {details['account_type']}"""
                
                st.code(summary, language='text')
                
                create_download_button(
                    summary,
                    f"Spectra-{details['account_type']}-{details['employee_name'].replace(' ', '-')}.txt",
                    "Download Account Details"
                )
                
                st.markdown("---")
                
                # Communication Templates
                st.markdown("### 📧 Communication Templates")
                
                # Generate Teams message
                teams_message = f"""Hi {details['first_name']},

Your Spectra {details['account_type']} account has been set up. Here are your login details:

Username: {details['username']}
Password: {details['password']}

Feel free to reach out if you have any questions or need help getting started!

Thanks"""

                # Generate Jira reply
                jira_reply = f"""Hi {details['first_name']},

Your Spectra {details['account_type']} account is all set up! I've sent the login details to you via Teams.

Please check your Teams messages and let me know if you need any assistance.

Thanks!"""

                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**💬 Message to Teams:**")
                    st.code(teams_message, language='text')
                    create_download_button(
                        teams_message,
                        f"Spectra-Teams-Message-{details['employee_name'].replace(' ', '-')}.txt",
                        "Download Teams Message"
                    )
                
                with col2:
                    st.markdown("**✅ Jira Reply:**")
                    st.code(jira_reply, language='text')
                    create_download_button(
                        jira_reply,
                        f"Spectra-Jira-Reply-{details['employee_name'].replace(' ', '-')}.txt",
                        "Download Jira Reply"
                    )

# ============================================================================
# LEAVER NOTIFICATION PARSER
# ============================================================================

def parse_leaver_notification(text: str) -> Optional[Dict]:
    """
    Parse leaver notification and extract details.
    Supports three input formats:
    1. Full notification text (with all details - iTrent format)
    2. Just an email address (e.g., john.smith@inhealthgroup.com)
    3. Just a name (e.g., John Smith)
    
    iTrent format example:
    [Name] has been made a leaver:
    Employee Reference #: [ID]
    Leaving Date: DD/MM/YYYY
    Reporting Manager: [Manager]
    Department: [Dept]
    """
    try:
        text = text.strip()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        joined = " ".join(lines)
        
        # Initialize variables
        email = None
        name = None
        employee_id = None
        leaving_date = None
        manager = None
        
        # 1. Try full notification parsing first (iTrent format)
        emp_match = re.search(r"^(.*?)\s+has\s+been\s+made\s+a\s+leaver", joined, re.IGNORECASE)
        id_match = re.search(r"Employee\s+Reference\s*#:\s*(\d+)", joined, re.IGNORECASE)
        date_match = re.search(r"Leaving\s+Date:\s*(\d{2}/\d{2}/\d{4})", joined, re.IGNORECASE)
        mgr_match = re.search(r"Reporting\s+Manager:\s*([^\n:]+?)(?:\s*(?:Department|$))", joined, re.IGNORECASE)
        
        # If we found all required fields in full notification format, use them
        if emp_match and id_match and date_match and mgr_match:
            name = emp_match.group(1).strip()
            employee_id = id_match.group(1).strip()
            leaving_date_str = date_match.group(1).strip()
            manager = mgr_match.group(1).strip()
            
            # Validate and parse the date
            leaving_date = validate_date_format(leaving_date_str)
            if leaving_date and name:
                # Extract first and last name only (ignore middle names)
                employee_name_parts = name.split()
                if len(employee_name_parts) > 2:
                    name = f"{employee_name_parts[0]} {employee_name_parts[-1]}"
                
                return {
                    'employee_name': name,
                    'employee_id': employee_id,
                    'leaving_date': leaving_date,
                    'manager': manager,
                    'sam_account_name': sanitize_username(name),
                    'input_type': 'full_notification'
                }
        
        # 2. If full notification parsing failed, try alternative methods
        # Find email
        for line in lines:
            m = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
            if m:
                email = m.group(0)
                break
        
        # Find date (supports 'leaver from 25th October', 'leaving date: ...', 'from ...', etc.)
        for line in lines:
            # Try DD/MM/YYYY
            m = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', line)
            if m:
                leaving_date = validate_date_format(m.group(1))
                if leaving_date:
                    break
            # Try 'from 25th October' or 'leaver from 25th October'
            m2 = re.search(r'from ([\w\d\s]+)', line, re.IGNORECASE)
            if m2:
                # Remove ordinal suffixes (st, nd, rd, th) from day numbers
                date_str = m2.group(1).strip()
                date_str = re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1', date_str, flags=re.IGNORECASE)
                # Try to parse as date (day + month, assume current year)
                try:
                    leaving_date = datetime.strptime(date_str + f" {datetime.today().year}", "%d %B %Y")
                except Exception:
                    try:
                        leaving_date = datetime.strptime(date_str + f" {datetime.today().year}", "%d %b %Y")
                    except Exception:
                        continue
                if leaving_date:
                    break
        
        # Find name (look for ' - leaver', or first line, or from email)
        for line in lines:
            m = re.match(r'^(.*?)(?:\s*-\s*leaver|\s*-\s*leaver from|$)', line, re.IGNORECASE)
            if m and m.group(1).strip():
                name = m.group(1).strip()
                break
        
        # Try to extract name from email if not found
        if not name and email:
            email_parts = email.split('@')[0].split('.')
            if len(email_parts) >= 2:
                name = f"{email_parts[0].capitalize()} {email_parts[-1].capitalize()}"
        
        # Fallback: use first line if still no name
        if not name and lines:
            name = lines[0]
        
        # If we have a valid name (at least two words) and date, return
        if name and len(name.split()) >= 2:
            return {
                'employee_name': capitalize_name(name),
                'employee_id': employee_id or 'N/A',
                'leaving_date': leaving_date or datetime.today(),
                'manager': manager or 'N/A',
                'sam_account_name': sanitize_username(name),
                'input_type': 'mixed'
            }
        
        return None
    except Exception as e:
        st.error(f"Error parsing leaver notification: {str(e)}")
        return None

def generate_disable_user_script(details: Dict, company: str = "IHG") -> str:
    """Generate PowerShell script to disable user account.
    
    Args:
        details: Dictionary with employee details
        company: Company type - "IHI" (Health Intelligence) or "IHG" (InHealth Group)
    """
    date_string = details['leaving_date'].strftime("%d/%m/%Y")
    description_suffix = f"Leaving Date: {date_string}"
    
    # Determine the target OU and server based on company
    if company == "IHI":
        target_ou = AD_IHI_DISABLED_OU
        server_param = "-Server 'hi.int'"
    else:
        target_ou = AD_DISABLED_OU
        server_param = "-Server 'ihgd.inhealthgroup.com'"
    
    return rf"""# Disable user account for {details['employee_name']}
$samAccountName = "{details['sam_account_name']}"
$ouPath = "{target_ou}"
$leavingNote = "{description_suffix}"
$serverParam = "{server_param}"

try {{
    # Get the user account with server specification
    $user = Get-ADUser -Identity $samAccountName -Properties Description, DistinguishedName, MemberOf {server_param} -ErrorAction Stop

    if ($user) {{
        Write-Host "Found user: $($user.Name)" -ForegroundColor Cyan
        
        # Update description with leaving date
        $existingDesc = $user.Description
        
        # Function to convert old format (DDMMYYYY) to new format (DD/MM/YYYY)
        function Convert-OldDateFormat {{
            param([string]$dateStr)
            if ($dateStr -match '^(\d{{2}})(\d{{2}})(\d{{4}})$') {{
                return "$($matches[1])/$($matches[2])/$($matches[3])"
            }}
            return $null
        }}
        
        # Check if there's already a leaving date in the description
        if ($existingDesc -match 'Leaving Date:\s*(\d{{2}}/\d{{2}}/\d{{4}})') {{
            # New format date found
            $existingDate = $matches[1]
            if ($existingDate -eq "{date_string}") {{
                # Same date already exists, no update needed
                Write-Host "ℹ️ Leaving date ($existingDate) already present; no update needed." -ForegroundColor Cyan
                $updatedDesc = $existingDesc
            }} else {{
                # Different date - clean up and set new format
                $jobTitle = $existingDesc -replace '\s*-?\s*(Leaving Date|Leave Date)\s*:?.*$', ''
                $updatedDesc = "$jobTitle - $leavingNote"
                Write-Host "ℹ️ Replaced leaving date from $existingDate to {date_string}" -ForegroundColor Cyan
            }}
        }} elseif ($existingDesc -match 'Leave Date\s*:?\s*(\d{{8}})') {{
            # Old format date found (e.g., "30012026")
            $oldFormatDate = $matches[1]
            $convertedOldDate = Convert-OldDateFormat -dateStr $oldFormatDate
            
            if ($convertedOldDate -eq "{date_string}") {{
                # Same date, leave as is
                Write-Host "ℹ️ Leaving date matches existing date ($convertedOldDate); no update needed." -ForegroundColor Cyan
                $updatedDesc = $existingDesc
            }} else {{
                # Different date - clean up and set new format
                $jobTitle = $existingDesc -replace '\s*-?\s*(Leaving Date|Leave Date)\s*:?.*$', ''
                $updatedDesc = "$jobTitle - $leavingNote"
                Write-Host "ℹ️ Replaced leaving date from $convertedOldDate to {date_string}" -ForegroundColor Cyan
            }}
        }} elseif ([string]::IsNullOrWhiteSpace($existingDesc)) {{
            # No description exists, set the leaving date
            $updatedDesc = $leavingNote
        }} else {{
            # Description exists but no leaving date, append it
            $updatedDesc = "$existingDesc - $leavingNote"
        }}
        
        # Update description
        Set-ADUser -Identity $user.DistinguishedName -Description $updatedDesc {server_param} -ErrorAction Stop
        Write-Host "✅ Updated description" -ForegroundColor Green
        
        # Remove user from all groups except 'Domain Users' using MemberOf property
        if ($user.MemberOf) {{
            Write-Host "Removing user from groups..." -ForegroundColor Cyan
            foreach ($groupDN in $user.MemberOf) {{
                try {{
                    $group = Get-ADGroup -Identity $groupDN {server_param} -ErrorAction Stop
                    if ($group.Name -ne 'Domain Users') {{
                        try {{
                            Remove-ADGroupMember -Identity $groupDN -Members $user.DistinguishedName -Confirm:$false {server_param} -ErrorAction Stop
                            Write-Host "✅ Removed user from group: $($group.Name)" -ForegroundColor Green
                        }} catch {{
                            $errMsg = $_.Exception.Message
                            Write-Host "⚠️ Could not remove from group $($group.Name): $errMsg" -ForegroundColor Yellow
                        }}
                    }} else {{
                        Write-Host "ℹ️ Skipping group: $($group.Name)" -ForegroundColor Cyan
                    }}
                }} catch {{
                    $errMsg = $_.Exception.Message
                    Write-Host "⚠️ Could not process group: $errMsg" -ForegroundColor Yellow
                }}
            }}
        }} else {{
            Write-Host "ℹ️ User is not a member of any groups (except primary group)" -ForegroundColor Cyan
        }}

        # Disable the account
        Set-ADUser -Identity $user.DistinguishedName -Enabled $false {server_param} -ErrorAction Stop
        Write-Host "✅ Account disabled" -ForegroundColor Green

        # Move to disabled OU
        Move-ADObject -Identity $user.DistinguishedName -TargetPath $ouPath {server_param} -ErrorAction Stop
        Write-Host "✅ Moved to disabled OU" -ForegroundColor Green
        
        Write-Host "`n✅ User '$samAccountName' has been successfully disabled and moved." -ForegroundColor Green
    }} else {{
        Write-Host "❌ User not found." -ForegroundColor Red
    }}
}} catch {{
    $errMsg = $_.Exception.Message
    Write-Host "❌ Error processing user '$samAccountName'" -ForegroundColor Red
    Write-Host "Error details: $errMsg" -ForegroundColor DarkRed
}}"""

with st.expander("🛑 Leaver Notification Parser", expanded=False):
    st.markdown("""
    **Instructions:** Provide employee information in any of these formats:
    - **Full iTrent notification email** (with all details including Employee Reference #, Leaving Date, Reporting Manager)
    - **Just the name** (e.g., "John Smith")
    - **Just the email** (e.g., "john.smith@inhealthgroup.com")
    
    The system will extract the employee name and leaving date, then generate a script to disable the account and move it to the appropriate OU.
    """)
    
    leaver_text = st.text_area(
        "Paste Leaver Notification, Name, or Email:",
        height=200,
        placeholder="Enter:\n• Full notification text, OR\n• Employee name (e.g., John Smith), OR\n• Employee email (e.g., john.smith@inhealthgroup.com)",
        help="Accepts full notifications, names, or email addresses",
        key="leaver_text"
    )

    # Company selection
    st.markdown("**Select Employee Company:**")
    company = st.radio(
        "Which company is the leaver from?",
        options=["IHG (InHealth Group)", "IHI (Health Intelligence)"],
        index=0,
        horizontal=True,
        help="IHG: Uses standard disabled OU | IHI: Uses OU=Leavers,OU=Disabled,OU=HIUsers,DC=hi,DC=int",
        label_visibility="collapsed"
    )
    
    # Convert radio selection to company code
    company_code = "IHG" if "IHG" in company else "IHI"

    if st.button("🚀 Generate Disable User Script", key="disable_user", type="primary"):
        if not leaver_text.strip():
            st.warning("⚠️ Please provide employee information (notification, name, or email).")
        else:
            with st.spinner("🔄 Processing information..."):
                details = parse_leaver_notification(leaver_text)
            
            if not details:
                st.error("❌ Could not extract leaver details. Please check the input format.")
                st.info("""
                **Accepted formats:**
                1. **Full iTrent notification:**
                   ```
                   [Name] has been made a leaver:
                   Employee Reference #: [ID]
                   Leaving Date: DD/MM/YYYY
                   Reporting Manager: [Manager Name]
                   Department: [Department]
                   ```
                
                2. **Just a name:** John Smith
                
                3. **Just an email:** john.smith@inhealthgroup.com
                """)
            else:
                today = datetime.today()
                is_future = details['leaving_date'] > today
                
                # Show success message with input type indicator
                input_type_msg = {
                    'email': 'email address',
                    'name': 'employee name',
                    'full_notification': 'notification'
                }
                input_type = input_type_msg.get(details.get('input_type', 'full_notification'), 'input')
                
                st.success(f"✅ Successfully processed {input_type}!")
                
                # Show info if using simplified input (name or email)
                if details.get('input_type') in ['email', 'name']:
                    st.info(f"ℹ️ Using today's date as leaving date. Employee ID and Manager set to 'N/A'.")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Employee", details['employee_name'])
                    st.metric("Employee ID", details['employee_id'])
                with col2:
                    st.metric("Leaving Date", details['leaving_date'].strftime('%d/%m/%Y'))
                    st.metric("Manager", details['manager'])
                
                st.markdown("---")
                
                script_filename = f"Disable-{details['employee_name'].replace(' ', '-')}.ps1"
                disable_script = generate_disable_user_script(details, company_code)
                
                if is_future:
                    days_until = (details['leaving_date'] - today).days
                    st.info(f"📅 Account will be disabled in {days_until} days")
                    
                    display_script_with_download(
                        disable_script,
                        "📄 Disable User PowerShell Script",
                        script_filename
                    )
                    
                    st.markdown("---")
                    
                    # Generate scheduler script
                    task_name = f"Disable {details['employee_name']} Account"
                    run_time = details['leaving_date'].strftime(f'%Y-%m-%d {LEAVER_TASK_TIME}')
                    
                    schedule_script = rf"""# Save script and schedule for future execution
$scriptContent = @"
{disable_script}
"@

$scriptPath = "$env:USERPROFILE\Documents\{script_filename}"
$scriptContent | Set-Content -Path $scriptPath -Encoding UTF8
Write-Host "📁 Script saved to: $scriptPath" -ForegroundColor Cyan

$taskName = "{task_name}"
$runDate = Get-Date "{run_time}"

try {{
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""
    $trigger = New-ScheduledTaskTrigger -Once -At $runDate
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Force -ErrorAction Stop
    
    Write-Host "✅ Scheduled disable task for {details['employee_name']}" -ForegroundColor Green
    Write-Host "📅 Task will run on: $($runDate.ToString('f'))" -ForegroundColor Cyan
}} catch {{
    Write-Host "❌ Error creating scheduled task: $_" -ForegroundColor Red
}}"""
                    
                    display_script_with_download(
                        schedule_script,
                        "⏰ Task Scheduler Script",
                        f"Schedule-Disable-{details['employee_name'].replace(' ', '-')}.ps1"
                    )
                    
                    st.warning("⚠️ **Important:** The scheduler script will automatically save the disable script and create the scheduled task.")
                else:
                    st.warning("⚠️ This employee's leaving date is today or in the past. Execute immediately!")
                    display_script_with_download(
                        disable_script,
                        "📄 Immediate Disable User Script",
                        script_filename
                    )

# ============================================================================
# M1 NEW EMPLOYEE ONBOARDING
# ============================================================================

def parse_m1(text: str) -> Dict[str, str]:
    """
    Parse M1 formatted text into a dictionary.
    Handles both colon-separated and tab-separated key-value pairs.
    """
    data = {}
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
        elif '\t' in line:
            parts = line.split('\t')
            if len(parts) >= 2:
                data[parts[0].strip()] = parts[-1].strip()
    
    return data

def year_to_roman(year: int) -> str:
    """Convert year (last 2 digits) to Roman numerals."""
    val = [100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ["C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ''
    i = 0
    while year > 0:
        for _ in range(year // val[i]):
            roman_num += syms[i]
            year -= val[i]
        i += 1
    return roman_num

def generate_password_from_name(first_name: str, last_name: str) -> str:
    """
    Generate an improved temporary password from employee name.
    Format: FirstName(4 chars) + Year(2-digit Roman) + LastName(3 chars) + #Month
    Example: SharXXVILai#02 (26 in Roman numerals for 2026)
    
    Benefits:
    - More secure with year in Roman numerals
    - Still easy to remember (based on name and current year)
    - Year changes annually providing natural password rotation
    - Better entropy than pure name-based password
    """
    if not first_name or not last_name:
        return generate_secure_password()
    
    # Get last 2 digits of current year as Roman numerals
    current_year = datetime.today().year % 100
    year_roman = year_to_roman(current_year)
    
    # Get current month as 2-digit number
    current_month = datetime.today().strftime("%m")
    
    # Build password: First 4 chars of first name + Year(Roman) + Last 3 chars of last name + #Month
    first_part = first_name.capitalize()[:4]
    last_part = last_name.lower()[:3]
    password = f"{first_part}{year_roman}{last_part}#{current_month}"
    
    # Remove the first character as requested
    return password[1:]

def generate_group_clone_script(source_input: str, target_sam: str, domain: str) -> str:
    """Generate a PowerShell script to clone AD groups from source to target.

    Args:
        source_input: Source user (sAMAccountName, email, or FirstName LastName).
        target_sam: Target user's sAMAccountName.
        domain: "IHI" or "IHG".
    """
    if domain == "IHI":
        server = "hi.int"
    else:
        server = "ihgd.inhealthgroup.com"

    return rf"""# Clone AD group memberships
# Domain: {domain}
$ErrorActionPreference = "Stop"
Import-Module ActiveDirectory -ErrorAction Stop

$sourceInput = "{source_input}"
$targetSam = "{target_sam}"
$server = "{server}"

function Escape-LdapFilterValue {{
    param([Parameter(Mandatory)][string]$Value)
    $Value `
        -replace "\\", "\5c" `
        -replace "\*", "\2a" `
        -replace "\(", "\28" `
        -replace "\)", "\29" `
        -replace "\0", "\00"
}}

function Resolve-ADUserFlexible {{
    param([Parameter(Mandatory)][string]$InputRaw)

    $input = $InputRaw.Trim()
    if ([string]::IsNullOrWhiteSpace($input)) {{ throw "No input provided." }}

    # Email / UPN
    if ($input -match "@") {{
        $v = Escape-LdapFilterValue $input
        $u = Get-ADUser -LDAPFilter "(|(userPrincipalName=$v)(mail=$v))" -Properties mail,userPrincipalName -Server $server -ErrorAction SilentlyContinue
        if ($u) {{ return $u }}
    }}

    # sAMAccountName (strip spaces)
    $sam = ($input -replace "\s", "")
    $vSam = Escape-LdapFilterValue $sam
    $u = Get-ADUser -LDAPFilter "(sAMAccountName=$vSam)" -Properties mail,userPrincipalName -Server $server -ErrorAction SilentlyContinue
    if ($u) {{ return $u }}

    # FirstName LastName
    if ($input -match "^\S+\s+\S+") {{
        $parts = $input -split "\s+", 2
        $first = Escape-LdapFilterValue $parts[0]
        $last  = Escape-LdapFilterValue $parts[1]

        $matches = Get-ADUser -LDAPFilter "(&(givenName=$first)(sn=$last))" -Properties mail,userPrincipalName -Server $server -ErrorAction SilentlyContinue
        if ($matches.Count -gt 1) {{ throw "Multiple users found for '$input'. Use username or email." }}
        if ($matches) {{ return $matches }}
    }}

    throw "User '$InputRaw' not found in Active Directory."
}}

$srcUser = Resolve-ADUserFlexible $sourceInput
$dstUser = Get-ADUser -Identity $targetSam -Server $server -ErrorAction Stop

Write-Host "Source : $($srcUser.SamAccountName)" -ForegroundColor Cyan
Write-Host "Target : $($dstUser.SamAccountName)" -ForegroundColor Cyan

# Get source groups
$srcUserFull = Get-ADUser -Identity $srcUser.DistinguishedName -Properties MemberOf -Server $server
if (-not $srcUserFull.MemberOf) {{
    Write-Warning "Source user has no group memberships."
    return
}}

$excludeNames = @("Domain Users")
$groupsToClone = $srcUserFull.MemberOf |
    Get-ADGroup -Server $server |
    Where-Object {{ $excludeNames -notcontains $_.Name }}

# Get target existing groups
$dstSet = New-Object "System.Collections.Generic.HashSet[string]"
$dstUserFull = Get-ADUser -Identity $dstUser.DistinguishedName -Properties MemberOf -Server $server
if ($dstUserFull.MemberOf) {{
    $dstUserFull.MemberOf | ForEach-Object {{ [void]$dstSet.Add($_) }}
}}

# Clone groups
$added   = @()
$skipped = @()
$failed  = @()

foreach ($group in $groupsToClone) {{
    if ($dstSet.Contains($group.DistinguishedName)) {{
        $skipped += $group.Name
        continue
    }}

    try {{
        Add-ADGroupMember -Identity $group.DistinguishedName -Members $dstUser.DistinguishedName -Server $server -ErrorAction Stop
        $added += $group.Name
        [void]$dstSet.Add($group.DistinguishedName)
    }} catch {{
        $failed += "$($group.Name) :: $($_.Exception.Message)"
    }}
}}

# Summary
Write-Host "=== Group Clone Summary ==="
Write-Host "Added   : $($added.Count)"
Write-Host "Skipped : $($skipped.Count)"
Write-Host "Failed  : $($failed.Count)"

if ($added) {{
    Write-Host ""; Write-Host "Added groups:"
    $added | Sort-Object | ForEach-Object {{ Write-Host "  $_" }}
}}

if ($skipped) {{
    Write-Host ""; Write-Host "Already had (skipped):"
    $skipped | Sort-Object | ForEach-Object {{ Write-Host "  $_" }}
}}

if ($failed) {{
    Write-Host ""; Write-Host "Failed:"
    $failed | ForEach-Object {{ Write-Host "  $_" }}
}}

Write-Host ""
if (-not $failed -and $added) {{
    Write-Host "Done. Group memberships cloned successfully."
}}

if (-not $failed -and -not $added -and $skipped) {{
    Write-Host "Nothing to add. Target already has all the source groups."
}}

if ($failed) {{
    Write-Host "Completed with some errors."
}}
"""

def detect_mirror_user(data: Dict[str, str]) -> str:
    """Try to detect a mirror user from M1 data fields."""
    if not data:
        return ""

    explicit_keys = {
        "Mirror User",
        "Mirror User Name",
        "Mirror From",
        "Mirror From User",
        "Mirror From Username",
        "Clone From",
        "Clone User",
        "Copy From",
        "Copy User",
        "AD Mirror User",
        "AD Clone User",
        "Template User",
        "Similar User",
    }

    for key in explicit_keys:
        value = data.get(key, "").strip()
        if value:
            return value

    for key, value in data.items():
        if not value:
            continue
        key_lower = key.lower()
        if any(token in key_lower for token in ["mirror", "clone", "copy", "template"]):
            return value.strip()

    return ""

def generate_onboarding_details(data: Dict[str, str], mirror_user: str = "") -> Dict:
    """Generate comprehensive onboarding details from M1 data."""
    try:
        # Extract and capitalize names
        manager_name = capitalize_name(data.get("Hiring Manager Name", ""))
        candidate_name = capitalize_name(data.get("Candidate Name", ""))
        job_title = data.get("candidate Job Title", "") or data.get("Candidate Job Title", "")
        location = data.get("Location", "")
        telephone = data.get("Candidate Mobile Number", "")
        address = data.get("Candidate Address", "")
        company_name = data.get("Company Name", "")
        start_date = data.get("Start Date", "")
        candidate_id = data.get('Unique Identifier - Candidate ID', '')

        # Parse names
        name_parts = candidate_name.split()
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[-1] if len(name_parts) > 1 else ""

        # Generate credentials
        username = sanitize_username(candidate_name)
        default_password = generate_password_from_name(first_name, last_name)
        spectra_pm_username = f"{first_name.lower()}{last_name[0].lower()}super" if last_name else ""
        # Use the same Spectra password from environment variables
        spectra_pm_password = SPECTRA_DEFAULT_PASSWORD

        # Manager username
        manager_parts = manager_name.split()
        manager_username = sanitize_username(manager_name) if len(manager_parts) >= 2 else manager_parts[0].lower() if manager_parts else ""

        # Determine permissions
        permissions = []
        if data.get("Access Permissions for XRM", "").lower() not in ["no", ""] and data.get("Access Permissions for XRM", "").strip():
            permissions.append("XRM")
        if data.get("Access to Standard Applications - Iris", "").lower() not in ["no", ""] and data.get("Access to Standard Applications - Iris", "").strip():
            permissions.append("IRIS")

        # Determine company and generate appropriate scripts
        company_reg = data.get("Company Registered Number", "")
        domain_code = "IHG"
        
        if "Health Intelligence" in company_reg:
            config = COMPANY_CONFIGS["Health Intelligence"]
            domain_code = "IHI"
            user_email = f"{username}{config['email_domain']}"
            company_display = config['display_name']
            
            # Build AD create script with only non-empty fields
            ad_params = []
            ad_params.append(f'-Name "{candidate_name}"')
            ad_params.append(f'-SamAccountName "{username}"')
            if first_name:
                ad_params.append(f'-GivenName "{first_name}"')
            if last_name:
                ad_params.append(f'-Surname "{last_name}"')
            ad_params.append(f'-DisplayName "{candidate_name}"')
            if job_title:
                ad_params.append(f'-Description "{job_title}"')
                ad_params.append(f'-Title "{job_title}"')
            if company_name:
                ad_params.append(f'-Department "{company_name}"')
            if location:
                ad_params.append(f'-Office "{location}"')
            if user_email:
                ad_params.append(f'-EmailAddress "{user_email}"')
            ad_params.append(f'-Path "{config["ad_path"]}"')
            ad_params.append(f'-Company "{company_display}"')
            if manager_username:
                ad_params.append(f'-Manager "{manager_username}"')
            ad_params.append(f'-AccountPassword (ConvertTo-SecureString "{default_password}" -AsPlainText -Force)')
            if candidate_id:
                ad_params.append(f'-employeeNumber "{candidate_id}"')
            ad_params.append('-Enabled $true')
            ad_params.append('-ErrorAction Stop')
            
            ad_params_str = ' `\n            '.join(ad_params)
            
            ad_create_script = f"""# Create new AD user for {candidate_name}
try {{
    if (-not (Get-ADUser -Filter {{SamAccountName -eq '{username}'}} -ErrorAction SilentlyContinue)) {{
        New-ADUser {ad_params_str}
        Write-Host "✅ User {username} created successfully." -ForegroundColor Green
    }} else {{
        Write-Host "⚠️ User {username} already exists." -ForegroundColor Yellow
    }}
}} catch {{
    Write-Host "❌ Error creating user: $_" -ForegroundColor Red
}}"""
            
            sections = config['sections']
        elif "TAC Healthcare" in company_reg:
            config = COMPANY_CONFIGS["TAC Healthcare"]
            user_email = f"{username}{config['email_domain']}"
            company_display = config['display_name']
            ad_create_script = ""
            sections = config['sections']
        else:
            config = COMPANY_CONFIGS["InHealth Group"]
            user_email = f"{username}{config['email_domain']}"
            company_display = config['display_name']
            ad_create_script = ""
            sections = config['sections']

        # AD update script (common for all) - only include non-empty fields
        update_params = []
        if job_title:
            update_params.append(f'-Title "{job_title}"')
        if company_name:
            update_params.append(f'-Department "{company_name}"')
        if manager_username:
            update_params.append(f'-Manager "{manager_username}"')
        if job_title:
            update_params.append(f'-Description "{job_title}"')
        if location:
            update_params.append(f'-Office "{location}"')
        if user_email:
            update_params.append(f'-EmailAddress "{user_email}"')
        if candidate_id:
            update_params.append(f'-employeeNumber "{candidate_id}"')
        if company_display:
            update_params.append(f'-Company "{company_display}"')
        update_params.append('-ErrorAction Stop')
        
        update_params_str = ' `\n        '.join(update_params)
        
        ad_update_script = f"""# Update AD user attributes for {candidate_name}
try {{
    Set-ADUser -Identity "{username}" `
        {update_params_str}
    Write-Host "✅ User attributes updated successfully." -ForegroundColor Green
}} catch {{
    Write-Host "❌ Error updating user: $_" -ForegroundColor Red
}}"""

        if permissions:
            sections = sections + ["Permissions"]

        resolved_mirror_user = mirror_user.strip() or detect_mirror_user(data)
        group_clone_script_ihi = ""
        group_clone_script_ihg = ""
        if resolved_mirror_user:
            group_clone_script_ihi = generate_group_clone_script(resolved_mirror_user, username, "IHI")
            group_clone_script_ihg = generate_group_clone_script(resolved_mirror_user, username, "IHG")

        # Build provisioning scripts based on company
        if domain_code == "IHI":
            # IHI Script 1: Create AD user (IHI) + Clone groups (IHI)
            ihi_parts = [p for p in [ad_create_script, group_clone_script_ihi] if p]
            ihi_provisioning_script = "\n\n# ---- Next Step ----\n\n".join(ihi_parts) if ihi_parts else ""

            # IHI Script 2: Update AD attributes (IHG) + Clone groups (IHG)
            ihg_parts = [p for p in [ad_update_script, group_clone_script_ihg] if p]
            ihg_provisioning_script = "\n\n# ---- Next Step ----\n\n".join(ihg_parts) if ihg_parts else ""
        else:
            # IHG only: Update AD attributes (IHG) + Clone groups (IHG)
            ihi_provisioning_script = ""
            ihg_parts = [p for p in [ad_update_script, group_clone_script_ihg] if p]
            ihg_provisioning_script = "\n\n# ---- Next Step ----\n\n".join(ihg_parts) if ihg_parts else ""

        # Generate messages
        manager_first_name = manager_name.split()[0] if manager_name else "Manager"
        
        # Build the joining info line with conditional fields
        if job_title and start_date:
            article = "an" if job_title[0].lower() in 'aeiou' else "a"
            joining_info = f"the new starter, {candidate_name}, who will be joining as {article} {job_title} on {start_date}"
        elif job_title:
            article = "an" if job_title[0].lower() in 'aeiou' else "a"
            joining_info = f"the new starter, {candidate_name}, who will be joining as {article} {job_title}"
        elif start_date:
            joining_info = f"the new starter, {candidate_name}, who will be starting on {start_date}"
        else:
            joining_info = f"the new starter, {candidate_name}"
        
        # Build manager message with conditional Spectra PM password for Health Intelligence
        base_message = f"""Hi {manager_first_name},

Here are the login details for {joining_info}:

Username: {username}
User Email: {user_email}
Password: {default_password}"""

        # Add Spectra PM password for Health Intelligence
        if "Health" in company_display and "Intelligence" in company_display:
            base_message += f"""

Spectra PM Username: {spectra_pm_username}
Spectra PM Password: {spectra_pm_password}"""
        
        base_message += """

Let me know if you need any help or have questions!

Thanks"""
        
        message_to_manager = base_message

        jira_reply = f"""Hi {manager_first_name},

The account for {candidate_name} is all set up. I've sent the login details to you via Teams.

Please check your Teams messages and let me know if you need anything else.

Thanks!"""

        return {
            "First Name": first_name,
            "Last Name": last_name,
            "Full Name": candidate_name,
            "Username": username,
            "Password": default_password,
            "User Email": user_email,
            "Job Title": job_title,
            "Description": job_title,
            "Department": company_name,
            "Office": location,
            "Company": company_display,
            "Manager": manager_name,
            "Manager Username": manager_username,
            "Mobile": telephone,
            "Address": address,
            "Employee ID": candidate_id,
            "Spectra PM Username": spectra_pm_username,
            "Spectra PM Password": spectra_pm_password,
            "Spectra PM Organization": "O0 - InHealth Intelligence Ltd",
            "NHS Email": "nomail@nhs.net",
            "Permissions": ", ".join(permissions) if permissions else "None",
            "AD Create Script": ad_create_script,
            "AD Update Script": ad_update_script,
            "IHI Provisioning Script": ihi_provisioning_script,
            "IHG Provisioning Script": ihg_provisioning_script,
            "Message to Manager": message_to_manager,
            "Jira Reply": jira_reply,
            "Mirror User": resolved_mirror_user,
            "Domain": domain_code,
            "Sections": sections
        }
    except Exception as e:
        st.error(f"Error generating onboarding details: {str(e)}")
        return None

with st.expander("👤 M1 New Employee Onboarding", expanded=False):
    st.markdown("""
    **Instructions:** Paste your M1 formatted data below to generate complete onboarding details
    including account credentials, PowerShell scripts, and communication templates.
    """)

    m1_input = st.text_area(
        "Paste M1 Input Data:",
        height=300,
        help="Paste the complete M1 formatted employee data",
        key="m1_input"
    )

    mirror_user = st.text_input(
        "Mirror groups from existing user (optional):",
        placeholder="e.g. jane.doe or jane.doe@inhealthgroup.com or Jane Doe",
        help="If left blank, the app will try to auto-detect a mirror user from the M1 data."
    )

    if st.button("🚀 Generate Onboarding Details", key="m1_generate", type="primary"):
        if not m1_input.strip():
            st.warning("⚠️ Please paste M1 data before generating.")
        else:
            with st.spinner("🔄 Processing M1 data..."):
                m1_data = parse_m1(m1_input)
                if m1_data:
                    onboarding_details = generate_onboarding_details(m1_data, mirror_user)
                else:
                    onboarding_details = None
            
            if not onboarding_details:
                st.error("❌ Could not generate onboarding details. Please check the M1 data format.")
            else:
                st.success("✅ Successfully generated onboarding details!")
                
                # Display summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Employee", onboarding_details["Full Name"])
                    st.metric("Username", onboarding_details["Username"])
                with col2:
                    st.metric("Job Title", onboarding_details["Job Title"])
                    st.metric("Company", onboarding_details["Company"])
                with col3:
                    st.metric("Manager", onboarding_details["Manager"])
                    st.metric("Email", onboarding_details["User Email"])
                
                st.markdown("---")
                
                # Display sections
                sections = onboarding_details["Sections"]
                
                for section in sections:
                    with st.expander(f"📋 {section}", expanded=False):
                        if section == "Office 365 Account":
                            st.markdown("**Account Details:**")
                            
                            # Display each field separately for easy copying
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                st.markdown("**First Name:**")
                            with col2:
                                st.code(onboarding_details["First Name"], language='text')
                            
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.markdown("**Last Name:**")
                            with col2:
                                st.code(onboarding_details["Last Name"], language='text')
                            
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.markdown("**Username:**")
                            with col2:
                                st.code(onboarding_details["Username"], language='text')
                            
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.markdown("**Password:**")
                            with col2:
                                st.code(onboarding_details["Password"], language='text')
                            
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.markdown("**Full Name:**")
                            with col2:
                                st.code(onboarding_details["Full Name"], language='text')
                            
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.markdown("**Job Title:**")
                            with col2:
                                st.code(onboarding_details["Job Title"], language='text')
                        
                        elif section == "Ad Account":
                            st.markdown("**Active Directory Details:**")
                            st.code(f"""Full Name: {onboarding_details["Full Name"]}
Description: {onboarding_details["Description"]}
Office: {onboarding_details["Office"]}
Job Title: {onboarding_details["Job Title"]}
Department: {onboarding_details["Department"]}
Company: {onboarding_details["Company"]}""", language='text')
                            
                            # Display only email and manager as individually copyable fields
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.markdown("**Manager:**")
                            with col2:
                                st.code(onboarding_details["Manager"], language='text')

                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.markdown("**User Email:**")
                            with col2:
                                st.code(onboarding_details["User Email"], language='text')

                            if onboarding_details.get("Mirror User"):
                                st.info(f"ℹ️ Mirror user detected: {onboarding_details['Mirror User']}")

                            if onboarding_details.get("Domain") == "IHI":
                                # IHI users get two scripts
                                if onboarding_details["IHI Provisioning Script"]:
                                    st.markdown("**IHI Script — Create AD User + Clone Groups (hi.int):**")
                                    st.code(onboarding_details["IHI Provisioning Script"], language='powershell')
                                    create_download_button(
                                        onboarding_details["IHI Provisioning Script"],
                                        f"IHI-Provision-{onboarding_details['Full Name'].replace(' ', '-')}.ps1",
                                        "Download IHI Script"
                                    )

                                if onboarding_details["IHG Provisioning Script"]:
                                    st.markdown("**IHG Script — Update AD Attributes + Clone Groups (ihgd):**")
                                    st.code(onboarding_details["IHG Provisioning Script"], language='powershell')
                                    create_download_button(
                                        onboarding_details["IHG Provisioning Script"],
                                        f"IHG-Provision-{onboarding_details['Full Name'].replace(' ', '-')}.ps1",
                                        "Download IHG Script"
                                    )
                            else:
                                # IHG users get one script
                                if onboarding_details["IHG Provisioning Script"]:
                                    st.markdown("**IHG Script — Update AD Attributes + Clone Groups (ihgd):**")
                                    st.code(onboarding_details["IHG Provisioning Script"], language='powershell')
                                    create_download_button(
                                        onboarding_details["IHG Provisioning Script"],
                                        f"IHG-Provision-{onboarding_details['Full Name'].replace(' ', '-')}.ps1",
                                        "Download IHG Script"
                                    )
                        
                        elif section == "VPN Account":
                            st.markdown("**VPN Account Details:**")
                            
                            # Display each field separately for easy copying
                            for field_name, field_key in [
                                ("First Name", "First Name"),
                                ("Last Name", "Last Name"),
                                ("Username", "Username"),
                                ("Password", "Password"),
                                ("Full Name", "Full Name"),
                                ("Description", "Description"),
                                ("Office", "Office"),
                                ("Job Title", "Job Title"),
                                ("Company", "Company"),
                                ("Manager", "Manager"),
                                ("User Email", "User Email")
                            ]:
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    st.markdown(f"**{field_name}:**")
                                with col2:
                                    st.code(onboarding_details[field_key], language='text')
                        
                        elif section == "Spectra PM":
                            st.markdown("**Spectra PM Account:**")
                            
                            # Display each field separately for easy copying
                            for field_name, field_key in [
                                ("First Name", "First Name"),
                                ("Last Name", "Last Name"),
                                ("Username", "Spectra PM Username"),
                                ("Organization", "Spectra PM Organization"),
                                ("Password", "Spectra PM Password"),
                                ("NHS Email", "NHS Email")
                            ]:
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    st.markdown(f"**{field_name}:**")
                                with col2:
                                    st.code(onboarding_details[field_key], language='text')
                        
                        elif section == "8x8 VCC Account":
                            st.markdown("**8x8 VCC Account:**")
                            
                            # Display each field separately for easy copying
                            for field_name, field_key in [
                                ("First Name", "First Name"),
                                ("Last Name", "Last Name"),
                                ("Username", "Username"),
                                ("Job Title", "Job Title"),
                                ("Department", "Department"),
                                ("User Email", "User Email"),
                                ("Office", "Office")
                            ]:
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    st.markdown(f"**{field_name}:**")
                                with col2:
                                    st.code(onboarding_details[field_key], language='text')
                        
                        elif section == "Permissions":
                            st.markdown("**Access Permissions:**")
                            st.code(onboarding_details["Permissions"], language='text')
                
                # Communication templates
                st.markdown("---")
                st.subheader("📧 Communication Templates")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Message to Manager:**")
                    st.code(onboarding_details["Message to Manager"], language='text')
                    create_download_button(
                        onboarding_details["Message to Manager"],
                        f"Manager-Message-{onboarding_details['Full Name'].replace(' ', '-')}.txt",
                        "Download Manager Message"
                    )
                
                with col2:
                    st.markdown("**Jira Reply:**")
                    st.code(onboarding_details["Jira Reply"], language='text')
                    create_download_button(
                        onboarding_details["Jira Reply"],
                        f"Jira-Reply-{onboarding_details['Full Name'].replace(' ', '-')}.txt",
                        "Download Jira Reply"
                    )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>Employee Management Toolkit v2.0</strong></p>
    <p>⚠️ <em>Important: Always review generated scripts before execution</em></p>
    <p>🔒 <em>Handle credentials securely and follow your organization's security policies</em></p>
</div>
""", unsafe_allow_html=True)
