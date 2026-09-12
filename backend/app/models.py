from datetime import datetime, date
from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    height = db.Column(db.Float, nullable=False)  # meters
    weight = db.Column(db.Float, nullable=False)  # kg
    activity_level = db.Column(db.String(20), nullable=False)
    workout_preference = db.Column(db.String(20), nullable=True)
    goal = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    workouts = db.relationship('WorkoutLog', backref='user', lazy=True,
                                cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy=True,
                             cascade='all, delete-orphan')
    nutrition_logs = db.relationship('NutritionLog', backref='user', lazy=True,
                                      cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'activity_level': self.activity_level,
            'workout_preference': self.workout_preference,
            'goal': self.goal,
        }


class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_type = db.Column(db.String(50), nullable=False)
    exercise = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=True)  # kg
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'workout_type': self.workout_type,
            'exercise': self.exercise,
            'sets': self.sets,
            'reps': self.reps,
            'weight': self.weight,
            'weight_lbs': round(self.weight / 0.453592, 1) if self.weight else None,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
        }


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_type = db.Column(db.String(30), nullable=False)  # weight, strength, workout_count, custom
    title = db.Column(db.String(150), nullable=False)
    target_value = db.Column(db.Float, nullable=False)
    start_value = db.Column(db.Float, nullable=True)
    current_value = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(20), nullable=True)
    target_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def progress_percent(self):
        if self.start_value is None or self.current_value is None:
            return 0
        span = self.target_value - self.start_value
        if span == 0:
            return 100
        pct = (self.current_value - self.start_value) / span * 100
        return max(0, min(100, round(pct)))

    def to_dict(self):
        return {
            'id': self.id,
            'goal_type': self.goal_type,
            'title': self.title,
            'target_value': self.target_value,
            'start_value': self.start_value,
            'current_value': self.current_value,
            'unit': self.unit,
            'target_date': self.target_date.strftime('%Y-%m-%d') if self.target_date else None,
            'status': self.status,
            'progress_percent': self.progress_percent(),
        }


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Cardio, Weight Training, Strength Training
    muscle_group = db.Column(db.String(50), nullable=False)
    equipment = db.Column(db.String(50), nullable=True)
    difficulty = db.Column(db.String(20), nullable=True)  # Beginner, Intermediate, Advanced
    instructions = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'muscle_group': self.muscle_group,
            'equipment': self.equipment,
            'difficulty': self.difficulty,
            'instructions': self.instructions,
        }


class NutritionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_name = db.Column(db.String(150), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=True)
    carbs = db.Column(db.Float, nullable=True)
    fat = db.Column(db.Float, nullable=True)
    meal_type = db.Column(db.String(20), nullable=True)  # breakfast, lunch, dinner, snack
    date = db.Column(db.Date, default=date.today)

    def to_dict(self):
        return {
            'id': self.id,
            'food_name': self.food_name,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'meal_type': self.meal_type,
            'date': self.date.strftime('%Y-%m-%d'),
        }
