from app import db, login_manager, app
from app import bcrypt
from flask_login import UserMixin
from datetime import datetime

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'user'  # Explicitly set the table name if needed
    
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    actual_name = db.Column(db.String(length=60), nullable=False)
    email_id = db.Column(db.String(length=60), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    user_bio = db.Column(db.String(length=150), nullable=False)
    profile_pic = db.Column(db.String(32), default='default.jpeg')
    badges = db.Column(db.String(32))
    uploads = db.relationship("Uploads", back_populates="user")

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
# Uploads model
class Uploads(db.Model):
    __tablename__ = 'uploads'  # Explicitly set the table name if needed

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key linking to 'user' table
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to the User table
    user = db.relationship("User", back_populates="uploads")

# class Leaderboard(db.Model):
# Uncomment and define this model if needed.

# Create all tables
with app.app_context():
    db.create_all()
