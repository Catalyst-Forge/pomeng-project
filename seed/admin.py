from app import create_app, db
from models.auth_model import User

app = create_app()

with app.app_context():
    # Cek apakah admin sudah ada
    existing_admin = User.query.filter_by(username='admin').first()
    
    if not existing_admin:
        # Buat admin baru jika belum ada
        admin = User(
            username='admin',
            fullname='Administrator',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin')
        
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully")
    else:
        print("Admin user already exists")