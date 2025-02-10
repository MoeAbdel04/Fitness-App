from flask import Blueprint, render_template
from flask_login import login_required

workout_bp = Blueprint('workout', __name__)

@workout_bp.route('/workout_selection')
@login_required
def workout_selection():
    return render_template('workout_selection.html')

@workout_bp.route('/cardio_training')
@login_required
def cardio_training():
    workout_details = {
        "title": "Cardio Training",
        "description": "Improve your cardiovascular health with running, cycling, or swimming.",
        "example_workout": [
            "5-minute warm-up",
            "20 minutes of running or cycling at a steady pace",
            "5-minute cool-down"
        ]
    }
    return render_template('workout_details.html', workout=workout_details)

@workout_bp.route('/weight_training')
@login_required
def weight_training():
    workout_details = {
        "title": "Weight Training",
        "description": "Build muscle and strength with a focus on lifting weights.",
        "example_workout": [
            "3 sets of 12 squats",
            "3 sets of 12 bench presses",
            "3 sets of 12 deadlifts"
        ]
    }
    return render_template('workout_details.html', workout=workout_details)

@workout_bp.route('/strength_training')
@login_required
def strength_training():
    workout_details = {
        "title": "Strength Training",
        "description": "Enhance strength with high-intensity weightlifting routines.",
        "example_workout": [
            "5 sets of 5 squats",
            "5 sets of 5 bench presses",
            "5 sets of 5 overhead presses"
        ]
    }
    return render_template('workout_details.html', workout=workout_details)
