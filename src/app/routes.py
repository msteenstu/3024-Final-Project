from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import traceback
import hashlib
from app import app, csrf, db
from app.models import Book, User
from app.user_operations import*
from app.shop_operations import*

#From docs
@app.before_request
def validate_csrf_manually():
    if request.endpoint in ['login', 'signup', 'logout'] \
        and request.method == 'POST':
            csrf.protect()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/user/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        form_email = request.form.get('email')
        form_name = request.form.get('name')
        form_password = request.form.get('password')
        form_password_confirm = request.form.get('password_confirm')

        if not form_email or not form_name  \
              or not form_password or not form_password_confirm:
            flash('Please fill out the signup form completely')
            return render_template('signup.html')
        
        if form_password != form_password_confirm:
            flash('Passwords do not match')
            return render_template('signup.html')
        
        check_password_against_policy, message = password_policy_enforcement(form_password)
        if not check_password_against_policy:
            flash(message)
            return render_template('signup.html')

        try:
            register_account(
                email = form_email,
                name = form_name,
                password = form_password
            )
            flash('User created successfully!')
            return redirect(url_for('index'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists, signup with a different one.')
            return render_template('signup.html')
        
        except Exception:
            traceback.print_exc()
            db.session.rollback()
            flash('Something went wrong when creating your account')
            return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/user/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
            form_email = request.form.get('email')
            form_password = request.form.get('password')

            if not form_email or not form_password:
                flash('Please fill out the signup form completely.')
                return render_template('login.html')
            
            try:
                user = query_user(form_email)
                _, user_password_hash = hash_user_password(form_password)
                if user \
                and user_password_hash  == user.password:
                    login_user(user)
                    return render_template('book_listings.html')
                else:
                    flash('Invalid credentials, try again.')
                    return render_template('login.html')
                
            except Exception:
                traceback.print_exc()
                flash('An error occurred during login, try again,')
                return redirect (url_for('index'))

    return render_template('login.html')

@app.route('/user/signout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('Successfully logged out, see you next time!')
    return redirect(url_for('index'))
