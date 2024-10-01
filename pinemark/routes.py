from flask import current_app as app, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Bookmark, Tag, BookmarkTag, User
from flask_login import login_user, logout_user, login_required, current_user

from . import db


@app.route('/')
@login_required
def home():
    user_name = current_user.username
    bookmarks = Bookmark.query.all()  # Fetch all bookmarks
    return render_template('index.html', bookmarks=bookmarks, user_name=user_name)

@app.route('/login')
def login():
    if (User.query.first() == None):
        return redirect(url_for('signup'))
    else:
        return render_template('auth/login.html')


@app.route('/login', methods=['POST'])
def login_post():
    
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Error: Invalid username or password')
        return redirect(url_for('login'))
         # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('home'))

@app.route('/signup')
def signup():
    return render_template('auth/signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():

    username = request.form.get('username')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if (password != password2):
        flash('Error: Passwords do not match')
        return redirect(url_for('signup')) 

    # if this returns a user, then the email already exists in database
    user = User.query.filter_by(username=username).first()

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
