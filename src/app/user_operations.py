from app import app, db
from app.models import User
from sqlalchemy.exc import IntegrityError
import hashlib
import re


def register_account(email, name, password):
    
    clean_email = email.strip().lower()

    check_if_user_exists = query_user(clean_email)
    if(check_if_user_exists is not None):
        raise IntegrityError
    
    password_salt, hashed_password = hash_user_password(password)

    new_account = User(
        email = clean_email,
        name = name,
        salt = password_salt,
        password = hashed_password
    )

    db.session.add(new_account)
    db.session.commit()

def hash_user_password(password):
    hash_salt = 'books'
    hashed_password = hashlib.md5(
        hash_salt.encode('utf-8') + password.encode('utf-8')
    ).digest()
    return hash_salt, hashed_password

def password_policy_enforcement(password):
    if len(password) < 12:
        return False, "Password must be at least 12 characters long."
    
    if not re.search(r"[A-Z]", password):
        return False, "Your password did not have an uppercase letter."
    
    if not re.search(r"[a-z]", password):
        return False, "Your password did not have an lowercase letter."
    
    if not re.search(r"[0-9]", password):
        return False, "Your password did not have a number."
    
    #Spaces do not count as a special character.
    if not re.search(r"[^a-zA-Z0-9\s]", password):
        return False, "Your password did not have a unique character."

    return True, ""

def query_user(email):
    return User.query.filter_by(email = email).first()

def delete_account(user_id):
    user = User.query.filter_by(id = user_id).first()

    if not user:
        raise IntegrityError
    
    db.session.delete(user)
    db.session.commit()

