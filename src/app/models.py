from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
