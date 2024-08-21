from flask import Blueprint, render_template

route_bp = Blueprint('routes', __name__)

@route_bp.route('/')
def index():
  return render_template('index.html')

@route_bp.route('/chat-bot')
def chat():
  return render_template('chatbot.html')