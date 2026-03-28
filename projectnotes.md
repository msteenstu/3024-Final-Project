### Notes for Now
use sqlachlemy orm BUT only query database with text. Discuss orm misuse, unparameterized queries
and general recommendations sql alchemy has. Mention decision for text could be greater flexibility over
queries, general orm learning curve etc?


Create normal read me, threat model/poc, and general project notes md


only orders can lack login required decorator


app uses sql alchemy to create the schema and relationships with
the models file quickly, integrates the application with the db
easily as well. Demonstrate ORM misuse with one select-style query
using textual execution.

no password policy enforced


query for genre section : ' UNION SELECT NULL, NULL, NULL, id, email, name, password FROM users--



Raw SQL test run
from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, NoResultFound
import hashlib
from app import app, csrf, db
from app.models import *

#From docs
@app.before_request
def validate_csrf_manually():
    if request.endpoint in ['login', 'signup', 'signout'] \
        and request.method == 'POST':
            csrf.protect()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

#Uses safe parameter binding
@app.route('/user/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        form_username = request.form.get('id')
        form_email = request.form.get('email')
        form_name = request.form.get('name')
        form_password = request.form.get('password')

        if not form_username or not form_email \
              or not form_name or not form_password:
            flash('Please fill out the signup form completely')
            return render_template('signup.html')

        try:
            create_user_query = text("""
                INSERT into users (id, email, name, password)
                VALUES (:id, :email, :name, :password)
            """)

            hashed_password = hashlib.md5(form_password.encode('utf-8')).digest()

            db.session.execute(create_user_query, {
                 "id": form_username,
                 "email": form_email,
                 "name": form_name,
                 "password": hashed_password
            })
            db.session.commit()

            flash('User created successfully!')
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists, signup with a different one.')
            return render_template('signup.html')
        except Exception:
            db.session.rollback()
            flash('Something went wrong when creating your account')
            return redirect(url_for('index'))

    return render_template('signup.html')

#t = text("SELECT * FROM users WHERE id=:user_id")
#result = connection.execute(t, {"user_id": 12})

@app.route('/user/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
            form_username = request.form.get('id')
            form_password = request.form.get('password')

            if not form_username or not form_password:
                flash('Please fill out the signup form completely')
                return render_template('login.html')
            
            try:
                retrieve_user_query = text("SELECT * FROM users WHERE id=:id")
                user_query_result = db.session.execute(retrieve_user_query, {"id": form_username})
                user = user_query_result.fetchone()

                if user and hashlib.md5(form_password.encode('uft-8')).digest() :
                    flash('Invalid credentials, try again.')
                    return render_template('login.html')


                login_user(form_username)
            except Exception:
                 pass


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
