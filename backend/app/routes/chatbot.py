import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

chatbot_bp = Blueprint('chatbot', __name__)

SYSTEM_PROMPT = (
    "You are Fit Bot, an energetic, friendly, and concise AI fitness assistant. "
    "Provide short, efficient, and engaging advice on workouts, nutrition, and overall fitness. "
    "Keep your responses brief yet informative, and add a touch of personality and support. "
    "If the user's question is about exercise techniques or proper form, reference available tutorials briefly."
)


@chatbot_bp.route('', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json(force=True)
    user_message = data.get('message', '')
    if not user_message.strip():
        return jsonify({'error': 'Message cannot be empty.'}), 400

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return jsonify({
            'response': "Fit Bot is warming up! Ask your admin to set OPENAI_API_KEY to enable live AI responses. "
                        "In the meantime: stay consistent, prioritize protein, and progressively overload your lifts!"
        })

    try:
        import openai
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ]
        )
        ai_response = response.choices[0].message.content.strip()
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
