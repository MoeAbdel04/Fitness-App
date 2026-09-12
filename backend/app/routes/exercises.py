from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from ..models import Exercise

exercises_bp = Blueprint('exercises', __name__)


@exercises_bp.route('', methods=['GET'])
@jwt_required()
def list_exercises():
    query = Exercise.query
    search = request.args.get('search')
    category = request.args.get('category')
    muscle_group = request.args.get('muscle_group')

    if search:
        query = query.filter(Exercise.name.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)
    if muscle_group:
        query = query.filter_by(muscle_group=muscle_group)

    exercises = query.order_by(Exercise.name.asc()).all()
    return jsonify({
        'exercises': [e.to_dict() for e in exercises],
        'categories': sorted({e.category for e in Exercise.query.all()}),
        'muscle_groups': sorted({e.muscle_group for e in Exercise.query.all()}),
    })
