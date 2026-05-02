"""
Author: Mckenna Steenbock
Description: The methods in this module
all support key shopping functionality
including managing user carts and 
validating book inventory. It also handles 
user interactions with the bookstore including
creating orders and basic querying for user invoices.
"""

from app import app, db
from app.models import Book, Cart, Checkout_Item, Invoice
from sqlalchemy import text
from datetime import datetime
import pytz

def query_all_books():
    """
    Queries all of the available books from
    the database in a similar fashion to
    the genre query to maintain consistency
    in the codebase.
    """
    return db.session.execute(
        text("SELECT * FROM books WHERE quantity > 0")).fetchall()

def query_books_by_genre(user_input):
    """
    Vulnerability: SQL Injection
    
    User-supplied input is directly used in
    a SQL query without parameterization,
    enabling untrusted input to be interpreted 
    as SQL code.
    """
    
    if user_input.lower() == 'all':
        return query_all_books()
    else:
        return db.session.execute(
            text(f"SELECT * FROM books WHERE genre = '{user_input.lower()}'")
            ).fetchall()
    
def get_buyer_cart(user_id):
    buyer_cart = Cart.query.filter_by(
        buyer_id = user_id,
        active_cart = True
    ).first()

    if buyer_cart is None:
        buyer_cart = Cart(
            active_cart = True,
            buyer_id = user_id
        )

        db.session.add(buyer_cart)
        db.session.commit()
    
    return buyer_cart

def add_to_cart(user_id: int, book_id: int, book_quantity: int):
    buyer_cart = get_buyer_cart(user_id)
    book = Book.query.filter_by(id = book_id).first()
    
    current_checkout_item = Checkout_Item.query.filter_by(
        cart_id = buyer_cart.id,
        book_id = book.id
    ).first()

    if current_checkout_item is None:
        current_checkout_item = Checkout_Item(
            cart_id = buyer_cart.id,
            book_id = book.id,
            quantity = book_quantity
        )
        db.session.add(current_checkout_item)
    else:
        current_checkout_item.quantity += book_quantity
    
    db.session.commit()

def validate_book_quantity_at_add(buyer_cart, book_id: int, requested_quantity: int):
    """
    Ensures the quantity of books being
    added to the user's cart is a valid value.
    """
    
    current_book = Book.query.filter_by(id = book_id).first()

    if current_book is None:
        return False, "Book does not exist or cannot be found."
    
    if requested_quantity <= 0:
        return False, "You cannot add less than one book to your cart."
   
    book_cart_quantity = get_book_quantity_in_cart(buyer_cart.id, current_book.id)

    if book_cart_quantity + requested_quantity > current_book.quantity:
        return False, f"There are not enough copies of {current_book.title} in stock to fulfill this request."
    else:
        return True, ""

def get_book_quantity_in_cart(buyer_cart_id, book_id):
    current_book_in_cart = Checkout_Item.query.filter_by(
        book_id = book_id,
        cart_id = buyer_cart_id
    ).first()

    if current_book_in_cart is None:
        return 0
    else:
        return current_book_in_cart.quantity


def calculate_cart_total(checkout_items):
    total = 0
    for item in checkout_items:
        total += float(item.book.price) * item.quantity

    total = round(total, 2)
    return f"{total:.2f}"

def validate_book_quantity_in_cart(buyer_cart):
    """
    Ensures the quantity of books in the
    user's cart is valid before letting
    the user make a purchase.
    """
    
    checkout_items = buyer_cart.checkout_items
    books_removed = []

    for item in checkout_items:
        if (item.book.quantity <= 0 
            or item.quantity > item.book.quantity):
            books_removed.append(item.book.title)
            db.session.delete(item)

    if len(books_removed) == 0:
        return True, " "
    else:
        db.session.commit()
        return (
            False,
            f"The following books were removed from your cart due to insufficient stock: "
            f"{', '.join(books_removed)}"
        )

def create_invoice(
        buyer_cart, buyer_id: int, order_name: str, shipping_address: str,
        zipcode: str, last_four_card_digits: str, card_expire_date: str,
    ):

    order_total = calculate_cart_total(buyer_cart.checkout_items)
    order_date = datetime.now(pytz.timezone('America/Denver'))

    new_order = Invoice(
        cart_id = buyer_cart.id,
        buyer_id = buyer_id,
        order_name = order_name,
        shipping_address = shipping_address,
        zipcode = zipcode,
        last_four_card_digits = last_four_card_digits,
        card_expire_date = card_expire_date,
        order_total = order_total,
        order_date = order_date
    )

    db.session.add(new_order)

def update_book_inventory(buyer_cart):
    """
    Updates the book quantities in
    the database after a purchase was
    made.
    """
    
    checkout_items = buyer_cart.checkout_items

    for item in checkout_items:
        item.book.quantity -= item.quantity

def query_all_buyer_orders(buyer_id: int):
    return Invoice.query.filter_by(buyer_id = buyer_id).all()

def get_buyer_invoice(invoice_id: int):
    """
    Vulnerability: Insecure Direct Object Reference
    
    The query retrieves an invoice using only
    the passed in ID and does not enforce an
    ownership check by filtering on the current
    user's ID.
    """
    
    return Invoice.query.filter_by(id = invoice_id).first()
