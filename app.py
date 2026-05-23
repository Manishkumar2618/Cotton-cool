import os
import json
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, session
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    verify_jwt_in_request,
    set_access_cookies,
    unset_jwt_cookies,
)
from functools import wraps
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JWT_SECRET_KEY'] = 'change-me-to-a-secure-key'
app.config['SECRET_KEY'] = 'change-me-to-a-secure-session-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_NAME'] = 'fashion_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
jwt = JWTManager(app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERS = {
    'admin': {
        'password': 'admin',
        'role': 'admin',
        'name': 'Admin',
        'email': 'admin@fashionhub.com',
        'orders': []
    }
}

# Add requested admin user for UI access
USERS['Maniskumar1226'] = {
    'password': 'Manish@2622',
    'role': 'admin',
    'name': 'Manish',
    'email': 'maniskumar1226@example.com',
    'orders': []
}

CARTS = {}
ORDERS = []

with open(os.path.join(DATA_DIR, 'products.json'), 'r', encoding='utf-8') as f:
    PRODUCTS = json.load(f)

CATEGORIES = ['Shirts', 'T-Shirts', 'Track Pants', 'Trousers']
COLLECTIONS = [
    {'slug': 'shirts', 'title': 'Shirts', 'subtitle': 'Smart styling for every day'},
    {'slug': 'tshirts', 'title': 'T-Shirts', 'subtitle': 'Comfort meets cool'},
    {'slug': 'track-pants', 'title': 'Track Pants', 'subtitle': 'Move freely'},
    {'slug': 'trousers', 'title': 'Trousers', 'subtitle': 'Tailored for modern life'}
]

PAYMENT_METHODS = ['cards', 'upi', 'wallets']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_product(product_id):
    for p in PRODUCTS:
        if p['id'] == product_id:
            return p
    return None


def get_current_username():
    username = None
    try:
        verify_jwt_in_request(optional=True)
        username = get_jwt_identity()
    except Exception:
        username = None
    if not username:
        username = session.get('username')
    return username


def get_current_user():
    username = get_current_username()
    if username and username in USERS:
        return USERS[username].copy()
    return None


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


def filter_products(category=None, filters=None):
    results = PRODUCTS
    if category:
        results = [p for p in results if p['category'].lower() == category.lower()]
    if not filters:
        return results
    if filters.get('size'):
        results = [p for p in results if filters['size'] in p.get('sizes', [])]
    if filters.get('color'):
        results = [p for p in results if filters['color'].lower() in [c.lower() for c in p.get('colors', [])]]
    if filters.get('fabric'):
        results = [p for p in results if filters['fabric'].lower() == p.get('fabric', '').lower()]
    if filters.get('price_min'):
        results = [p for p in results if p['price'] >= float(filters['price_min'])]
    if filters.get('price_max'):
        results = [p for p in results if p['price'] <= float(filters['price_max'])]
    return results


@app.route('/')
def index():
    featured = [p for p in PRODUCTS if p['featured']][:8]
    return render_template('index.html', collections=COLLECTIONS, featured=featured, categories=CATEGORIES)


@app.route('/category/<slug>')
def category_page(slug):
    filters = {
        'size': request.args.get('size'),
        'color': request.args.get('color'),
        'fabric': request.args.get('fabric'),
        'price_min': request.args.get('price_min'),
        'price_max': request.args.get('price_max')
    }
    products = filter_products(slug.replace('-', ' '), filters)
    return render_template('category.html', category=slug.replace('-', ' ').title(), products=products, filters=filters)


@app.route('/search')
def search_page():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        q_lower = query.lower()
        results = [p for p in PRODUCTS if q_lower in p['name'].lower() or q_lower in p['description'].lower() or q_lower in p['category'].lower()]
    return render_template('category.html', category=f'Search results for "{query}"', products=results, filters={})


@app.route('/product/<product_id>')
def product_page(product_id):
    product = get_product(product_id)
    if not product:
        return redirect(url_for('index'))
    return render_template('product.html', product=product)


@app.route('/customize/<product_id>')
def customize(product_id):
    product = get_product(product_id)
    if not product:
        return redirect(url_for('index'))
    return render_template('customize.html', product=product)


@app.route('/cart')
def cart_page():
    cart_id = request.cookies.get('cart_id')
    cart = CARTS.get(cart_id, []) if cart_id else []
    items = []
    total = 0
    for item in cart:
        product = get_product(item['product_id'])
        if product:
            item_total = product['price'] * item['quantity']
            total += item_total
            items.append({**item, 'product': product, 'item_total': item_total})
    return render_template('cart.html', items=items, total=total)


@app.route('/account')
def account_page():
    return render_template('account.html')


@app.route('/admin')
def admin_page():
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return redirect(url_for('account_page'))
    sales_total = sum(order['total'] for order in ORDERS)
    popular = sorted(PRODUCTS, key=lambda p: p['sales'], reverse=True)[:6]
    sales_by_category = {}
    orders_by_status = {}
    top_customers = {}
    sales_trend = {}
    for order in ORDERS:
        orders_by_status[order['status']] = orders_by_status.get(order['status'], 0) + 1
        top_customers[order['customer']] = top_customers.get(order['customer'], 0) + order['total']
        order_date = datetime.fromisoformat(order['timestamp']).date().isoformat()
        sales_trend[order_date] = sales_trend.get(order_date, 0) + order['total']
        for item in order['items']:
            category = item['product'].get('category', 'Other')
            sales_by_category[category] = sales_by_category.get(category, 0) + item['product']['price'] * item['quantity']
    top_customers = [{'customer': customer, 'total': total} for customer, total in sorted(top_customers.items(), key=lambda x: x[1], reverse=True)[:5]]
    inventory_alerts = [p for p in PRODUCTS if p.get('stock', 0) < 10]
    sales_trend = [{'date': date, 'revenue': revenue} for date, revenue in sorted(sales_trend.items())]
    return render_template(
        'admin.html',
        orders=ORDERS,
        sales_total=sales_total,
        popular=popular,
        sales_by_category=sales_by_category,
        orders_by_status=orders_by_status,
        top_customers=top_customers,
        inventory_alerts=inventory_alerts,
        sales_trend=sales_trend
    )


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    user = USERS.get(username)
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=username)
    response = jsonify({'access_token': access_token, 'user': {'username': username, 'name': user['name'], 'email': user['email'], 'role': user.get('role', 'customer'), 'phone': user.get('phone'), 'pincode': user.get('pincode'), 'address': user.get('address')}})
    set_access_cookies(response, access_token)
    session['username'] = username
    return response


