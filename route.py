from flask import Blueprint, render_template, request, jsonify
from process import preparation, botResponse
from crud import get_all_intents, add_intent, update_intent, delete_intent
from flask_login import login_required


route_bp = Blueprint('route', __name__)

preparation()

@route_bp.route('/')
def index():
    return render_template('index.html')

@route_bp.route('/chat-bot')
def chat():
    return render_template('chatbot.html')

@route_bp.route("/predict", methods=["GET", "POST"])
def predict():
    text = request.get_json().get("message")
    response = botResponse(text)
    message = {"answer": response}
    return jsonify(message)

@route_bp.route('/crud-test')
@login_required  # Menambahkan dekorator login_required di sini
def crud_test():
    return render_template('crud.html')

@route_bp.route('/intents', methods=['GET'])
@login_required  # Menambahkan dekorator login_required di sini
def get_intents():
    intents = get_all_intents()
    return jsonify(intents)

@route_bp.route('/intents', methods=['POST'])
@login_required  # Menambahkan dekorator login_required di sini
def create_intent():
    data = request.get_json()
    tag = data.get('tag')
    patterns = data.get('patterns')
    responses = data.get('responses')
    new_intent = add_intent(tag, patterns, responses)
    return jsonify(new_intent)

@route_bp.route('/intents/<tag>', methods=['PUT'])
@login_required  # Menambahkan dekorator login_required di sini
def update_existing_intent(tag):
    data = request.get_json()
    new_patterns = data.get('patterns')
    new_responses = data.get('responses')
    updated_intent = update_intent(tag, new_patterns, new_responses)
    if updated_intent:
        return jsonify(updated_intent)
    else:
        return jsonify({'error': 'Intent not found'}), 404

@route_bp.route('/intents/<tag>', methods=['DELETE'])
@login_required  # Menambahkan dekorator login_required di sini
def remove_intent(tag):
    deleted_intent = delete_intent(tag)
    if deleted_intent:
        return jsonify(deleted_intent)
    else:
        return jsonify({'error': 'Intent not found'}), 404