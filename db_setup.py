from app import app, db
from models import User, BMIHistory, CalorieTracking

# Initialize database
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

    # Optional: Seed initial test users
    if not User.query.first():
        test_user = User(username="testuser", email="test@example.com",
                         password="$pbkdf2-sha256$29000$abcdef...hashedpassword")
        db.session.add(test_user)
        db.session.commit()
        print("Test user created!")
    
    print("Database setup complete!")
