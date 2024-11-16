from flask import Flask, jsonify
from models.auth_model import User
from extensions import db, migrate, login_manager
from controller.view_auth import auth_bp
from controller.view_Lstm import lstm
from controller.view_train_lstm import lstm_train
from controller.view_fineTuning import fineTuning
from route import route_bp  # Import blueprint

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SECRET_KEY'] = 'Belekali'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth.login'


    app.register_blueprint(auth_bp)
    app.register_blueprint(lstm)
    app.register_blueprint(fineTuning)
    app.register_blueprint(route_bp)
    app.register_blueprint(lstm_train)
    

    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=2001)
