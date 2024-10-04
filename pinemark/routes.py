import os
from flask import current_app as app, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Bookmark, Tag, BookmarkTag, User
from flask_login import login_user, logout_user, login_required, current_user
from .scrape import capture_page_info

from . import db


@app.route('/', methods=['GET', 'POST'])
@login_required
def home():

    user_name = current_user.username
    bookmarks = Bookmark.query.all()  # Fetch all bookmarks
    if request.method == 'POST':
        url = request.form['url']
        # Capture the page info
        title, description, favicon_url, screenshot_path = capture_page_info(url)

        # Create a new bookmark entry
        new_bookmark = Bookmark(
            title=title,
            url=url,
            description=description,
            favicon=favicon_url,
            screenshot_path=screenshot_path,
            rating=1,  # You can set a default rating or customize as needed
            is_favorite=False,
            access_count=0,
        )

        # Add the new bookmark to the database
        db.session.add(new_bookmark)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('index.html', bookmarks=bookmarks, user_name=user_name)

@app.route('/delete/<int:bookmark_id>', methods=['POST'])
@login_required
def delete_bookmark(bookmark_id):
    bookmark = Bookmark.query.get(bookmark_id)
    if bookmark:
        if bookmark.screenshot_path:
            try:
                # Construct the full path to the screenshot
                file_path = os.path.join(app.root_path, 'static', 'screenshots', bookmark.screenshot_path)
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Delete the file
            except Exception as e:
                flash(f'Error deleting file: {e}', 'error')

        db.session.delete(bookmark)
        db.session.commit()
        flash('Bookmark deleted successfully!', 'success')
    else:
        flash('Bookmark not found.', 'error')
    return redirect(url_for('home'))

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
