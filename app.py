from flask import Flask

# to create authentication
from functools import wraps
from flask import render_template, request, redirect, url_for, session 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///birdwise.db'
app.config['SECRET_KEY'] = '8b435b3f121b6273e153d976'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

with app.app_context():
    pass