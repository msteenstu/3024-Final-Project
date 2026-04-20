from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError, InternalError
import traceback
import re
from app import app, csrf, db
from app.models import Book, User
from app.user_operations import*
from app.shop_operations import*

#From docs
@app.before_request
def validate_csrf_manually():
    if request.endpoint in [
        'login', 'signup', 'logout', 'add_book_to_cart', 'complete_order'] \
        and request.method == 'POST':
            csrf.protect()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/user/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        form_email = request.form.get('email')
        form_name = request.form.get('name')
        form_password = request.form.get('password')
        form_password_confirm = request.form.get('password_confirm')

        if not form_email or not form_name  \
              or not form_password or not form_password_confirm:
            flash('Please fill out the signup form completely')
            return render_template('signup.html')
        
        if form_password != form_password_confirm:
            flash('Passwords do not match')
            return render_template('signup.html')
        
        check_password_against_policy, message = password_policy_enforcement(form_password)
        if not check_password_against_policy:
            flash(message)
            return render_template('signup.html')

        try:
            register_account(
                email = form_email,
                name = form_name,
                password = form_password
            )
            flash('User created successfully!')
            return redirect(url_for('index'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists, signup with a different one.')
            return render_template('signup.html')
        
        except Exception:
            traceback.print_exc()
            db.session.rollback()
            flash('Something went wrong when creating your account')
            return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/user/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
            form_email = request.form.get('email')
            form_password = request.form.get('password')

            if not form_email or not form_password:
                flash('Please fill out the signup form completely.')
                return render_template('login.html')

            try:
                user = query_user(form_email)
                _, user_password_hash = hash_user_password(form_password)
                if user \
                and user_password_hash  == user.password:
                    login_user(user)
                    return redirect(url_for('view_books'))
                else:
                    flash('Invalid credentials, try again.')
                    return render_template('login.html')
                
            except Exception:
                traceback.print_exc()
                flash('An error occurred during login, try again,')
                return redirect (url_for('index'))

    return render_template('login.html')

@app.route('/user/signout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('Successfully logged out, see you next time!')
    return redirect(url_for('index'))

@app.route('/user/account', methods=['GET', 'POST'])
@login_required
def view_account():
    return render_template('user_account.html')

@app.route('/user/delete', methods=['POST'])
@login_required
def delete_account():
    return redirect(url_for('index'))

@app.route('/user/books', methods=['GET','POST'])
@login_required
def view_books():
    books = query_all_books()

    if request.method == 'POST' and request.form.get('genre'):
        books = query_books_by_genre(request.form.get('genre'))

    return render_template('book_listings.html', books=books)

@app.route('/user/cart/add', methods=['POST'])
@login_required
def add_book_to_cart():
    if request.method == 'POST':
        buyer_cart = get_buyer_cart(current_user.id)
        book_id = int(request.form.get('book_id'))
        book_quantity = int(request.form.get('book_quantity'))

        if book_quantity is None:
            flash('You must select a positive, whole book quantity.')
            return redirect(url_for('view_books'))

        valid_book_quantity, message = validate_book_quantity_at_add(buyer_cart, book_id, book_quantity)
        if not valid_book_quantity:
            flash(message)
            return redirect(url_for('view_books'))
        
        try:
            add_to_cart(current_user.id, book_id, book_quantity)
            flash("Book added to your cart.")
            return redirect(url_for('view_books'))

        except (IntegrityError, ValueError, InternalError):
            db.session.rollback()
            flash('An error occurred while adding the book to cart, try again later.')
            return redirect(url_for('view_books'))

@app.route('/user/cart', methods=['GET'])
@login_required
def view_cart():
    buyer_cart = get_buyer_cart(current_user.id)
    checkout_items = buyer_cart.checkout_items
    
    valid_checkout_item_quantity, message = validate_book_quantity_in_cart(buyer_cart)
    if not valid_checkout_item_quantity:
        flash(message)
        return redirect(url_for('view_cart')) #refreshes pages to cart items are up-to-date

    order_total = calculate_cart_total(checkout_items)

    return render_template('view_cart.html', checkout_items = checkout_items, order_total = order_total)

@app.route('/user/cart/purchase', methods=['POST'])
@login_required
def complete_order():
    buyer_cart = get_buyer_cart(current_user.id)

    if request.method == 'POST' and buyer_cart is not None:
        
        order_name = request.form.get('order_name')
        shipping_address = request.form.get('shipping_address')
        shipping_zipcode = request.form.get('zipcode')
        payment_card = request.form.get('payment_card')
        card_expire_date = request.form.get('expiration_date')

        #https://regex101.com/r/AFarfB/1
        #/^(0[1-9]|1[0-2])\/?([0-9]{2})$/
        #inspired by, changed some of it
        #and html pattern
        if (not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", card_expire_date) 
                or int(card_expire_date[3:]) < 26):
            flash('Invalid expiration date provided')
            return redirect(url_for('view_cart'))

        if (len(payment_card) < 16 or len(payment_card) > 19 
            or not payment_card.isdigit()):
            flash('Invalid payment card.')
            return redirect(url_for('view_cart'))

        try:
            create_invoice(
                buyer_cart,
                current_user.id,
                order_name,
                shipping_address,
                shipping_zipcode,
                payment_card[-4:],
                card_expire_date
            )
            update_book_inventory(buyer_cart)
            buyer_cart.active_cart = False
            db.session.commit()

            flash('Order was placed, thanks for shopping with Book Worm')
            return redirect(url_for('index'))

        except (IntegrityError, ValueError, InternalError):
            db.session.rollback()
            flash('An error occurred while processing your order, try again.')
            return redirect(url_for('view_cart'))


@app.route('/user/orders', methods=['GET'])
def view_orders():
    return render_template('view_orders.html')