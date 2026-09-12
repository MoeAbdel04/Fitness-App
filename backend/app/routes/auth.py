from datetime import timedelta
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from ..extensions import db
from ..models import User
from ..utils import lbs_to_kg

auth_bp = Blueprint('auth', __name__)

RESET_TOKEN_EXPIRY = timedelta(minutes=15)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    required = ['username', 'email', 'password', 'age', 'gender', 'height', 'weight_lbs', 'activity_level']
    missing = [f for f in required if not data.get(f) and data.get(f) != 0]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'An account with that email already exists.'}), 409
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'That username is taken.'}), 409

    user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password'], method='pbkdf2:sha256'),
        age=int(data['age']),
        gender=data['gender'],
        height=float(data['height']),  # meters
        weight=lbs_to_kg(data['weight_lbs']),
        activity_level=data['activity_level'],
        workout_preference=data.get('workout_preference'),
        goal=data.get('goal'),
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({'message': 'Account created successfully!', 'token': token, 'user': user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials, please try again.'}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({'message': 'Login successful!', 'token': token, 'user': user.to_dict()})


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json(force=True)
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'No account found with that email address.'}), 404
    reset_token = create_access_token(identity=str(user.id), expires_delta=RESET_TOKEN_EXPIRY,
                                       additional_claims={'purpose': 'password_reset'})
    return jsonify({'message': 'Email verified. You can now reset your password on-site.',
                     'reset_token': reset_token})


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json(force=True)
    reset_token = data.get('reset_token')
    new_password = data.get('password')
    if not reset_token or not new_password:
        return jsonify({'error': 'Reset token and new password are required.'}), 400

    from flask_jwt_extended import decode_token
    try:
        decoded = decode_token(reset_token)
    except Exception:
        return jsonify({'error': 'Invalid or expired reset token. Please request a new one.'}), 400

    if decoded.get('purpose') != 'password_reset':
        return jsonify({'error': 'Invalid reset token.'}), 400

    user = User.query.get(int(decoded['sub']))
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.commit()
    return jsonify({'message': 'Your password has been updated. Please log in.'})


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    return jsonify({'user': user.to_dict()})
