"""
Author: Mckenna
"""

from flask_login import UserMixin
from app import db

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    author = db.Column(db.String(170), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    page_count = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Numeric(6, 2), nullable=False, default=0.00)

    checkout_items = db.relationship(
        'Checkout_Item',
        back_populates='book',
        lazy=True
    )

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    salt = db.Column(db.String(50), nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)

    cart = db.relationship(
        'Cart',
        back_populates='buyer',
        lazy=True
    )

    invoice = db.relationship(
        'Invoice',
        back_populates = 'buyer',
        lazy=True
    )

class Cart(db.Model):
    __tablename__ = 'user_carts'

    id = db.Column(db.Integer, primary_key=True)
    active_cart = db.Column(db.Boolean, nullable = False, default = False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    buyer = db.relationship('User', back_populates='cart')
    checkout_items = db.relationship(
        'Checkout_Item',
        back_populates='cart',
        lazy=True
    )
    invoice = db.relationship('Invoice', back_populates='cart', lazy=True)

class Checkout_Item(db.Model):
    __tablename__ = 'checkout_items'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    cart_id = db.Column(db.Integer, db.ForeignKey('user_carts.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    cart = db.relationship('Cart', back_populates='checkout_items')
    book = db.relationship('Book', back_populates='checkout_items')

class Invoice(db.Model):
    __tablename__= 'order_invoices'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('user_carts.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    order_name = db.Column(db.String(100), nullable=False)
    shipping_address = db.Column(db.String(200), nullable=False)
    zipcode = db.Column(db.String(5), nullable=False)

    last_four_card_digits = db.Column(db.String(4), nullable=False)
    card_expire_date = db.Column(db.String(5), nullable=False)

    order_total = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)

    cart = db.relationship('Cart', back_populates='invoice')
    buyer = db.relationship('User', back_populates='invoice')
