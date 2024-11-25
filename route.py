from flask import Blueprint, render_template, request, jsonify
from predict.process import ResponseGenerator
import asyncio
from flask_login import login_required

response_generator = ResponseGenerator()
route_bp = Blueprint('route', __name__, template_folder='templates')


@route_bp.route('/')
def index():
    return render_template('index.html')

@route_bp.route('/chat-bot')
def chat():
    return render_template('chatbot.html')


@route_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('pages/main-dashboard.html')

@route_bp.route("/predict", methods=["GET", "POST"])
def predict():
    try:
        # Get the message from request
        text = request.get_json().get("message")
        
        if not text:
            return jsonify({
                "error": "No message provided",
                "answer": "Mohon masukkan pesan Anda."
            }), 400

        # Get response using the ResponseGenerator
        response = response_generator.get_response(text)
        
        # Return the response
        return jsonify({
            "answer": response,
            "status": "success"
        })
        
    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f"Error in prediction: {str(e)}")
        
        # Return error response
        return jsonify({
            "error": "Internal server error",
            "answer": "Maaf, terjadi kesalahan dalam memproses permintaan Anda."
        }), 500