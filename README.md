***Courses Recommendation System***
This repository contains the code for a Courses Recommendation System developed as part of my Final Year Project (FYP). This system uses content-based filtering and collaborative filtering to recommend courses to users based on their preferences and past course history.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------
Table of Contents
Introduction
Features
Project Structure
Installation
Usage
Screenshots
Technologies Used
Acknowledgments


**Introduction**
The Courses Recommendation System is designed to help users find courses that match their interests and preferences. Users receive recommendations based on the similarity of course content and other users' preferences. The system includes distinct sessions for users and admins and provides personalized course suggestions.

Recommendation Techniques
Content-Based Filtering: Recommends courses based on similar course attributes.
Collaborative Filtering: Recommends courses based on user preferences and similarities between users’ course histories.

**Features**
User Features
User Signup/Login: Users can create an account and log in securely.
Home Page: Displays the user's course history.
Content-Based Recommendation: Users can search for courses similar to a specified course.
Collaborative Filtering Recommendation: Suggests courses based on similar users' preferences.
Logout: Ends the session and redirects to the login page.
Admin Features
Admin Signup/Login: The first signup instance creates an admin account.
User History Page: Shows a list of all registered users and their course histories.
User Management: Admins can delete user accounts and course histories.
Logout: Ends the admin session and redirects to the login page.

**Project Structure**
├── data
│   ├── courses.csv              # Coursera dataset for 3000 courses
│   ├── users.json               # JSON file to store user account data
│   ├── admin.json               # JSON file to store admin account data
├── model
│   ├── similarity.pkl           # Precomputed similarity matrix for content-based filtering
│   ├── courses.pkl              # Processed courses data for recommendations
├── src
│   ├── app.py                   # Streamlit app with UI and recommendation logic
│   ├── utils.py                 # Utility functions for data processing
│   ├── collaborative_filtering.py # Collaborative filtering functions
│   ├── content_based_filtering.py # Content-based filtering functions
├── README.md                    # Project documentation
└── requirements.txt             # Python dependencies

**Installation**
Clone the Repository

bash
Copy code
git clone https://github.com/yourusername/courses-recommendation-system.git
cd courses-recommendation-system
Install Dependencies

bash
Copy code
pip install -r requirements.txt
Prepare Dataset

Ensure courses.csv is in the data directory.
Run preprocessing scripts to generate similarity.pkl and courses.pkl.
Start the Streamlit App

bash
Copy code
streamlit run src/app.py


**Usage**
Run the Application: After installation, navigate to the Streamlit app in your browser.
User Signup/Login: Create a user account or log in.
Admin Features: Access user history and manage accounts.
Recommendations:
Go to the Content-Based Recommendation page to get course suggestions based on a selected course.
Go to the Collaborative Filtering page to view recommendations based on similar users' preferences.

**Screenshots**
User Home Page
Content-Based Filtering Page
Collaborative Filtering Page
Admin User Management Page
(Add screenshots here for a visual representation of the interface.)

**Technologies Used**
Python: Core programming language for logic and data processing.
Streamlit: For building the web interface.
Pandas & NumPy: Data handling and matrix operations.
Scikit-Learn: Cosine similarity calculations.
JSON: User and admin data storage.
Pickle: For saving and loading model files (similarity.pkl and courses.pkl).


Acknowledgments
Special thanks to Coursera for the dataset and Streamlit for the interactive web app framework.

This project was developed as part of my Final Year Project. For questions or feedback, please contact me at hassan7538216@gmail.com.
