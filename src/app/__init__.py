from flask import Flask

app = Flask('BookWorm Web App')
app.secret_key = 'books are great!'

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book_worm.db'
db = SQLAlchemy(app)

from app import models
with app.app_context():
    db.create_all()

from flask_login import LoginManager
loginManager = LoginManager()
loginManager.init_app(app)

from app.models import User
@loginManager.user_loader
def load_user(id):
    try:
        #Will throw an exception if a user is not returned.
        return db.session.query(User).filter(User.id == id).one()
    except Exception:
        #If the user is not found, do not throw an exception,
        #continue execution normally.
        return None

#This import must be placed here to avoid
#a circular import error.
from app import routes