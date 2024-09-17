import streamlit as st
import random
import re

# Set page config
st.set_page_config(page_title="Support Request App", layout="centered")

# Input box for single data entry
input_data = st.text_area("Enter the request details (Name, Issue, Transaction ID, Phone#, Asset Tag - optional):")

# Predefined random summaries for specific issues
password_reset_summaries = [
    "Request for Password Reset",
    "Password Change Required",
    "Can't Log into My Account - Need Password Reset",
    "Need Assistance with Password Change",
    "Help Needed for Account Access - Password Issue",
    "Password Reset Request",
    "Unable to Access Account - Password Problem",
    "Password Reset Required",
    "Can't Login - Need Help with Password",
    "Password Change Request"
]

xrm_account_summaries = [
    "Need Assistance with XRM Account Reset",
    "XRM Account Reset Required",
    "Request for XRM Account Reset",
    "XRM Account Login Issue",
    "XRM Account Reset Needed",
    "XRM Account Inaccessible - Requesting Help",
    "Problem with XRM Login - Requesting Assistance",
    "Locked Out of XRM Account - Need Reset",
    "Need XRM Account Password Change",
    "Help Needed to Access XRM Account"
]

spectra_account_summaries = [
    "Spectra Account Frozen - Assistance Needed",
    "Request to Unfreeze Spectra Account",
    "Spectra Account Inactive - Need Help",
    "Help Needed to Restore Spectra Account",
    "Issue with Frozen Spectra Account",
    "Spectra Account Locked - Requesting Support",
    "Urgent Request to Unfreeze Spectra Account",
    "Can't Access Frozen Spectra Account - Need Help",
    "Request to Unlock Frozen Spectra Account",
    "Spectra Account Inaccessible - Assistance Required"
]

# Descriptions list for different issues
password_reset_descriptions = [
    "I am unable to access my account and need help resetting my password.",
    "I forgot my password and can't log into my account. Please reset it.",
    "Account is locked due to failed login attempts. Assistance needed to reset the password.",
    "I'm unable to log in and require a password reset.",
    "My account won't accept my password, and I need help resetting it.",
    "The password for my account needs to be reset as I'm unable to log in.",
    "I cannot access my account after a password issue. Assistance required for a password reset.",
    "I've forgotten my account password and need help resetting it.",
    "Account is inaccessible due to a forgotten password. Please reset it.",
    "I am locked out of my account and require a password reset."
]

xrm_descriptions = [
    "I have been locked out of my XRM account despite multiple attempts to log in. Please assist in resetting my account.",
    "XRM account reset is needed urgently. I cannot log in.",
    "My XRM account is inaccessible, and I need help resetting it.",
    "I forgot my XRM password. Please reset it for me.",
    "I am unable to log in to my XRM account. Kindly assist with a password reset.",
    "I've tried to log in to XRM several times, and it keeps failing. Please help me reset the password.",
    "Locked out of my XRM account after multiple failed attempts. Please help me reset the password.",
    "I cannot access my XRM account after a password issue. Assistance is required for resetting it.",
    "My XRM account login keeps failing. I need a password reset.",
    "XRM account access is blocked after several wrong password attempts. Help is needed."
]

spectra_descriptions = [
    "My Spectra account has been frozen and I need help unfreezing it as soon as possible.",
    "I am unable to access my Spectra account because it has been frozen. Please assist in unfreezing it.",
    "My Spectra account is currently frozen and I require help restoring access.",
    "I need immediate assistance to unfreeze my Spectra account, which has been locked.",
    "My Spectra account is inaccessible due to it being frozen. Please help me resolve this.",
    "My account on Spectra has been frozen and I cannot use the service. Assistance is needed to unfreeze it.",
    "I have been locked out of my Spectra account due to freezing. Help is needed to restore access.",
    "My Spectra account has been frozen and I cannot proceed with my work. Please help me unlock it.",
    "The Spectra account I am using is currently frozen, and I need support to fix this issue.",
    "I cannot log in to my Spectra account as it has been frozen. Please assist me in unfreezing it."
]

# Internal messages
password_reset_internal_messages = [
    "The Active Directory account password has been successfully reset, and the issue has been resolved. The new password was provided to the user over the phone.",
    "Password reset for Active Directory was successful. The new password was given to the user over the phone.",
    "The password was reset for the user's Active Directory account, and the new password was provided over the phone.",
    "Active Directory password was reset, and the user was informed of the new password over the phone.",
    "The password reset for Active Directory resolved the issue. The user received the new password via phone.",
    "Password reset on Active Directory has been completed, and the user was given the new password by phone.",
    "The user’s Active Directory password has been reset, and the new password was communicated over the phone.",
    "Password reset was successful. The user was given their new Active Directory password via phone.",
    "The Active Directory password reset has resolved the issue. The new password was provided to the user over the phone.",
    "The password was reset and shared with the user over the phone, successfully resolving the Active Directory issue."
]

