import os
import random
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Import local utilities and services
from utils.auth import login_required
from utils.cart import get_cart, save_cart, calculate_total
from utils.helpers import is_valid_email, get_cart_item_count
import services.product_service as product_service
from services.telegram_service import send_telegram

app = Flask(__name__)

# Configure Flask app keys
app.secret_key = os.getenv("FLASK_SECRET_KEY", "velocestore-session-key-991283")

# Ensure session dictionaries are initialized before handling requests
@app.before_request
def init_session_db():
    if 'users' not in session:
        session['users'] = {}
    if 'orders' not in session:
        session['orders'] = []

# Context processor to inject cart count globally across all templates
@app.context_processor
def inject_cart_count():
    cart = get_cart()
    count = get_cart_item_count(cart)
    return dict(cart_count=count)

# ==========================================
# 1. HOME MODULE
# ==========================================
@app.route('/')
def home():
    try:
        categories = product_service.get_categories()
        featured_products = product_service.get_featured_products(limit=4)
        latest_products = product_service.get_latest_products(limit=4)
        return render_template(
            'home.html',
            categories=categories,
            featured_products=featured_products,
            latest_products=latest_products
        )
    except Exception as e:
        app.logger.error(f"Error loading home page: {e}")
        return render_template('500.html'), 500

# ==========================================
# 2. PRODUCTS PAGE (CATALOG)
# ==========================================
@app.route('/products')
def products():
    try:
        search_query = request.args.get('q', '').strip()
        category_filter = request.args.get('category', '').strip()
        sort_by = request.args.get('sort', '').strip()

        categories = product_service.get_categories()
        all_products = product_service.get_all_products()

        filtered_products = all_products

        # Filter by Category
        if category_filter:
            filtered_products = [p for p in filtered_products if p.get('category') == category_filter]

        # Filter by Search Query
        if search_query:
            filtered_products = [
                p for p in filtered_products
                if search_query.lower() in p.get('title', '').lower()
            ]

        # Sort Products
        if sort_by == 'price_asc':
            filtered_products = sorted(filtered_products, key=lambda x: x.get('price', 0.0))
        elif sort_by == 'price_desc':
            filtered_products = sorted(filtered_products, key=lambda x: x.get('price', 0.0), reverse=True)
        elif sort_by == 'name_asc':
            filtered_products = sorted(filtered_products, key=lambda x: x.get('title', '').lower())
        elif sort_by == 'id_desc':
            filtered_products = sorted(filtered_products, key=lambda x: x.get('id', 0), reverse=True)

        return render_template(
            'products.html',
            products=filtered_products,
            categories=categories,
            active_category=category_filter,
            search_query=search_query,
            active_sort=sort_by
        )
    except Exception as e:
        app.logger.error(f"Error loading products catalog: {e}")
        return render_template('500.html'), 500

# ==========================================
# 3. PRODUCT DETAIL PAGE
# ==========================================
@app.route('/product/<int:id>')
def product_detail(id):
    try:
        product = product_service.get_product_by_id(id)
        if not product:
            return render_template('404.html'), 404

        # Fetch related products (same category, excluding current product)
        all_products = product_service.get_all_products()
        related = [
            p for p in all_products
            if p.get('category') == product.get('category') and p.get('id') != product.get('id')
        ]

        return render_template(
            'product_detail.html',
            product=product,
            related_products=related[:4]
        )
    except Exception as e:
        app.logger.error(f"Error loading product detail ({id}): {e}")
        return render_template('500.html'), 500

# ==========================================
# 4. REGISTER MODULE
# ==========================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Basic Validation
        if not username or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Password confirmation does not match.', 'danger')
            return render_template('register.html')

        # Check if user already exists
        users = session.get('users', {})
        if email in users:
            flash('An account with this email already exists.', 'warning')
            return render_template('register.html')

        # Store user in session
        users[email] = {
            'username': username,
            'email': email,
            'password': password
        }
        session['users'] = users
        session.modified = True

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ==========================================
# 5. LOGIN MODULE
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next', '') or request.form.get('next', '')

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and Password are required.', 'danger')
            return render_template('login.html', next_url=next_url)

        # Authenticate against session registry
        users = session.get('users', {})
        user_data = users.get(email)

        if not user_data or user_data.get('password') != password:
            flash('Invalid email or password.', 'danger')
            return render_template('login.html', next_url=next_url)

        # Set logged in user state
        session['user'] = {
            'username': user_data.get('username'),
            'email': user_data.get('email')
        }
        flash(f"Welcome back, {user_data.get('username')}!", 'success')

        if next_url:
            return redirect(next_url)
        return redirect(url_for('account'))

    return render_template('login.html', next_url=next_url)

# ==========================================
# LOGOUT MODULE
# ==========================================
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

# ==========================================
# 6. ACCOUNT MODULE
# ==========================================
@app.route('/account')
@login_required
def account():
    # Retrieve orders corresponding to this user
    all_orders = session.get('orders', [])
    user_email = session['user'].get('email')

    # Filter orders by logged in email
    user_orders = [o for o in all_orders if o.get('user_email') == user_email]

    return render_template('account.html', orders=user_orders)

