from flask import Flask, render_template, redirect, url_for, jsonify, flash, request, make_response, Blueprint
import datetime
from utils.finetuning.validator import FineTuningJobSchema, BASE_MODELS
from utils.finetuning.metricsHandler import MetricsHandler
from config import config
from models.lstm_model import Lstm
from models.fine_tuning import Finetuning
from openai import OpenAI
from utils.finetuning.utils import update_selected_model, validate_model_id, get_checkpoints, filter_chatbot_models
from predict.process import ResponseGenerator
from flask_login import login_required

response_generator = ResponseGenerator()
route_bp = Blueprint('route', __name__, template_folder='templates')
client = OpenAI()

@route_bp.route('/')
def index():
    return render_template('index.html')

@route_bp.route('/chat-bot')
def chat():
    return render_template('chatbot.html')


@route_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        response_model = client.models.list()
        models = []
        
        for model in response_model.data:
            model_data = {
                "id": model.id,
                "object": model.object,
                "created": datetime.datetime.fromtimestamp(model.created).strftime('%Y-%m-%d %H:%M:%S'),
                "owned_by": model.owned_by
            }
            models.append(model_data)
        
        # Count datasets
        total_finetuning_records = Finetuning.query.count()
        total_lstm_records = Lstm.query.count()
        
        # Filter model-related counts
        finetuning_jobs = [
            model for model in models 
            if model['id'].startswith('ft:')
        ]
        chatbot_models = filter_chatbot_models(models)
        
        return render_template('pages/main-dashboard.html', 
                            total_finetuning=len(finetuning_jobs),
                            total_openai_models=len(chatbot_models),
                            total_finetuning_records=total_finetuning_records,
                            total_lstm_records=total_lstm_records)
    except Exception as e:
        print(f"Error in dashboard: {str(e)}")
        return render_template('pages/main-dashboard.html', 
                            error=str(e), 
                            total_finetuning=0, 
                            total_openai_models=0,
                            total_finetuning_records=0,
                            total_lstm_records=0)

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