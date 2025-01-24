from app import app, db
from birdwise.models import User
from flask_login import login_user, logout_user, login_required, current_user

from birdwise.forms import RegisterForm, LoginForm

# to create authentication
from functools import wraps
from flask import render_template, request, redirect, url_for, session, flash

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import url_for 
from birdwise.models import User
from sendmail import Sendmail

mail = Mail(app)
# created an instance of the Mail
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

#profile pic route 
import os
from werkzeug.utils import secure_filename

def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            #flash('Please login to continue')
            return redirect(url_for('login'))
    return inner

@app.route('/')
def home_page():
    return render_template('home.html')
# @auth_required
# def somefunc():
#     return 0

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('new_home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/home')
@login_required
def new_home_page():
    return render_template('newhome.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(actual_name=form.actual_name.data,
                              username=form.username.data,
                              email_id=form.email_id.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('new_home_page'))
    if form.errors: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    if form.errors:
        print("Form errors:", form.errors)

    return render_template('register.html', form=form)

@app.route('/profile')
def profile_page():
    return render_template('profile2.html')

@app.route('/my-courses')
def my_courses_page():
    return render_template('courses.html')

@app.route('/my-uploads')
def my_uploads_page():
    return render_template('uploads.html')

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgotpassword.html')

@app.route('/forgot_password', methods=['POST'])
def forgot_password_post():
    email = request.form.get('email')

    # Check if the email exists in the database
    user = User.query.filter_by(email=email).first()

    if user:
        send_reset_email(user)
        #flash('A reset link has been sent to your email.', 'success')

    else:
        #flash('Email does not exist.', 'danger')
        return redirect(url_for('forgot_password'))
    
    return redirect(url_for('login'))

@app.route('/my-quizzes')
def quiz_page():
    return render_template('quiz.html')

@app.route('/reset_password')
def reset_password():
    return render_template('resetpassword.html') 

@app.route('/reset_password/<token>', methods=['POST'])
def reset_password_post(token):
    #Validate token post method after html page created
    user = verify_reset_token(token)
    if not user:
        #flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('forgot_password'))
    new_password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not new_password or new_password != confirm_password:
        #flash('Passwords do not match or are invalid.', 'danger')
        return render_template('resetpassword.html', token=token)
    
    user.password = new_password
    db.session.commit()

    #flash('Your password has been updated. You can now log in.', 'success')
    return redirect(url_for('login'))

# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
@app.route('/upload_profile_pic', methods=['POST'])
@auth_required
def upload_profile_pic():
    if 'profile_pic' not in request.files:
        #flash('No file part')
        return redirect(url_for('profile'))
    
    file = request.files['profile_pic']
    
    if file.filename == '':
        #flash('No selected file')
        return redirect(url_for('profile'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        user_id = session['user_id']

        new_filename = f"user_{user_id}.{filename.rsplit('.', 1)[1].lower()}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

        # UPLOAD_FOLDER = 'static/profile_pic'
        # create a folder called static and inside create another folder for profile_pic

        user = User.query.get(user_id)
        user.profile_pic = new_filename
        db.session.commit()
        
        #flash('Profile picture updated successfully')
        return redirect(url_for('profile'))
    
    #flash('Invalid file format')
    return redirect(url_for('home'))

def generate_reset_token(user):
    return serializer.dumps(user.email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return User.query.filter_by(email=email).first()

def send_reset_email(user):
    token = generate_reset_token(user)
    reset_url = url_for('reset_password', token=token, _external=True)
    subject = " Reset your password"
    body = f'''
    To reset your password, click the following link:
    {reset_url}

    If you did not make this request, simply ignore this email.
    '''
    Sendmail(user.email, subject, body)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS'] 