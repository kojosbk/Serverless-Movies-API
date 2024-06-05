import streamlit as st

def capitalize_name(name):
    return " ".join(word.capitalize() for word in name.split())

def generate_message(manager, name):
    manager = capitalize_name(manager)
    name = capitalize_name(name)
    
    names = name.split()
    first_name = names[0]
    last_name = names[-1]
    
    username = f"{first_name.lower()}.{last_name.lower()}"
    user_email = f"{username}@inhealthgroup.com"
    password = "Inhealth24"
    
    message = f"""
    Hello {manager},
    
    Please find attached the login details of {name}
    
    Username: {username}
    User email: {user_email}
    Password: {password}
    """
    return message

st.title('Generate Login Details Message')

manager_name = st.text_input("Enter the manager's name")
new_starter_name = st.text_input("Enter the new starter's name")

if st.button('Generate Message'):
    if manager_name and new_starter_name:
        message = generate_message(manager_name, new_starter_name)
        st.text_area("Generated Message", value=message, height=200)
    else:
        st.error("Please enter both the manager's name and the new starter's name")