xrm_internal_messages = [
    "Password has been unlocked and reset. User has been given the new password via Teams and over the phone.",
    "The XRM account password was reset, and the user was informed of the new password through Teams and phone.",
    "The user’s password was reset and provided through Teams and phone communication.",
    "XRM account reset successfully. The new password has been shared with the user over the phone and via Teams.",
    "Password reset completed. The user has received the new password both on Teams and via phone.",
    "The user’s password was reset, and they were notified via Teams and phone.",
    "Password was unlocked and reset. The new password was sent to the user through Teams and phone.",
    "Password reset was successful, and the user was given the new credentials over the phone and Teams.",
    "The XRM account password was reset, and the user was informed of the new password over the phone and through Teams.",
    "The account was reset, and the new password was communicated to the user on Teams and phone."
]

spectra_internal_messages = [
    "Account has been unfrozen and a new password has been set and sent to the user via Teams and on the phone.",
    "The Spectra account has been unfrozen and the new password was provided to the user via Teams and phone.",
    "The account was unfrozen and the new password was shared with the user on Teams and by phone.",
    "Spectra account unlocked and password updated. The user has been informed via phone and Teams.",
    "The frozen account has been unfrozen and a new password was sent to the user through Teams and phone.",
    "Account reset and unfrozen. The user has received their new password via Teams and phone.",
    "The Spectra account has been unfrozen and the password reset. The user was informed over Teams and phone.",
    "Account has been unlocked and reset. The new password was given to the user via Teams and phone.",
    "Spectra account unfrozen and new password created. The user was notified over the phone and Teams.",
    "The account was unfrozen and the user was given the new password via Teams and phone."
]

# Reply message bodies for each issue type
password_reset_user_messages = [
    "Your Windows account password has been reset. Please use the new password provided over the phone to log in.",
    "We have successfully reset your Windows password. Use the new credentials to access your account.",
    "Your password has been changed as requested. Please log in with the new password we provided.",
    "Password reset completed. You can now log in to your account using the new password.",
    "Your account password has been reset. Please use the new password communicated to you.",
    "We've reset your password. Please check your phone for the new credentials.",
    "The password for your Windows account has been reset. Use the new password to log in.",
    "Your password reset is complete. Log in with the new password provided.",
    "We've updated your password as per your request. Please use the new password to access your account.",
    "Your password has been successfully reset. You can now log in with the new credentials."
]

xrm_user_messages = [
    "Your XRM account password has been reset. Please use the new password provided via Teams or phone.",
    "We have reset your XRM account password. Use the new credentials to log in.",
    "Your XRM password has been changed. Please log in with the new password we've shared.",
    "Password reset for your XRM account is complete. You can now access your account.",
    "Your XRM account has been reset. Use the new password provided to you.",
    "We've successfully reset your XRM password. Please check Teams or your phone for the new password.",
    "Your XRM account password has been updated. Log in using the new credentials.",
    "Password reset completed for XRM. Use the new password to log in.",
    "Your XRM account is now accessible. Please use the new password we've sent you.",
    "We've reset your XRM password as requested. You can now log in with the new password."
]

spectra_user_messages = [
    "Your Spectra account has been unfrozen and reset. Please use the new password to log in.",
    "We have unfrozen your Spectra account. Use the new credentials provided to access your account.",
    "Your Spectra account is now active. Please log in with the new password we've shared.",
    "Account unfrozen and password reset. You can now access your Spectra account.",
    "Your Spectra account has been restored. Use the new password to log in.",
    "We've unfrozen your Spectra account and reset your password. Please use the new credentials.",
    "Your Spectra account is accessible again. Log in with the new password provided.",
    "Spectra account unfrozen. Please use the new password to access your account.",
    "Your account has been unfrozen and reset. You can now log in to Spectra.",
    "We've reactivated your Spectra account. Please log in using the new password."
]

# Known issue types
issue_types = ['ad', 'xrm', 'spectra']

