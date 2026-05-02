"""
Author: Mckenna Steenbock
Description: This file contains
the necessary settings and imports
to run the Book Worm web application.
"""

from flask import Flask
import os

app = Flask('Book Worm Web App')
app.secret_key = os.environ.get("SECRET_KEY")

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book_worm.db'
db = SQLAlchemy(app)

# Import the object models for the database schema
# and populate the database with books for sale.
from app import models
with app.app_context():
    db.create_all()

    # This import is placed here to avoid a circular import.
    from app.database_populate import populate_book_inventory
    populate_book_inventory()

# Cross-Site Request Forgery (CSRF) Support Configuration
# The SAMESITE setting allows session cookies to be sent with cross-site requests 
# from different origins over HTTPS.
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'

# Insecure Cross-Site Request Forgery (CSRF) Related Configuration
# Automatic CSRF protection is disabled for the application, enabling
# forged requests on routes without manual protections applied.
# Custom CSRF protection implementation adapted from Flask-WTF's (n.d.) documentation.
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
app.config["WTF_CSRF_CHECK_DEFAULT"] = False
csrf.init_app(app)

from flask_login import LoginManager
loginManager = LoginManager()
loginManager.init_app(app)

# An exception will be thrown if a user is not returned,
# but execution should not stop if this occurs.
from app.models import User
@loginManager.user_loader
def load_user(id):
    try:
        return db.session.query(User).filter(User.id == id).one()
    except Exception:
        return None

# This import must be placed here to avoid
# a circular import error.
from app import routes