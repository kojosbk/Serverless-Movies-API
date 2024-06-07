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
    job_title = data.get("Candidate Job Title", "")
    location = data.get("Location", "")
    telephone = data.get("Telephone", "")

    names = name.split()
    first_name = names[0]
    last_name = names[-1]
    
    username = f"{first_name.lower()}.{last_name.lower()}"
    user_email = f"{username}@inhealthgroup.com"
    password = "Inhealth24"
    
    return {
        "Candidate's First Name": first_name,
        "Candidate's Last Name": last_name,
        "Username": username,
        "Password": password,
        "Candidate's Full Name": name,
        "Job Title": job_title,
        "Office Location": location,
        "Company": "InHealth Group",
        "Hiring Manager": manager,
        "Gdrive": f"\\\\IHGD\\Homefolder\\Profiles\\{username}\\Documents",
        "Mobile Number": telephone,
        "Security Group Membership": "Please copy the group permissions of the person you are to mirror",
        "Message to Send to Manager": f"Dear {manager},\n\nPlease find the login details for {name} below:\n\nUsername: {username}\nUser Email: {user_email}\nPassword: {password}\n\nBest regards,\nYour IT Team"
    }

def copy_to_clipboard(text, key):
    js_code = f"""
    <script>
    function copyToClipboard(text, key) {{
        navigator.clipboard.writeText(text).then(function() {{
            var tick = document.getElementById(key + '_tick');
            if (tick) {{
                tick.style.display = 'inline';
            }}
        }}, function(err) {{
            console.error('Could not copy text: ', err);
        }});
    }}
    copyToClipboard("{text}", "{key}");
    </script>
    """
    st.components.v1.html(js_code, height=0)

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
        st.text(value)
        copy_button_html = f"""
        <div style="display: flex; align-items: center; margin-top: 5px;">
            <button id="{key}_button" style="background-color: #007BFF; color: white; padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer;" onclick="copyToClipboard('{value}', '{key}')">Copy {key}</button>
            <span id="{key}_tick" style="color: green; display: none; margin-left: 10px;">✔️</span>
        </div>
        <script>
        function copyToClipboard(text, key) {{
            navigator.clipboard.writeText(text).then(function() {{
                var tick = document.getElementById(key + '_tick');
                if (tick) {{
                    tick.style.display = 'inline';
                }}
            }}, function(err) {{
                console.error('Could not copy text: ', err);
            }});
        }}
        </script>
        """
        st.components.v1.html(copy_button_html, height=45)
