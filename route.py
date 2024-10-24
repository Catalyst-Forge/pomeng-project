from flask import Blueprint, render_template, request, jsonify
from predict.process import preparation, botResponse
from flask_login import login_required


route_bp = Blueprint('route', __name__)

preparation()

@route_bp.route('/')
def index():
    return render_template('index.html')

@route_bp.route('/chat-bot')
def chat():
    return render_template('chatbot.html')


@route_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

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