@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    pincode = data.get('pincode')
    address = data.get('address')
    if not username or not email or not password:
        return jsonify({'error': 'Missing fields'}), 400
    if username in USERS:
        return jsonify({'error': 'Username already exists'}), 409
    USERS[username] = {
        'password': password,
        'role': 'customer',
        'name': username.title(),
        'email': email,
        'phone': phone,
        'pincode': pincode,
        'address': address,
        'orders': []
    }
    access_token = create_access_token(identity=username)
    response = jsonify({'access_token': access_token, 'user': {'username': username, 'name': username.title(), 'email': email, 'role': 'customer', 'phone': phone, 'pincode': pincode, 'address': address}})
    set_access_cookies(response, access_token)
    session['username'] = username
    return response


@app.route('/api/me')
def api_me():
    username = None
    try:
        verify_jwt_in_request(optional=True)
        username = get_jwt_identity()
    except Exception:
        username = None
    if not username:
        username = session.get('username')
    if not username or username not in USERS:
        return jsonify({'user': None})
    user = USERS[username].copy()
    user['username'] = username
    user_orders = user.get('orders', [])
    return jsonify({'user': {'username': username, 'name': user['name'], 'email': user['email'], 'role': user.get('role', 'customer'), 'phone': user.get('phone'), 'pincode': user.get('pincode'), 'address': user.get('address'), 'orders': user_orders}})


@app.route('/api/logout', methods=['POST'])
def api_logout():
    response = jsonify({'success': True})
    unset_jwt_cookies(response)
    session.pop('username', None)
    response.set_cookie('fashion_user', '', expires=0)
    return response


@app.route('/api/cart', methods=['GET', 'POST', 'DELETE'])
def api_cart():
    cart_id = request.cookies.get('cart_id') or str(uuid.uuid4())
    if cart_id not in CARTS:
        CARTS[cart_id] = []

    if request.method == 'GET':
        return jsonify({'cart_id': cart_id, 'items': CARTS[cart_id]})

    data = request.json or {}
    if request.method == 'POST':
        item = {
            'product_id': data.get('product_id'),
            'quantity': int(data.get('quantity', 1)),
            'customization': data.get('customization', {})
        }
        CARTS[cart_id].append(item)
        response = jsonify({'cart_id': cart_id, 'items': CARTS[cart_id]})
        response.set_cookie('cart_id', cart_id, max_age=30*24*3600)
        return response

    if request.method == 'DELETE':
        prod_id = data.get('product_id')
        CARTS[cart_id] = [item for item in CARTS[cart_id] if item['product_id'] != prod_id]
        return jsonify({'cart_id': cart_id, 'items': CARTS[cart_id]})


