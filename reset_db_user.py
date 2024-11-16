from flask import Flask
from extensions import db
from models.auth_model import User  # Assuming the User model is in models.py
import logging

def reset_database(app):
    """
    Reset the database by dropping all tables and recreating them.
    Optionally add initial data if needed.
    """
    try:
        # Drop all tables
        with app.app_context():
            logging.info("Dropping all database tables...")
            db.drop_all()
            
            # Recreate all tables
            logging.info("Creating all database tables...")
            db.create_all()
            
            # Optionally add initial admin user
            admin_user = User(
                username="admin",
                fullname="Administrator",
                email="admin@example.com",
                is_active=True
            )
            admin_user.set_password("admin123")  # Remember to change this in production
            
            db.session.add(admin_user)
            db.session.commit()
            
            logging.info("Database reset completed successfully!")
            return True
            
    except Exception as e:
        logging.error(f"Error resetting database: {str(e)}")
        return False

if __name__ == "__main__":
    # Create Flask app instance
    app = Flask(__name__)
    
    # Configure database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database with app
    db.init_app(app)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Reset database
    success = reset_database(app)
    
    if success:
        print("Database reset completed successfully!")
    else:
        print("Database reset failed. Check the logs for details.")