# Function to parse the input data
def parse_input(input_data):
    lines = input_data.strip().split("\n")
    data = {
        "name": None,
        "issue": None,
        "transaction_id": None,
        "phone_number": None,
        "asset_tag": None
    }

    for line in lines:
        line = line.strip()
        line_lower = line.lower()
        issue_found_in_line = False  # Flag to indicate if issue type was found in this line

        # Check for issue type within the line using word boundaries
        for issue in issue_types:
            pattern = r'\b' + re.escape(issue) + r'\b'
            if re.search(pattern, line_lower):
                data["issue"] = issue
                issue_found_in_line = True
                break  # Exit the loop once the issue type is found

        if issue_found_in_line:
            continue  # Skip processing the rest of the line since issue type is already found

        # Check for transaction ID (assuming it's a 6-digit number)
        if re.match(r'^\d{6}$', line):
            data["transaction_id"] = line
        # Check for phone number (assuming it starts with + or country code and is 10+ digits)
        elif re.match(r'^(\+?\d{10,15})$', line):
            data["phone_number"] = line
        # Check for asset tag formats
        elif re.match(r'^\d{5}$', line):  # 5-digit asset tag
            data["asset_tag"] = line
        elif re.match(r'^(LT|DT)-[A-Za-z0-9]+$', line):  # LT- or DT- followed by alphanumerics
            data["asset_tag"] = line
        # Assume any line with alphabetic characters and spaces is a name
        elif re.match(r'^[A-Za-z\s]+$', line):
            data["name"] = line
        # If none of the above, try to infer based on content
        else:
            # If transaction ID is missing and line is numeric
            if data["transaction_id"] is None and line.isdigit():
                data["transaction_id"] = line
            # If phone number is missing and line matches phone number pattern
            elif data["phone_number"] is None and re.match(r'^\d{10,15}$', line):
                data["phone_number"] = line
            # If asset tag is missing and line matches asset tag pattern
            elif data["asset_tag"] is None and re.match(r'^[A-Za-z0-9\-]+$', line):
                data["asset_tag"] = line
            # If name is missing
            elif data["name"] is None:
                data["name"] = line

    # Check if essential data is missing
    if not data["name"] or not data["issue"] or not data["transaction_id"]:
        return None
    else:
        return data

# Function to generate the appropriate message based on the issue
def generate_message(data):
    issue_type = data["issue"]

    # Select summary, description, internal message, and user reply based on issue type
    if issue_type == "ad":
        summary = random.choice(password_reset_summaries)
        description = random.choice(password_reset_descriptions)
        internal_message = random.choice(password_reset_internal_messages)
        user_message_body = random.choice(password_reset_user_messages)
        app_name = "Active Directory"
    elif issue_type == "xrm":
        summary = random.choice(xrm_account_summaries)
        description = random.choice(xrm_descriptions)
        internal_message = random.choice(xrm_internal_messages)
        user_message_body = random.choice(xrm_user_messages)
        app_name = "XRM"
    elif issue_type == "spectra":
        summary = random.choice(spectra_account_summaries)
        description = random.choice(spectra_descriptions)
        internal_message = random.choice(spectra_internal_messages)
        user_message_body = random.choice(spectra_user_messages)
        app_name = "Spectra"
    else:
        summary = "Issue Summary"
        description = "No specific description available for this issue type."
        internal_message = "No internal message available for this issue type."
        user_message_body = "Your issue has been resolved."
        app_name = data["issue"]

    # Construct the reply message
    user_reply = f"Hello {data['name']},\n\n{user_message_body}\n\nBest regards,\nSupport Team"

    # Display the generated request in the specified format
    st.subheader("Raise this request on behalf of")
    st.code(data['name'], language='text')

    st.subheader("Application Name")
    st.code(app_name, language='text')

    st.subheader("Summary")
    st.code(summary, language='text')

    st.subheader("Description")
    st.code(description, language='text')

    # Display Transaction ID
    st.subheader("Transaction ID")
    st.code(data['transaction_id'], language='text')

    # Optionally, display Asset Tag if it exists
    if data.get('asset_tag'):
        st.subheader("Asset Tag")
        st.code(data['asset_tag'], language='text')

    # Optionally, display Phone Number if it exists
    if data.get('phone_number'):
        st.subheader("Phone#")
        st.code(data['phone_number'], language='text')

    # Internal Message
    st.subheader("Internal Message")
    st.code(internal_message, language='text')

    # Reply on Jira
    st.subheader("Reply on Jira")
    st.code(user_reply, language='text')

# Parse the input and generate message when a button is clicked
if st.button("Generate Request"):
    parsed_data = parse_input(input_data)
    if parsed_data:
        generate_message(parsed_data)
    else:
        st.error("Please ensure the input contains at least Name, Issue, and Transaction ID.")
