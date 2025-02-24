# Fit Fusion

Fit Fusion is a personal fitness tracker web application built with Flask. It helps users manage their fitness journey by tracking workouts, calculating key metrics like BMI and TDEE, and providing tailored workout recommendations—all in a clean, responsive interface with dark/light mode support.

## Features

- **User Authentication:**  
  Secure registration, login, and logout functionalities with password hashing.

- **User Profile:**  
  View and update personal information such as username, email, age, gender, height (entered in feet/inches), weight (in lbs), activity level, workout preference, and fitness goals.

- **Workout Logging:**  
  Log workouts with details including workout type, exercise, sets, reps, and current weight. All entries are saved in a SQLite database.

- **Progress Tracking:**  
  Visualize fitness progress with interactive charts that display weight changes (in lbs) and BMI trends over time using Matplotlib.

- **Calorie and TDEE Calculation:**  
  Automatically calculates Total Daily Energy Expenditure (TDEE) based on user data and suggests calorie maintenance and deficit plans.

- **Recommended Workouts:**  
  Provides personalized workout suggestions based on the user's workout preference (e.g., cardio, weight training, or strength training).

- **Dark/Light Mode Toggle:**  
  Enhance your experience with a dark mode toggle, allowing you to switch between light and dark themes.

- **Responsive Design:**  
  Built using Bootstrap 5, ensuring a seamless experience across devices.

## Technologies Used

- **Backend:** Python, Flask, SQLAlchemy, Werkzeug (for password hashing)
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Database:** SQLite
- **Charting:** Matplotlib
- **Others:** Base64 (for encoding images)

## Installation and Setup

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd fit-fusion
