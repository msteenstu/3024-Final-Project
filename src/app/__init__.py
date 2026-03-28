from flask import Flask

app = Flask('BookWorm Web App')
app.secret_key = 'books are great!'

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book_worm.db'
db = SQLAlchemy(app)

from app import models
with app.app_context():
    db.create_all()

    #Avoid circular import.
    from app.database_populate import populate_book_inventory
    populate_book_inventory()

#flask docs and 3022 final
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
app.config["WTF_CSRF_CHECK_DEFAULT"] = False
csrf.init_app(app)

from flask_login import LoginManager
loginManager = LoginManager()
loginManager.init_app(app)

from app.models import User
@loginManager.user_loader
def load_user(id):
    try:
        #Will throw an exception if a user is not returned.
        #Used ORM functionality for simplicity to load the user
        #for flask login
        return db.session.query(User).filter(User.id == id).one()
    except Exception:
        #If the user is not found, do not throw an exception,
        #continue execution normally.
        return None

#This import must be placed here to avoid
#a circular import error.
from app import routes