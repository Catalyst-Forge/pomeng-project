from flask import Flask
from extensions import db, migrate, login_manager
from auth import auth_bp
from dashboard import dashboard_bp
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
        from models import User
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth.login'


    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(route_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
