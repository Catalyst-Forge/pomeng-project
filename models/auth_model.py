from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    """User model for authentication and user management"""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False, index=True)
    fullname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(50), nullable=False, default='user')  # New role column

    def set_password(self, password):
        """Set the user's password using SHA-256 hashing"""
        try:
            self.password = generate_password_hash(password, method='sha256')
        except Exception as e:
            raise ValueError(f"Error setting password: {str(e)}")

    def check_password(self, password):
        """Verify the user's password"""
        try:
            return check_password_hash(self.password, password)
        except ValueError:
            # Handle the OpenSSL error gracefully
            return False
        except Exception:
            return False

    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    @classmethod
    def get_by_username(cls, username):
        """Get user by username"""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def email_exists(cls, email):
        """Check if email already exists"""
        return cls.query.filter_by(email=email).first() is not None

    @classmethod
    def username_exists(cls, username):
        """Check if username already exists"""
        return cls.query.filter_by(username=username).first() is not None

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'fullname': self.fullname,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'role': self.role  # Include role in the dictionary
        }

    def __repr__(self):
        return f'<User {self.username}>'