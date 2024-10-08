import streamlit as st
import pandas as pd
import pickle
import json
import os
from sklearn.metrics.pairwise import cosine_similarity

# File Paths
SIMILARITY_PATH = 'similarity.pkl'
COURSES_PATH = 'courses.pkl'
USERS_DATA_PATH = 'newdata/users.json'
ADMIN_DATA_PATH = 'newdata/admin.json'

# Custom CSS for styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    body {
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(135deg, #FF69B4, #000000);
        color: white;
    }
    
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    
    .stSelectbox {
        color: #4CAF50;
    }
    
    .stTextInput>div>div>input {
        color: #4CAF50;
    }
    
    .stTitle {
        color: #FF69B4;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .sidebar .sidebar-content {
        background-color: white;
    }
    
    .sidebar .sidebar-content .stSelectbox {
        color: black;
    }
    
    .sidebar .sidebar-content .stRadio > label {
        color: black;
    }
    
    @keyframes fadeIn {
        0% {opacity: 0;}
        100% {opacity: 1;}
    }
    
    .fade-in {
        animation: fadeIn 1s ease-in;
    }
    
    .icon {
        font-size: 24px;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Load the pickle files
@st.cache_data
def load_pickle(file_path):
    try:
        with open(file_path, 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return None

similarity = load_pickle(SIMILARITY_PATH)
courses = load_pickle(COURSES_PATH)

# Initialize JSON files with empty structures if they don't exist
def initialize_json_file(path, initial_data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, 'w') as file:
            json.dump(initial_data, file, indent=4)

initialize_json_file(USERS_DATA_PATH, {"users": []})
initialize_json_file(ADMIN_DATA_PATH, {"admin": []})

# Load and save JSON files
def load_json_file(path):
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {"users": []} if path == USERS_DATA_PATH else {"admin": []}

def save_json_file(path, data):
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to recommend courses (Content-Based Filtering)
def recommend(course_name):
    if not isinstance(courses, pd.DataFrame) or courses.empty or similarity is None:
        st.error("Course data or similarity matrix is not available.")
        return []

    if course_name not in courses['course_name'].values:
        st.error(f"Course '{course_name}' not found in the course list.")
        return []

    index = courses[courses['course_name'] == course_name].index[0]
    distances = similarity[index]
    course_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:9]

    recommended_courses = [courses.iloc[i[0]].course_name for i in course_indices]
    return recommended_courses

# Function to get user history for collaborative filtering
def get_user_history():
    users_data = load_json_file(USERS_DATA_PATH)
    for user in users_data['users']:
        if user['username'] == st.session_state.username:
            return user['history']
    return []

# Function for collaborative filtering recommendations
def collaborative_filtering_recommendations():
    users_data = load_json_file(USERS_DATA_PATH)
    user_history = get_user_history()

    if not user_history:
        return []

    # Create a DataFrame for user preferences
    user_course_matrix = pd.DataFrame(0, index=[user['username'] for user in users_data['users']],
                                      columns=courses['course_name'])
    
    # Fill the matrix
    for user in users_data['users']:
        for course in user['history']:
            if course in user_course_matrix.columns:
                user_course_matrix.at[user['username'], course] = 1

    # Calculate cosine similarity between users
    user_similarity = cosine_similarity(user_course_matrix)
    user_similarity_df = pd.DataFrame(user_similarity, index=user_course_matrix.index, columns=user_course_matrix.index)

    # Get similar users
    similar_users = user_similarity_df[st.session_state.username].sort_values(ascending=False)[1:4]
    
    # Recommend courses based on similar users
    recommended_courses = set()
    for similar_user in similar_users.index:
        for course in users_data['users'][users_data['users'].index(next(u for u in users_data['users'] if u['username'] == similar_user))]['history']:
            if course not in user_history:
                recommended_courses.add(course)

    return list(recommended_courses)

# Unified Signup/Login Page
def auth_page():
    st.title("Signup / Login")
    
    st.sidebar.title("Navigation")
    navigation_choice = st.sidebar.selectbox("Choose an option", ["Login", "Signup"])
    
    if navigation_choice == "Signup":
        st.subheader("Create Admin/User Account")
        user_type = st.selectbox("Sign up as", ["User", "Admin"])

        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Signup"):
            if username and password:
                if user_type == "Admin":
                    admin_data = load_json_file(ADMIN_DATA_PATH)
                    if len(admin_data["admin"]) == 0:
                        admin_data["admin"].append({"username": username, "password": password})
                        save_json_file(ADMIN_DATA_PATH, admin_data)
                        st.success("Admin account created successfully.")
                    else:
                        st.warning("Admin account already exists. Please log in.")
                else:
                    users_data = load_json_file(USERS_DATA_PATH)
                    if any(user.get('username') == username for user in users_data.get('users', [])):
                        st.warning("Username already exists. Please choose another one.")
                    else:
                        users_data['users'].append({"username": username, "password": password, "history": []})
                        save_json_file(USERS_DATA_PATH, users_data)
                        st.success("Signup successful. You can now log in.")
            else:
                st.warning("Both username and password are required.")

    elif navigation_choice == "Login":
        st.subheader("Login")

        login_type = st.selectbox("Login as", ["User", "Admin"])
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if login_type == "Admin":
                admin_data = load_json_file(ADMIN_DATA_PATH)
                if any(admin.get('username') == username and admin.get('password') == password for admin in admin_data.get('admin', [])):
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.username = username
                    st.success("Admin login successful!")
                    st.rerun()
                else:
                    st.error("Invalid admin credentials.")
            elif login_type == "User":
                users_data = load_json_file(USERS_DATA_PATH)
                user_data = next((user for user in users_data.get('users', []) if user['username'] == username), None)
                if user_data and user_data['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = False
                    st.session_state.username = username
                    st.session_state.user_history = user_data.get('history', [])
                    st.success("User login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

# Pages for User
def home_page():
    st.title("Welcome to the Coursera Courses Recommendation System")
    st.write("Discover courses tailored to your interests and needs.")
    
    if st.session_state.get('logged_in') and not st.session_state.get('is_admin'):
        st.write("Your course history:")
        if st.session_state.user_history:
            for course in st.session_state.user_history:
                st.text(course)
        else:
            st.info("No history available. Start exploring courses!")

# Course Recommendation Page (Content-Based)
def recommendation_page():
    st.title("Courses Recommendation (Content-Based)")

    course_names = courses['course_name'].values
    selected_course = st.selectbox("Select a course you like:", course_names)

    if st.button('Show Recommended Courses'):
        recommended_courses = recommend(selected_course)
        if recommended_courses:
            st.write("Recommended Courses based on your interests are:")
            for course in recommended_courses:
                st.text(course)

            # Update user history
            if st.session_state.get('logged_in') and not st.session_state.get('is_admin'):
                users_data = load_json_file(USERS_DATA_PATH)
                for user in users_data['users']:
                    if user['username'] == st.session_state.username:
                        if selected_course not in user['history']:
                            user['history'].append(selected_course)
                        break
                save_json_file(USERS_DATA_PATH, users_data)
                st.success("Your course history has been updated!")

# Collaborative Filtering Page
def collaborative_filtering_page():
    st.title("Collaborative Filtering Recommendations")

    if st.session_state.get('logged_in') and not st.session_state.get('is_admin'):
        recommended_courses = collaborative_filtering_recommendations()
        if recommended_courses:
            st.write("Recommended Courses based on similar users' preferences are:")
            for course in recommended_courses:
                st.text(course)
        else:
            st.info("No recommendations available based on user history. Try exploring more courses!")

# Admin Pages
def user_history_page():
    st.title("User History")

    if st.session_state.get('logged_in') and st.session_state.get('is_admin'):
        users_data = load_json_file(USERS_DATA_PATH)
        if not users_data['users']:
            st.info("No users found in the system.")
            return

        selected_user = st.selectbox("Select a user to view history:", [user['username'] for user in users_data['users']])

        user = next((user for user in users_data['users'] if user['username'] == selected_user), None)
        if user:
            st.write(f"History for {selected_user}:")
            if user['history']:
                for course in user['history']:
                    st.text(course)
            else:
                st.info("No history available for this user.")

            if st.button("Delete History"):
                user['history'] = []
                save_json_file(USERS_DATA_PATH, users_data)
                st.success(f"History for user '{selected_user}' has been deleted.")
                st.rerun()

def delete_user_page():
    st.title("Delete User")

    if st.session_state.get('logged_in') and st.session_state.get('is_admin'):
        users_data = load_json_file(USERS_DATA_PATH)
        if not users_data['users']:
            st.info("No users found in the system.")
            return

        selected_user = st.selectbox("Select a user to delete:", [user['username'] for user in users_data['users']])

        if st.button("Delete User"):
            users_data['users'] = [user for user in users_data['users'] if user['username'] != selected_user]
            save_json_file(USERS_DATA_PATH, users_data)
            st.success(f"User '{selected_user}' has been deleted.")
            st.rerun()

# Logout functionality
def logout_page():
    st.title("Logout")
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("You have been logged out successfully.")
        st.rerun()

# Main Navigation
if 'logged_in' not in st.session_state:
    auth_page()
elif st.session_state.get('logged_in') and st.session_state.get('is_admin'):
    st.sidebar.title("Admin Menu")
    admin_choice = st.sidebar.radio("", ["User History", "Delete User", "Logout"])
    if admin_choice == "User History":
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<i class="icon">📊</i> User History', unsafe_allow_html=True)
        user_history_page()
        st.markdown('</div>', unsafe_allow_html=True)
    elif admin_choice == "Delete User":
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<i class="icon">🗑️</i> Delete User', unsafe_allow_html=True)
        delete_user_page()
        st.markdown('</div>', unsafe_allow_html=True)
    elif admin_choice == "Logout":
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<i class="icon">🚪</i> Logout', unsafe_allow_html=True)
        logout_page()
        st.markdown('</div>', unsafe_allow_html=True)
elif st.session_state.get('logged_in') and not st.session_state.get('is_admin'):
    st.sidebar.title("User Menu")
    user_choice = st.sidebar.radio("", ["Home", "Recommendations (Content-Based)", "Recommendations (Collaborative Filtering)", "Logout"])
    if user_choice == "Home":
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<i class="icon">🏠</i> Home', unsafe_allow_html=True)
        home_page()
    elif user_choice == "Home":
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<i class="icon">🏠</i> Home', unsafe_allow_html=True)
        home_page()
        st.markdown('</div>', unsafe_allow_html=True)
    elif user_choice == "Recommendations (Content-Based)":
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<i class="icon">📚</i> Recommendations (Content-Based)', unsafe_allow_html=True)
        recommendation_page()
        st.markdown('</div>', unsafe_allow_html=True)
    elif user_choice == "Recommendations (Collaborative Filtering)":
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<i class="icon">👥</i> Recommendations (Collaborative Filtering)', unsafe_allow_html=True)
        collaborative_filtering_page()
        st.markdown('</div>', unsafe_allow_html=True)
    elif user_choice == "Logout":
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<i class="icon">🚪</i> Logout', unsafe_allow_html=True)
        logout_page()
        st.markdown('</div>', unsafe_allow_html=True)

# Add this at the end of your script to ensure proper styling
st.markdown("""
<script>
    var elements = window.parent.document.querySelectorAll('.stSelectbox');
    elements.forEach(function(element) {
        element.style.color = 'black';
    });
</script>
""", unsafe_allow_html=True)