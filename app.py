from flask import Flask

# to create authentication
from functools import wraps
from flask import render_template, request, redirect, url_for, session 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import login_user, current_user
from birdwise.models import User

from birdwise.extensions import db, login_manager, bcrypt

app = Flask(__name__, template_folder='birdwise/templates', static_folder='birdwise\static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///birdwise.db'
app.config['SECRET_KEY'] = '8b435b3f121b6273e153d976'
migrate = Migrate(app, db)
# Initialize db, bcrypt, and login manager
db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from birdwise import routes

with app.app_context():
    pass