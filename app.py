from flask import Flask, jsonify
from models.auth_model import User
from extensions import db, migrate, login_manager
from controller.view_auth import auth_bp
import nltk
from openai import OpenAI
from config import config
import os
from flask_wtf.csrf import CSRFProtect
from controller.view_Lstm import lstm
from utils.finetuning.metricsHandler import MetricsHandler
from controller.view_train_lstm import train_lstm
from controller.view_train_finetuning import train_finetuning
from controller.view_fineTuning import fineTuning
from dotenv import load_dotenv
from route import route_bp

def create_app():
    app = Flask(__name__,  static_url_path='/static')
    load_dotenv()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    client = OpenAI()
    metrics_handler = MetricsHandler()
    flask_debug = os.getenv('FLASK_DEBUG', '0')
    config_name = 'development' if flask_debug == '1' else 'production'
    app.config.from_object(config[config_name])
    OpenAI.api_key = os.getenv('OPENAI_API_KEY')



    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)

    login_manager.login_view = 'auth.login'


    app.register_blueprint(auth_bp)
    app.register_blueprint(lstm)
    app.register_blueprint(fineTuning)
    app.register_blueprint(train_finetuning)
    app.register_blueprint(route_bp)
    app.register_blueprint(train_lstm)
    

    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=2002)
