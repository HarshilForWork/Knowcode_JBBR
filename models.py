from app import db, login_manager
from app import bcrypt
from app import app
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    actual_name = db.Column(db.String(length=60), nullable=False, unique=False)
    email_id = db.Column(db.String(length=60), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    user_bio = db.Column(db.String(length=150), nullable=False)
    profile_pic = db.Column(db.String(32), default = 'default.jpeg')
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
    
class Uploads(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key linking to Users table
    file_name = db.Column(db.String(255), nullable=False)  # File name
    file_path = db.Column(db.String(255), nullable=False)  # File storage path
    file_type = db.Column(db.String(50), nullable=False)   # File type (e.g., 'photo', 'video')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of upload

    # Relationship to the Users table
    user = db.relationship("Users", back_populates="uploads")

# class Leaderboard(db.Model):

with app.app_context():
   db.create_all()