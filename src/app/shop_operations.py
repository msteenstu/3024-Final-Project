from app import app, db
from app.models import User, Book, Cart, Checkout_Item, Invoice
from sqlalchemy import text

def query_all_books():
    return db.session.execute(
        text("SELECT * FROM books")).fetchall()

def query_books_by_genre(user_input):
    return db.session.execute(
        text(f"SELECT * FROM books WHERE genre = '{user_input}'")
        ).fetchall()
    
def get_buyer_cart():
    pass

def add_to_cart():
    pass

def validate_checkout_item():
    pass

def place_order():
    pass

def create_invoice():
    pass

def query_all_buyer_orders():
    pass