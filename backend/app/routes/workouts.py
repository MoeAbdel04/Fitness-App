from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import User, WorkoutLog
from ..utils import calculate_bmi, calculate_tdee, lbs_to_kg, kg_to_lbs

workouts_bp = Blueprint('workouts', __name__)


def _current_user():
    return User.query.get(int(get_jwt_identity()))


@workouts_bp.route('', methods=['GET'])
@jwt_required()
def list_workouts():
    user = _current_user()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = WorkoutLog.query.filter_by(user_id=user.id) \
        .order_by(WorkoutLog.date.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'workouts': [w.to_dict() for w in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
    })


@workouts_bp.route('', methods=['POST'])
@jwt_required()
def log_workout():
    user = _current_user()
    data = request.get_json(force=True)
    required = ['workout_type', 'exercise', 'sets', 'reps']
    missing = [f for f in required if data.get(f) in (None, '')]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    workout = WorkoutLog(
        user_id=user.id,
        workout_type=data['workout_type'],
        exercise=data['exercise'],
        sets=int(data['sets']),
        reps=int(data['reps']),
        weight=lbs_to_kg(data.get('weight')),
    )
    db.session.add(workout)
    db.session.commit()
    return jsonify({'message': 'Workout logged successfully!', 'workout': workout.to_dict()}), 201


@workouts_bp.route('/<int:workout_id>', methods=['PUT'])
@jwt_required()
def edit_workout(workout_id):
    user = _current_user()
    workout = WorkoutLog.query.get_or_404(workout_id)
    if workout.user_id != user.id:
        return jsonify({'error': 'Unauthorized action.'}), 403

    data = request.get_json(force=True)
    workout.workout_type = data.get('workout_type', workout.workout_type)
    workout.exercise = data.get('exercise', workout.exercise)
    workout.sets = int(data.get('sets', workout.sets))
    workout.reps = int(data.get('reps', workout.reps))
    if 'weight' in data:
        workout.weight = lbs_to_kg(data.get('weight'))
    db.session.commit()
    return jsonify({'message': 'Workout updated successfully!', 'workout': workout.to_dict()})


@workouts_bp.route('/<int:workout_id>', methods=['DELETE'])
@jwt_required()
def delete_workout(workout_id):
    user = _current_user()
    workout = WorkoutLog.query.get_or_404(workout_id)
    if workout.user_id != user.id:
        return jsonify({'error': 'Unauthorized action.'}), 403
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout deleted successfully!'})


@workouts_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user = _current_user()
    height_cm = user.height * 100.0
    bmi = calculate_bmi(user.weight, user.height)
    tdee = calculate_tdee(user)
    calorie_plans = {
        'maintenance': tdee,
        'light_deficit': tdee - 250,
        'medium_deficit': tdee - 500,
        'extreme_deficit': tdee - 750,
    }

    all_workouts = WorkoutLog.query.filter_by(user_id=user.id).order_by(WorkoutLog.date.asc()).all()
    weighted = [w for w in all_workouts if w.weight]
    chart_series = [{
        'date': w.date.strftime('%Y-%m-%d'),
        'weight_lbs': kg_to_lbs(w.weight),
        'bmi': calculate_bmi(w.weight, user.height),
    } for w in weighted]

    volume_series = [{
        'date': w.date.strftime('%Y-%m-%d'),
        'volume': round((w.weight or 0) * w.sets * w.reps, 1),
        'exercise': w.exercise,
    } for w in all_workouts]

    recent = WorkoutLog.query.filter_by(user_id=user.id).order_by(WorkoutLog.date.desc()).limit(5).all()

    recommendations = {
        'cardio': 'Try a 30-minute run or cycling session.',
        'weight_training': 'Consider a full-body strength training routine.',
        'strength_training': 'Focus on compound lifts like squats, deadlifts, and bench press.',
    }
    recommended_workout = recommendations.get(
        (user.workout_preference or '').lower(),
        'Keep up the great work with your fitness routine!'
    )

    return jsonify({
        'bmi': bmi,
        'tdee': tdee,
        'calorie_plans': calorie_plans,
        'weight_lbs': kg_to_lbs(user.weight),
        'chart_series': chart_series,
        'volume_series': volume_series,
        'recent_workouts': [w.to_dict() for w in recent],
        'total_workouts': len(all_workouts),
        'recommended_workout': recommended_workout,
    })
