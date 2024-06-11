import streamlit as st

def capitalize_name(name):
    return " ".join(word.capitalize() for word in name.split())

def get_initials(name):
    return "".join([word[0].upper() for word in name.split()])

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

def generate_message(data):
    manager = capitalize_name(data.get("Hiring Manager Name", ""))
    name = capitalize_name(data.get("Candidate Name", ""))
    job_title = data.get("candidate Job Title", "") or data.get("Candidate Job Title", "")  # Handle both variations
    location = data.get("Location", "")
    telephone = data.get("Candidate Mobile Number", "")
    address = data.get("Candidate Address", "")

    names = name.split()
    first_name = names[0]
    last_name = names[-1]
    initials = get_initials(name)
    
    username = f"{first_name.lower()}.{last_name.lower()}"
    user_email = f"{username}@inhealthgroup.com"
    password = "Inhealth24"
    
    internal_note = f"Account created for {name} . Email sent to {manager} via teams regarding account details."
    
    return {
        "Candidates First Name": first_name,
        "Candidates Last Name": last_name,
        "Initials": initials,
        "Username": username,
        "Password": password,
        "Candidate's Full Name": name,
        "Description": job_title,
        "Office": location,
        "Job Title": job_title,
        "Company": "InHealth Group",
        "Manager": manager,
        "Gdrive Documents": f"\\\\IHGD\\Homefolder\\Profiles\\{username}\\",
        "Mobile": telephone,
        "Address": address,
        "Message to Send Manager": f"""Hello {manager},

Please find the login details for {name} below:

Username: {username}
User Email: {user_email}
Password: {password}

Best regards,
Your IT Team""",
        "Internal Note": internal_note
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
    for key, value in st.session_state.generated_data.items():
        st.subheader(key)
        st.code(value, language='plaintext')