# ==========================================
# 7. RESET PASSWORD MODULE
# ==========================================
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not email or not new_password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('reset_password.html')

        if new_password != confirm_password:
            flash('Password confirmation does not match.', 'danger')
            return render_template('reset_password.html')

        users = session.get('users', {})
        if email not in users:
            flash('No registered account was found with that email address.', 'danger')
            return render_template('reset_password.html')

        # Update user password in session
        users[email]['password'] = new_password
        session['users'] = users
        session.modified = True

        flash('Your password has been reset successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

# ==========================================
# 8. CONTACT MODULE
# ==========================================
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not subject or not message:
            flash('All contact fields are required.', 'danger')
            return render_template('contact.html')

        flash('Thank you for contacting E-Store support! Our agents have received your message.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')

# ==========================================
# 9. ADD TO CART ROUTE (COOKIE BASED)
# ==========================================
@app.route('/add-to-cart/<int:id>')
def add_to_cart(id):
    try:
        qty = request.args.get('qty', 1, type=int)
        if qty < 1:
            qty = 1

        product = product_service.get_product_by_id(id)
        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('products'))

        cart = get_cart()
        items = cart.setdefault("items", {})

        prod_id_str = str(id)
        if prod_id_str in items:
            items[prod_id_str] += qty
        else:
            items[prod_id_str] = qty

        flash(f"Added {product.get('title', 'item')} to cart.", 'success')

        response = make_response(redirect(url_for('cart_page')))
        save_cart(response, cart)
        return response
    except Exception as e:
        app.logger.error(f"Error adding to cart ({id}): {e}")
        return render_template('500.html'), 500

# ==========================================
# 10. SHOPPING CART PAGE
# ==========================================
@app.route('/cart')
def cart_page():
    try:
        cart = get_cart()
        items = cart.get("items", {})

        cart_items_details = []
        all_products = product_service.get_all_products()
        # Build dictionary map for O(1) details lookup
        product_map = {str(p.get('id')): p for p in all_products}

        for prod_id_str, quantity in items.items():
            product = product_map.get(prod_id_str)
            if product:
                subtotal = product.get('price', 0.0) * quantity
                cart_items_details.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })

        totals = calculate_total(cart_items_details)

        return render_template(
            'cart.html',
            cart_items=cart_items_details,
            totals=totals
        )
    except Exception as e:
        app.logger.error(f"Error loading cart page: {e}")
        return render_template('500.html'), 500

# ==========================================
# 11. MODIFY CART ROUTES
# ==========================================
@app.route('/cart/increase/<int:id>')
def cart_increase(id):
    cart = get_cart()
    items = cart.get("items", {})
    prod_id_str = str(id)

    if prod_id_str in items:
        items[prod_id_str] += 1

    response = make_response(redirect(url_for('cart_page')))
    save_cart(response, cart)
    return response

@app.route('/cart/decrease/<int:id>')
def cart_decrease(id):
    cart = get_cart()
    items = cart.get("items", {})
    prod_id_str = str(id)

    if prod_id_str in items:
        if items[prod_id_str] > 1:
            items[prod_id_str] -= 1
        else:
            items.pop(prod_id_str, None)

    response = make_response(redirect(url_for('cart_page')))
    save_cart(response, cart)
    return response

@app.route('/cart/remove/<int:id>')
def cart_remove(id):
    cart = get_cart()
    items = cart.get("items", {})
    prod_id_str = str(id)

    items.pop(prod_id_str, None)

    flash('Item removed from your cart.', 'info')
    response = make_response(redirect(url_for('cart_page')))
    save_cart(response, cart)
    return response

# ==========================================
# 12. CHECKOUT ROUTE
# ==========================================
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    try:
        cart = get_cart()
        items = cart.get("items", {})

        if not items:
            flash('Your cart is empty. Please add products before checking out.', 'warning')
            return redirect(url_for('products'))

        # Fetch cart details to display order summary
        all_products = product_service.get_all_products()
        product_map = {str(p.get('id')): p for p in all_products}

        cart_items_details = []
        for prod_id_str, quantity in items.items():
            product = product_map.get(prod_id_str)
            if product:
                subtotal = product.get('price', 0.0) * quantity
                cart_items_details.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })

        totals = calculate_total(cart_items_details)

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()

            if not name or not phone or not address:
                flash('All shipping information is required.', 'danger')
                return render_template('checkout.html', cart_items=cart_items_details, totals=totals)

            # Generate random order ID
            order_id = random.randint(10000, 99999)

            # Map order items details for session storage
            order_items = []
            for item in cart_items_details:
                order_items.append({
                    'product_id': item['product'].get('id'),
                    'title': item['product'].get('title'),
                    'quantity': item['quantity'],
                    'price': item['product'].get('price'),
                    'subtotal': item['subtotal']
                })

            order_data = {
                'id': order_id,
                'user_email': session['user'].get('email'),
                'name': name,
                'phone': phone,
                'address': address,
                'items': order_items,
                'total': totals['grand_total']
            }

            # 1. Save order in session["orders"]
            orders = session.get('orders', [])
            orders.append(order_data)
            session['orders'] = orders
            session.modified = True

            # 2. Send Telegram Notification
            # Runs safely, failures logged and caught internally inside service
            telegram_message = (
                f"🛒 New Order\n"
                f"Customer Name: {name}\n"
                f"Phone Number: {phone}\n"
                f"Address: {address}\n"
                f"Total Amount: ${totals['grand_total']:.2f}"
            )
            send_telegram(telegram_message)

            # 3. Clear cart cookie and flash success page
            flash('Your order has been placed successfully!', 'success')

            response = make_response(render_template('checkout_success.html', order=order_data))
            # Delete cart cookie by saving empty items
            save_cart(response, {"items": {}})
            return response

        return render_template(
            'checkout.html',
            cart_items=cart_items_details,
            totals=totals
        )
    except Exception as e:
        app.logger.error(f"Error handling checkout: {e}")
        return render_template('500.html'), 500

# ==========================================
# ERROR HANDLERS
# ==========================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Listen on all interface IPs for ease of testing
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route("/test-api")
def test_api():
    import requests

    try:
        r = requests.get(
            "https://fakestoreapi.com/products",
            timeout=15
        )

        return {
            "status_code": r.status_code,
            "data": r.json()
        }

    except Exception as e:
        return {
            "error": str(e)
        }