import streamlit as st
import random

# Set page config
st.set_page_config(page_title="Support Request App", layout="centered")

# User input for name
user_name = st.text_input("Enter your name:")
number = st.text_input("Enter your contact number:")
location = st.text_input("Enter your location:")
trailer_number = st.text_input("Enter the trailer number:")

# List of predefined messages for "Fix an account problem"
account_problem_messages = [
    "I am experiencing difficulties logging into my Windows account. Despite multiple attempts, I am unable to access my account. Each time I try to log in, I encounter an error message or the login screen does not accept my credentials. This issue has been persistent and is preventing me from accessing my files and applications. I have checked my internet connection and confirmed that my password is correct. However, the problem still persists. Could you please assist me in resolving this login issue?",
    "I am having trouble logging into my Windows account. I have tried multiple times, but I keep getting an error message or my credentials are not accepted. I have confirmed that my internet connection and password are correct. Can you help me resolve this issue?",
    "I'm unable to log into my Windows account. Each attempt results in an error or rejection of my credentials. I've verified my internet connection and password. Please assist me with this problem.",
    "I can't log into my Windows account. My credentials are not accepted, and I get an error message each time. I've checked my internet and password. Could you help?",
    "I am having login issues with my Windows account. My credentials aren't being accepted. I’ve verified my internet and password. Please help.",
    "Trouble logging into my Windows account. Credentials not accepted despite correct internet and password. Need help.",
    "Can't log into Windows. Credentials rejected. Internet and password are correct. Help needed.",
    "Unable to log into Windows. Credentials fail. Checked internet and password. Assistance required.",
    "Logging issue with Windows. Correct credentials not working. Need assistance.",
    "Windows login problem. Credentials fail. Please help.",
    "Windows login issue. Credentials not accepted. Help needed.",
    "Windows login trouble. Need help.",
    "Can't log into Windows. Help.",
    "Windows login fail. Assistance?",
    "Login issue. Help!"
]

# List of predefined messages for "Trailer static issue"
trailer_problem_messages = [
    "There is no internet connection available on the trailer. Despite multiple attempts to troubleshoot, I am unable to establish a connection. The router appears to be functioning, but the devices cannot access the internet. I have checked the cables and rebooted the system several times without success. This issue is affecting our ability to work and communicate effectively. Could you please provide assistance in resolving this connectivity problem?",
    "There is no internet connection on the trailer. I have tried troubleshooting but can't establish a connection. The router seems fine, but devices can't access the internet. I have checked cables and rebooted multiple times. Could you assist with this issue?",
    "No internet on the trailer. I've tried troubleshooting, but nothing works. Router appears fine, but devices can't connect. Checked cables and rebooted. Need help.",
    "No internet in the trailer. Troubleshooting failed. Router seems okay, but devices can't connect. Checked everything. Please help.",
    "Trailer has no internet. Router works, devices don't connect. Tried troubleshooting. Need help.",
    "No internet on trailer. Router seems fine, but no connection. Tried everything. Help needed.",
    "Internet down in trailer. Router okay, no device connection. Troubleshooting failed. Need assistance.",
    "No internet connection in trailer. Router fine, devices not connecting. Tried fixing. Need help.",
    "Trailer internet issue. Router works, no device connection. Need help.",
    "No internet on trailer. Router fine, devices not connecting. Help needed.",
    "No internet in trailer. Devices can't connect. Help.",
    "Trailer internet down. Need help.",
    "No internet on trailer. Help.",
    "Trailer internet issue. Assist?",
    "Internet out. Help!"
]

# List of predefined summaries for "XRM Account Reset"
xrm_account_summaries = [
    "XRM Account Reset Required",
    "Need Assistance with XRM Account Reset",
    "Request for XRM Account Reset",
    "XRM Account Login Issue",
    "XRM Account Reset Needed"
]

# List of predefined messages for "XRM Account Reset"
xrm_account_descriptions = [
    "I am unable to access my XRM account despite entering the correct credentials. Please reset my account to resolve the issue.",
    "My XRM account credentials are not working. I have tried resetting my password, but the problem persists. Please assist.",
    "I have been locked out of my XRM account. Each attempt to log in fails, even with the correct username and password. I need a reset.",
    "Despite multiple attempts, I cannot log into my XRM account. The credentials are being rejected. Please reset my account.",
    "I am facing issues accessing my XRM account. The login page does not accept my credentials. A reset is required.",
    "My XRM account is inaccessible. I have verified my credentials and internet connection, but still can't log in. Please help with a reset.",
    "I've tried to log into my XRM account several times without success. My credentials seem to be invalid. Please reset my account.",
    "I cannot access my XRM account. Even after password reset attempts, the issue persists. Assistance needed for account reset.",
    "My XRM account login fails every time. I have checked my credentials, but still can't get in. A reset is required.",
    "The XRM account login page is not accepting my credentials. I need a reset to resolve the issue.",
    "Unable to log into my XRM account. The credentials are correct but still not working. Please reset my account.",
    "I am facing login issues with my XRM account. Despite correct credentials, access is denied. Need an account reset.",
    "I cannot access my XRM account. Login attempts fail even with correct credentials. A reset is needed.",
    "My XRM account is not accepting my password. After several tries, I still can't log in. Please reset my account.",
    "Having trouble accessing my XRM account. The credentials are being rejected. Please help by resetting my account."
]

# Function to generate messages based on the selected issue
def generate_message(issue):
    if issue == "Fix an account problem":
        st.subheader("Summary")
        st.write("Account Reset Required")
        
        st.subheader("Description")
        message = random.choice(account_problem_messages)
        st.write(f"{message}")
        
        st.subheader("Internal Note")
        st.write("The account has been successfully reset in Active Directory, and the issue has been resolved.")
    elif issue == "Trailer static issue":
        st.subheader("Summary")
        st.write("Trailer is experiencing static issues.")
        
        st.subheader("Description")
        message = random.choice(trailer_problem_messages)
        st.write(f"{message}")
        
        st.subheader("Internal Note")
        st.write("Provided instructions to the user to flush the DNS using 'ipconfig /flushdns' and 'ipconfig /release'. The user has confirmed that the issue has been resolved.")
    elif issue == "XRM Account Reset":
        st.subheader("Summary")
        summary = random.choice(xrm_account_summaries)
        st.write(f"{summary}")
        
        st.subheader("Description")
        description = random.choice(xrm_account_descriptions)
        st.write(f"{description}")
        
        st.subheader("Internal Note")
        st.code("The XRM account password has been successfully reset, and the issue has been resolved.")

# Generate message when a button is clicked
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Fix an account problem"):
        generate_message("Fix an account problem")
with col2:
    if st.button("Trailer static issue"):
        generate_message("Trailer static issue")
with col3:
    if st.button("XRM Account Reset"):
        generate_message("XRM Account Reset")

# Show a toast message using st.toast (experimental feature)
if st.button("Submit"):
    st.toast("Your request has been submitted.", icon="🎉")

# Display experimental dialog for more user interactions
if st.button("Need Help?"):
    with st.experimental_dialog("Support Dialog"):
        st.write("You can contact our support team at support@example.com or call 1-800-123-4567 for further assistance.")
