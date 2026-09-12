import json
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import User
from ..utils import lbs_to_kg, kg_to_lbs, meters_to_feet_inches, feet_inches_to_meters

profile_bp = Blueprint('profile', __name__)


def _current_user():
    return User.query.get(int(get_jwt_identity()))


@profile_bp.route('', methods=['GET'])
@jwt_required()
def get_profile():
    user = _current_user()
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    feet, inches = meters_to_feet_inches(user.height)
    data = user.to_dict()
    data.update({
        'weight_lbs': kg_to_lbs(user.weight),
        'height_feet': feet,
        'height_inches': inches,
    })
    return jsonify({'user': data})


@profile_bp.route('', methods=['PUT'])
@jwt_required()
def update_profile():
    user = _current_user()
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    data = request.get_json(force=True)

    if 'feet' in data and 'inches' in data:
        user.height = feet_inches_to_meters(data['feet'], data['inches'])
    if 'weight_lbs' in data and data['weight_lbs'] not in (None, ''):
        user.weight = lbs_to_kg(data['weight_lbs'])

    for field in ['username', 'email', 'age', 'gender', 'activity_level', 'workout_preference', 'goal']:
        if field in data and data[field] not in (None, ''):
            setattr(user, field, int(data[field]) if field == 'age' else data[field])

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully!', 'user': user.to_dict()})


@profile_bp.route('/download', methods=['GET'])
@jwt_required()
def download_data():
    user = _current_user()
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    user_data = user.to_dict()
    user_data['workout_logs'] = [w.to_dict() for w in user.workouts]
    user_data['goals'] = [g.to_dict() for g in user.goals]
    user_data['nutrition_logs'] = [n.to_dict() for n in user.nutrition_logs]
    json_data = json.dumps(user_data, indent=4)
    return Response(json_data, mimetype='application/json',
                     headers={'Content-Disposition': 'attachment;filename=user_data.json'})
