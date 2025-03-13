# Fit Fusion

Fit Fusion is a Flask-based fitness tracking application that allows users to:

- Register and log in.
- Track workouts (with sets, reps, and weight).
- View a paginated workout history (10 per page).
- Edit or delete individual workouts via a 3‑dot dropdown menu.
- Monitor progress with a Matplotlib-based weight/BMI chart.
- Update personal profile information.
- Reset passwords on-site (no email verification).
- Download personal data in JSON format.
- Interact with Fit Bot for quick fitness Q&A and references to tutorials.

## Features

1. **User Authentication**  
   - Register a new account, specifying age, gender, height (in feet/inches), and weight (in lbs).
   - Log in securely (passwords hashed with PBKDF2).
   - Log out to clear sessions.

2. **Dashboard**  
   - Displays user’s BMI, current weight, and TDEE-based calorie plan.
   - Shows a Matplotlib-generated chart of weight and BMI over time.
   - Paginated workout history (10 per page) with 3‑dot dropdown for edit/delete.
   - Allows logging new workouts with sets, reps, and weight.

3. **Workout Management**  
   - **Add Workouts**: Choose workout type (Cardio, Weight Training, Strength Training), specify sets, reps, and weight.
   - **Edit Workouts**: Update an existing workout via an edit page.
   - **Delete Workouts**: Remove workouts you no longer need.

4. **On-Site Password Reset**  
   - “Forgot Password” workflow that verifies email and allows resetting on-site without email links.

5. **Profile & Privacy**  
   - Update personal info (username, email, age, gender, height, weight).
   - Download personal data (including workout logs) as JSON.
   - View personal data on a privacy tab.

6. **Tutorials & Multimedia**  
   - Separate pages for tutorials and multimedia content, referencing proper exercise form, nutrition tips, etc.
   - Fit Bot references tutorials in Q&A if needed.

7. **Fit Bot**  
   - AI-powered assistant that provides concise, friendly advice on workouts and nutrition.
   - System prompt instructs Fit Bot to keep responses short, efficient, and supportive.

## Installation & Setup

1. **Clone or Download** this repository.

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
