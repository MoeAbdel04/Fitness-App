from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import User, NutritionLog
from ..utils import calculate_tdee

nutrition_bp = Blueprint('nutrition', __name__)


def _current_user():
    return User.query.get(int(get_jwt_identity()))


def _parse_date(value):
    return datetime.strptime(value, '%Y-%m-%d').date() if value else date.today()


@nutrition_bp.route('', methods=['GET'])
@jwt_required()
def list_logs():
    user = _current_user()
    day = _parse_date(request.args.get('date'))
    logs = NutritionLog.query.filter_by(user_id=user.id, date=day).order_by(NutritionLog.id.asc()).all()

    total_calories = sum(l.calories for l in logs)
    tdee = calculate_tdee(user)

    return jsonify({
        'date': day.strftime('%Y-%m-%d'),
        'logs': [l.to_dict() for l in logs],
        'total_calories': total_calories,
        'total_protein': sum(l.protein or 0 for l in logs),
        'total_carbs': sum(l.carbs or 0 for l in logs),
        'total_fat': sum(l.fat or 0 for l in logs),
        'tdee_target': tdee,
        'remaining_calories': round(tdee - total_calories),
    })


@nutrition_bp.route('', methods=['POST'])
@jwt_required()
def create_log():
    user = _current_user()
    data = request.get_json(force=True)
    required = ['food_name', 'calories']
    missing = [f for f in required if data.get(f) in (None, '')]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    log = NutritionLog(
        user_id=user.id,
        food_name=data['food_name'],
        calories=float(data['calories']),
        protein=float(data['protein']) if data.get('protein') not in (None, '') else None,
        carbs=float(data['carbs']) if data.get('carbs') not in (None, '') else None,
        fat=float(data['fat']) if data.get('fat') not in (None, '') else None,
        meal_type=data.get('meal_type', 'snack'),
        date=_parse_date(data.get('date')),
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Food logged!', 'log': log.to_dict()}), 201


@nutrition_bp.route('/<int:log_id>', methods=['DELETE'])
@jwt_required()
def delete_log(log_id):
    user = _current_user()
    log = NutritionLog.query.get_or_404(log_id)
    if log.user_id != user.id:
        return jsonify({'error': 'Unauthorized action.'}), 403
    db.session.delete(log)
    db.session.commit()
    return jsonify({'message': 'Log deleted.'})
