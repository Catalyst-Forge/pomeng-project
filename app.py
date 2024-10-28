from flask import Flask, jsonify
from models.auth_model import User
from extensions import db, migrate, login_manager
from viewController.view_auth import auth_bp
from viewController.view_Lstm import crud_bp
from viewController.view_fineTuning import fineTuning
from route import route_bp  # Import blueprint

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth.login'


    app.register_blueprint(auth_bp)
    app.register_blueprint(crud_bp)
    app.register_blueprint(fineTuning)
    app.register_blueprint(route_bp)

    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