@app.route('/api/checkout', methods=['POST'])
@jwt_required(optional=True)
def api_checkout():
    data = request.json or {}
    cart_id = request.cookies.get('cart_id')
    if not cart_id or cart_id not in CARTS or not CARTS[cart_id]:
        return jsonify({'error': 'Cart is empty'}), 400
    cart = CARTS[cart_id]
    total = 0
    items = []
    for item in cart:
        product = get_product(item['product_id'])
        if not product:
            continue
        quantity = item.get('quantity', 1)
        total += product['price'] * quantity
        items.append({'product': product, 'quantity': quantity, 'customization': item.get('customization', {})})
    customer = get_current_username() or 'guest'
    profile = get_current_user() or {}
    order = {
        'order_id': str(uuid.uuid4()),
        'timestamp': datetime.utcnow().isoformat(),
        'total': total,
        'items': items,
        'status': 'Processing',
        'payment_method': data.get('payment_method', 'cards'),
        'payment_gateway': data.get('payment_gateway', 'placeholder'),
        'customer': customer,
        'shipping_phone': profile.get('phone'),
        'shipping_pincode': profile.get('pincode'),
        'shipping_address': profile.get('address')
    }
    order['customer'] = customer
    ORDERS.append(order)
    if order['customer'] in USERS:
        USERS[order['customer']]['orders'].append(order)
    CARTS[cart_id] = []
    return jsonify({'success': True, 'order': order})


@app.route('/api/payment-intent', methods=['POST'])
def api_payment_intent():
    data = request.json or {}
    method = data.get('payment_method', 'cards')
    gateway = data.get('payment_gateway', 'placeholder')
    return jsonify({
        'gateway': gateway,
        'payment_method': method,
        'status': 'ready',
        'message': f'Payment gateway placeholder created for {method}. Replace with an actual provider integration in production.',
        'instructions': f'Use this placeholder to wire your payment gateway for {gateway}.',
        'redirect_url': f'https://example.com/pay/{gateway}'
    })


@app.route('/api/upload-customization', methods=['POST'])
def api_upload_customization():
    if 'design' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['design']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'url': url_for('static', filename=f'uploads/{filename}')})


@app.route('/api/products', methods=['GET', 'POST'])
def api_products():
    if request.method == 'GET':
        return jsonify({'products': PRODUCTS})
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    data = request.json or {}
    product = {
        'id': str(uuid.uuid4()),
        'name': data.get('name', 'New Product'),
        'category': data.get('category', 'Shirts'),
        'price': float(data.get('price', 29.99)),
        'description': data.get('description', ''),
        'sizes': data.get('sizes', ['S', 'M', 'L']),
        'colors': data.get('colors', ['Black', 'White']),
        'fabric': data.get('fabric', 'Cotton'),
        'stock': int(data.get('stock', 25)),
        'sales': 0,
        'images': data.get('images', ['/static/images/product-placeholder.jpg']),
        'featured': bool(data.get('featured', False))
    }
    PRODUCTS.append(product)
    return jsonify({'product': product})


@app.route('/api/products/<product_id>', methods=['PUT', 'DELETE'])
@admin_required
def api_product_modify(product_id):
    product = get_product(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    if request.method == 'DELETE':
        PRODUCTS.remove(product)
        return jsonify({'success': True})
    data = request.json or {}
    for field in ['name', 'category', 'price', 'description', 'sizes', 'colors', 'fabric', 'stock', 'featured', 'images']:
        if field in data:
            product[field] = data[field]
    return jsonify({'product': product})


@app.route('/api/recommendations/<product_id>')
def api_recommendations(product_id):
    product = get_product(product_id)
    if not product:
        return jsonify({'recommendations': []})
    recommendations = [p for p in PRODUCTS if p['category'] == product['category'] and p['id'] != product['id']][:4]
    return jsonify({'recommendations': recommendations})


@app.route('/api/reviews/<product_id>', methods=['GET', 'POST'])
def api_reviews(product_id):
    product = get_product(product_id)
    if not product:
        return jsonify({'reviews': []})
    if 'reviews' not in product:
        product['reviews'] = []
    if request.method == 'POST':
        data = request.json or {}
        product['reviews'].append({'user': data.get('user', 'Guest'), 'rating': int(data.get('rating', 5)), 'comment': data.get('comment', '')})
    return jsonify({'reviews': product['reviews']})


@app.route('/api/coupons')
def api_coupons():
    coupons = [
        {'code': 'NEW15', 'discount': 15, 'description': '15% off on first purchase'},
        {'code': 'SUMMER20', 'discount': 20, 'description': '20% off selected items'}
    ]
    return jsonify({'coupons': coupons})


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


if __name__ == '__main__':
    app.run(debug=True)
