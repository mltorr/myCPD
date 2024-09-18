import streamlit as st
import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'username' not in st.session_state:
    st.session_state.username = ""

if 'full_name' not in st.session_state:
    st.session_state.full_name = ""

if 'user_type' not in st.session_state:
    st.session_state.user_type = ""

if 'page' not in st.session_state:
    st.session_state.page = "Login"

# Path to JSON files
cpd_file = "cpd_records.json"
user_credentials_file = "users.json"

# Load user credentials from JSON file
def load_user_credentials():
    try:
        with open(user_credentials_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Load CPD data from JSON file
def load_data():
    try:
        with open(cpd_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save CPD data to JSON file
def save_data(data):
    with open(cpd_file, "w") as f:
        json.dump(data, f, indent=4)

def load_users():
    with open('users.json', 'r') as file:
        return json.load(file)

def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file, indent=4)

def add_user(username, password, full_name, user_type):
    users = load_users()
    if any(user['username'] == username for user in users):
        return "User already exists"
    
    new_user = {
        "username": username,
        "password": password,
        "full_name": full_name,
        "user_type": user_type
    }
    users.append(new_user)
    save_users(users)
    return "User added successfully"

def edit_user(username, password, full_name, user_type):
    users = load_users()
    for user in users:
        if user['username'] == username:
            user['password'] = password
            user['full_name'] = full_name
            user['user_type'] = user_type
            save_users(users)
            return "User updated successfully"
    
    return "User not found"

def manage_users():
    st.title("Manage Users")

    # Load users for dropdown
    users = load_users()
    usernames = [user['username'] for user in users]

    # Form for adding a new user
    st.header("Add New User")
    with st.form(key='add_user_form'):
        add_username = st.text_input("Username")
        add_password = st.text_input("Password", type='password')
        add_full_name = st.text_input("Full Name")
        add_user_type = st.selectbox("User Type", ["user", "admin"])
        add_user_button = st.form_submit_button("Add User")

        if add_user_button:
            result = add_user(add_username, add_password, add_full_name, add_user_type)
            st.success(result)

    # Form for editing an existing user
    st.header("Edit Existing User")
    with st.form(key='edit_user_form'):
        edit_username = st.selectbox("Select Username to Edit", usernames)
        edit_password = st.text_input("New Password", type='password')
        edit_full_name = st.text_input("New Full Name")
        edit_user_type = st.selectbox("New User Type", ["user", "admin"])
        edit_user_button = st.form_submit_button("Edit User")

        if edit_user_button:
            result = edit_user(edit_username, edit_password, edit_full_name, edit_user_type)
            st.success(result)


# Login Page
def login():
    st.title("Login to myCPD Portal")

    users = load_user_credentials()

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.button("Login")

    if submit:
        for user in users:
            if user['username'] == username and user['password'] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.full_name = user['full_name']
                st.session_state.user_type = user['user_type']
                st.session_state.page = "Dashboard"  # Redirect to the dashboard after login
                st.experimental_rerun()
                return
        st.error("Invalid username or password")

# Page to log new CPD's
def log_or_edit_cpd(edit_mode=False, cpd_to_edit=None):
    if "username" not in st.session_state:
        st.error("No user is logged in. Please log in first.")
        return

    username = st.session_state.username
    st.title(f"Log CPD Activity for {username}")

    if edit_mode and cpd_to_edit:
        title = cpd_to_edit["Title"]
        cpd_type = cpd_to_edit["Type"]
        hours = cpd_to_edit["Hours"]
        date = datetime.strptime(cpd_to_edit["Date"], "%Y-%m-%d")
        organization = cpd_to_edit["Organization"]
        description = cpd_to_edit["Description"]
        learning_outcomes = cpd_to_edit["Learning outcomes"]
        links = cpd_to_edit["Links"]
        certificate = cpd_to_edit.get("Certificate", None)
    else:
        title = ""
        cpd_type = "Event"
        hours = 0.0
        date = datetime.today()
        organization = ""
        description = ""
        learning_outcomes = ""
        links = ""
        certificate = None

    with st.form("cpd_form"):
        title = st.text_input("CPD Title", value=title)
        cpd_type = st.selectbox("Type of CPD", ["Event", "Seminar", "Webinar", "Training Course", "Training Video"], index=["Event", "Seminar", "Webinar", "Training Course", "Training Video"].index(cpd_type))
        hours = st.number_input("Number of CPD Hours", min_value=0.0, step=0.5, value=hours)
        date = st.date_input("Date of CPD Activity", value=date)
        organization = st.text_input("Name of Organization Providing the Training", value=organization)
        description = st.text_area("Description", value=description)
        learning_outcomes = st.text_area("Learning Outcomes and Objectives", value=learning_outcomes)
        links = st.text_input("Supporting Links", value=links)
        certificate = st.file_uploader("Upload Certificate (PDF)", type=["pdf"])

        submit = st.form_submit_button("Submit")

        if submit:
            data = load_data()

            username = st.session_state.username

            if edit_mode and cpd_to_edit:
                index = data.index(cpd_to_edit)
                data[index] = {
                    "Username": username,
                    "Title": title,
                    "Type": cpd_type,
                    "Hours": hours,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Organization": organization,
                    "Description": description,
                    "Learning outcomes": learning_outcomes,
                    "Links": links,
                    "Certificate": certificate.name if certificate else cpd_to_edit.get("Certificate", None)
                }
                st.success("CPD activity updated successfully.")
            else:
                new_record = {
                    "Username": username,
                    "Title": title,
                    "Type": cpd_type,
                    "Hours": hours,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Organization": organization,
                    "Description": description,
                    "Learning outcomes": learning_outcomes,
                    "Links": links,
                    "Certificate": certificate.name if certificate else None
                }
                data.append(new_record)
                st.success("CPD activity logged successfully.")

            save_data(data)

#Edit CPD entries
def edit_cpd():
    st.title("Edit CPD Activity")

    data = load_data()

    username = st.session_state.username
    user_data = [record for record in data if record.get("Username") == username]

    if not user_data:
        st.write("No CPD records found.")
        return

    cpd_titles = [f"{record['Title']} ({record['Date']})" for record in user_data]
    selected_cpd = st.selectbox("Select a CPD record to edit", cpd_titles)

    cpd_to_edit = user_data[cpd_titles.index(selected_cpd)]

    log_or_edit_cpd(edit_mode=True, cpd_to_edit=cpd_to_edit)

#Dashboard for Admin usertype users
def admin_dashboard():
    st.title("Admin Dashboard")

    data = load_data()
    users = load_user_credentials()

    if not data:
        st.write("No CPD records found.")
        return

    users_df = pd.DataFrame(users)
    user_only_df = users_df[users_df['user_type'] == 'user']

    user_cpd_hours = []
    for user in user_only_df['username']:
        user_data = pd.DataFrame([record for record in data if record.get('Username', '') == user])

        total_cpd_hours = user_data['Hours'].sum() if not user_data.empty else 0
        user_cpd_hours.append(total_cpd_hours)

    user_only_df['Total CPD Hours'] = user_cpd_hours
    user_only_df['Target Hours'] = 40
    user_only_df['Percentage Completed'] = (user_only_df['Total CPD Hours'] / user_only_df['Target Hours']) * 100

    fig, ax = plt.subplots()
    ax.bar(user_only_df['full_name'], user_only_df['Total CPD Hours'], color='skyblue')
    ax.set_xlabel("User")
    ax.set_ylabel("Total CPD Hours")
    ax.set_title("Total CPD Hours Per User")
    st.pyplot(fig)

    st.subheader("CPD Data Table")
    user_only_df.rename(columns={'full_name': 'Name'}, inplace=True)
    st.table(user_only_df[['Name', 'Total CPD Hours', 'Target Hours', 'Percentage Completed']])

def generate_pie_chart(cpd_by_type):
    fig, ax = plt.subplots(figsize=(6, 6))
    colors = plt.get_cmap('Set3')(range(len(cpd_by_type)))
    ax.pie(cpd_by_type, labels=cpd_by_type.index, autopct='%1.1f%%', startangle=90, wedgeprops={'width': 0.5}, colors=colors)
    ax.axis('equal')
    plt.tight_layout()
    return fig

def encode_image_to_base64(fig):
    import io
    import base64
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    return img_str

# Dashboard Page for usertype = users
def dashboard():
    st.title(f"Welcome {st.session_state.full_name}")

    data = load_data()  # Ensure this function is defined elsewhere

    user_data = pd.DataFrame([record for record in data if record.get('Username', '') == st.session_state.username])

    if user_data.empty:
        st.write("No CPD records found for you.")
        return

    user_data['Date'] = pd.to_datetime(user_data['Date'], format="%Y-%m-%d")

    current_year = datetime.now().year
    this_year_df = user_data[user_data['Date'].dt.year == current_year]
    total_cpd_hours_year = this_year_df['Hours'].sum()
    percentage_completed = (total_cpd_hours_year / 40) * 100

    total_cpd_hours_lifetime = user_data['Hours'].sum()

    cpd_by_type = user_data['Type'].value_counts()

    # Create a container with a white background, gap, and shadow
    with st.container():
        st.markdown(
            """
                <div style="display: flex; gap: 20px;">
                    <div style="flex: 1; background-color: #f9f9f9; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <h3>Total CPD Hours This Year</h3>
                        <p><strong>Completed Hours:</strong> {}</p>
                        <p><strong>Yearly Goal (40 hrs):</strong> {:.2f}%</p>
                        <div style="width: 100%; background-color: #e0e0e0; border-radius: 5px; height: 20px;">
                            <div style="width: {:.2f}%; background-color: #4caf50; height: 100%; border-radius: 5px;"></div>
                        </div>
                    </div>
                    <div style="flex: 1; background-color: #f9f9f9; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <h3>Total Lifetime CPD Hours</h3>
                        <p><strong>Completed Hours:</strong> {}</p>
                    </div>
                    <div style="flex: 1; background-color: #f9f9f9; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <h3>CPD Completed by Type</h3>
                        <img src="data:image/png;base64,{}" style="max-width: 100%;"/>
                    </div>
                </div>
            """.format(
                total_cpd_hours_year,
                percentage_completed,
                percentage_completed,
                total_cpd_hours_lifetime,
                encode_image_to_base64(generate_pie_chart(cpd_by_type))
            ),
            unsafe_allow_html=True
        )



    st.subheader("CPD Records Summary")
    st.write(user_data[['Title', 'Type', 'Hours', 'Date', 'Organization', 'Description', 'Learning outcomes', 'Links']])

    # Include Font Awesome for icons
    st.markdown('''
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    ''', unsafe_allow_html=True)

    # Display three cards per row
    page_bg_img = f"""
    <style>
    /* Stretch the content to fit the window size */
    [data-testid="stAppViewContainer"] > .main {{
        padding-left: 10px;
        padding-right: 10px;
        max-width: 100%;
        width: 100%;
        margin: 0;
    }}

    /* Adjust the scaling box to have a fixed height and handle overflow */
    .scaling-box {{
        background-color: #F9F9F9;
        border: 1px solid #ddd;
        padding: 10px;
        margin: 10px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: 0.3s;
        border-radius: 5px;
        text-align: left;
        height: 500px; /* Fixed height */
        display: flex;
        flex-direction: column;
        overflow: hidden; /* Hide overflowing content */
    }}

    .scaling-box:hover {{
        transform: scale(1.05);
    }}

    /* Handle expandable content within the box */
    .scaling-box .scaling-box-inner {{
        overflow-y: auto; /* Scrollable content */
        flex: 1; /* Take remaining space */
    }}

    /* Reduce margins between columns */
    .stColumn {{
        padding-left: 5px;
        padding-right: 5px;
    }}

    /* Hide the Streamlit top padding */
    .css-1d391kg {{
        padding-top: 0 !important;
    }}

    h3 {{
        --tw-text-opacity: 1;
        color: rgb(102 102 102/var(--tw-text-opacity));
        line-height: 1.5;
        font-weight: 600;
        font-size: 1.525rem;
        white-space: wrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin: 0;
    }}
    </style>
    """

    st.markdown(page_bg_img, unsafe_allow_html=True)

    # Show CPD activities in 3 columns
    st.title("CPD Activities")

    # Number of columns for each row
    num_cols = 2
    applist = st.container()

    # Assuming 'user_data' is the dataframe you're working with
    for i in range(0, len(user_data), num_cols):
        row = applist.columns(num_cols)
        for j in range(num_cols):
            if i + j < len(user_data):
                activity = user_data.iloc[i + j]
                with row[j]:
                    st.markdown(f'''
                        <div class="scaling-box">
                            <h3>{activity["Title"]}</h3>
                            <div class="scaling-box-inner">
                                <p><i class="fas fa-calendar-day"></i> <strong>Date of CPD Activity: </strong>{activity["Date"].strftime("%Y-%m-%d")}</p>
                                <p><i class="fas fa-tag"></i> <strong>Type:</strong> {activity["Type"]}</p>
                                <p><i class="fas fa-building"></i> <strong>Organization:</strong> {activity["Organization"]}</p>
                                <p><i class="fas fa-file-alt"></i> <strong>Description:</strong><p> {activity["Description"]}</p>
                                <p><i class="fas fa-bullhorn"></i> <strong>Outcomes & Objectives:</strong><p> {activity["Learning outcomes"]}</p>
                                <p><i class="fas fa-link"></i> <strong>Links:</strong><p><a href="{activity['Links']}" target="_blank">{activity['Links']}</a></p>
                            </div>
                            <p class="scaling-box-description">
                                <i class="fas fa-clock"></i> <strong>{activity["Hours"]} hours logged</strong>
                                <br>
                                <a href="{activity["Links"]}" style="
                                    display: inline-block; 
                                    padding: 8px 16px; 
                                    border: 1px solid #6200ee; 
                                    border-radius: 5px; 
                                    color: #6200ee; 
                                    text-decoration: none;">
                                    Download certificate
                                </a>
                            </p>
                        </div>
                    ''', unsafe_allow_html=True)

# Logout
def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.full_name = ""
    st.session_state.user_type = ""
    st.session_state.page = "Login"  
    st.experimental_rerun()

# Main app logic
def main():
    if st.session_state.page == "Login":
        login()
    elif st.session_state.authenticated:
        # Sidebar navigation
        st.sidebar.title("Navigation")
        
        if st.session_state.user_type == 'admin':
            page = st.sidebar.selectbox("Select Page", ["Dashboard", "Manage Users"])

            if page == "Dashboard":
                admin_dashboard()
            elif page == "Manage Users":
                manage_users()
            elif page == "Edit CPD":
                edit_cpd()
        else:
            page = st.sidebar.selectbox("Select Page", ["Dashboard", "Log CPD", "Edit CPD"])

            if page == "Dashboard":
                dashboard()
            elif page == "Log CPD":
                log_or_edit_cpd()
            elif page == "Edit CPD":
                edit_cpd()

        # Logout button
        if st.sidebar.button("Logout"):
            logout()

if __name__ == "__main__":
    main()
