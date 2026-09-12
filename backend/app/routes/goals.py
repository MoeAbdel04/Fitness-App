from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import User, Goal

goals_bp = Blueprint('goals', __name__)


def _current_user():
    return User.query.get(int(get_jwt_identity()))


@goals_bp.route('', methods=['GET'])
@jwt_required()
def list_goals():
    user = _current_user()
    goals = Goal.query.filter_by(user_id=user.id).order_by(Goal.created_at.desc()).all()
    return jsonify({'goals': [g.to_dict() for g in goals]})


@goals_bp.route('', methods=['POST'])
@jwt_required()
def create_goal():
    user = _current_user()
    data = request.get_json(force=True)
    required = ['goal_type', 'title', 'target_value']
    missing = [f for f in required if data.get(f) in (None, '')]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    target_date = None
    if data.get('target_date'):
        target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()

    goal = Goal(
        user_id=user.id,
        goal_type=data['goal_type'],
        title=data['title'],
        target_value=float(data['target_value']),
        start_value=float(data['start_value']) if data.get('start_value') not in (None, '') else None,
        current_value=float(data['current_value']) if data.get('current_value') not in (None, '') else data.get('start_value'),
        unit=data.get('unit'),
        target_date=target_date,
    )
    db.session.add(goal)
    db.session.commit()
    return jsonify({'message': 'Goal created!', 'goal': goal.to_dict()}), 201


@goals_bp.route('/<int:goal_id>', methods=['PUT'])
@jwt_required()
def update_goal(goal_id):
    user = _current_user()
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != user.id:
        return jsonify({'error': 'Unauthorized action.'}), 403

    data = request.get_json(force=True)
    if 'current_value' in data and data['current_value'] not in (None, ''):
        goal.current_value = float(data['current_value'])
    if 'status' in data:
        goal.status = data['status']
    if 'title' in data:
        goal.title = data['title']
    if 'target_value' in data:
        goal.target_value = float(data['target_value'])
    if 'target_date' in data and data['target_date']:
        goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()

    if goal.current_value is not None and goal.status != 'completed':
        reached = (goal.current_value >= goal.target_value) if goal.target_value >= (goal.start_value or 0) \
            else (goal.current_value <= goal.target_value)
        if reached:
            goal.status = 'completed'

    db.session.commit()
    return jsonify({'message': 'Goal updated!', 'goal': goal.to_dict()})


@goals_bp.route('/<int:goal_id>', methods=['DELETE'])
@jwt_required()
def delete_goal(goal_id):
    user = _current_user()
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != user.id:
        return jsonify({'error': 'Unauthorized action.'}), 403
    db.session.delete(goal)
    db.session.commit()
    return jsonify({'message': 'Goal deleted.'})
