from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy import text
from app import app, db
from app.models import *


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/user/signup')
def signup():
    return render_template('signup.html')

@app.route('/user/login')
def login():
    return render_template('login.html')

@app.route('/user/logout')
def logout():
    logout_user()
    flash('Logout successful, see you next time!')
    return redirect(url_for('index'))

#SQL Alchemy docs example
#t = text("SELECT * FROM users")
#result = connection.execute(t)

def list_all_books():
    books_query = text("SELECT * FROM books")
    return db.session.execute(books_query).all()
