import streamlit as st

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

def generate_message(data):
    manager = capitalize_name(data.get("Hiring Manager Name", ""))
    name = capitalize_name(data.get("Candidate Name", ""))
    job_title = data.get("candidate Job Title", "")
    location = data.get("Location", "")
    telephone = data.get("Telephone", "")

    names = name.split()
    first_name = names[0]
    last_name = names[-1]
    
    username = f"{first_name.lower()}.{last_name.lower()}"
    user_email = f"{username}@inhealthgroup.com"
    password = "Inhealth24"
    
    return {
        "Candidates First Name": first_name,
        "Candidates Last Name": last_name,
        "Username": username,
        "Password": password,
        "Candidate's Full Name": name,
        "Description": job_title,
        "Office": location,
        "Job Title": job_title,
        "Company": "InHealth Group",
        "Manager": manager,
        "Gdrive": f"\\\\IHGD\\Homefolder\\Profiles\\{username}\\Documents",
        "Mobile": telephone,
        "MSG": "Please copy the group permissions of the person you are to mirror",
        "Message to Send Manager": f"Hello {manager},\n\nPlease find attached the login details of {name}\n\nUsername: {username}\nUser email: {user_email}\nPassword: {password}"
    }

st.title('Generate User Onboarding Details')

data = st.text_area("Paste the full details here:", height=300)

if st.button('Generate Details'):
    if data:
        parsed_data = parse_input(data)
        message_data = generate_message(parsed_data)
        
        for key, value in message_data.items():
            st.subheader(key)
            st.text(value)
            if st.button(f"Copy {key}", key=f"{key}_button"):
                st.write(f"```{value}```")
                st.success(f"{key} copied to clipboard!")
    else:
        st.error("Please enter the required details")
