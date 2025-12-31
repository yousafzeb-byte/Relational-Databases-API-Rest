"""
E-commerce API with Flask, SQLAlchemy, Marshmallow, and MySQL
Coding Temple - Relational Databases & API REST Development Project

Author: Yousaf Zeb
Date: December 23, 2025
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Database Configuration
DB_USERNAME = os.getenv('DB_USERNAME', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'ecommerce_api')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)


# ============================================================
# DATABASE MODELS
# ============================================================

# Association table for Many-to-Many relationship between Orders and Products
order_product = db.Table('order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Relationship: One User can have Many Orders
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Product {self.product_name}>'


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Many-to-Many relationship with Products
    products = db.relationship('Product', secondary=order_product, lazy='subquery',
                             backref=db.backref('orders', lazy=True))
    
    def __repr__(self):
        return f'<Order {self.id}>'


# ============================================================
# MARSHMALLOW SCHEMAS
# ============================================================

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


class OrderSchema(ma.SQLAlchemyAutoSchema):
    products = ma.Nested(ProductSchema, many=True)
    
    class Meta:
        model = Order
        load_instance = True
        include_fk = True  # Include foreign keys like user_id

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


# ============================================================
# USER ENDPOINTS
# ============================================================

@app.route('/users', methods=['GET'])
def get_users():
    """GET /users: Retrieve all users"""
    users = User.query.all()
    return users_schema.jsonify(users), 200


@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """GET /users/<id>: Retrieve a user by ID"""
    user = User.query.get_or_404(id)
    return user_schema.jsonify(user), 200


@app.route('/users', methods=['POST'])
def create_user():
    """POST /users: Create a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['name', 'address', 'email']):
            return jsonify({'error': 'Missing required fields: name, address, email'}), 400
        
        new_user = User(
            name=data['name'],
            address=data['address'],
            email=data['email']
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return user_schema.jsonify(new_user), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    """PUT /users/<id>: Update a user by ID"""
    try:
        user = User.query.get_or_404(id)
        data = request.get_json()
        
        if 'name' in data:
            user.name = data['name']
        if 'address' in data:
            user.address = data['address']
        if 'email' in data:
            user.email = data['email']
        
        db.session.commit()
        return user_schema.jsonify(user), 200
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    """DELETE /users/<id>: Delete a user by ID"""
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User {id} deleted successfully'}), 200


# ============================================================
# PRODUCT ENDPOINTS
# ============================================================

@app.route('/products', methods=['GET'])
def get_products():
    """GET /products: Retrieve all products"""
    products = Product.query.all()
    return products_schema.jsonify(products), 200


@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    """GET /products/<id>: Retrieve a product by ID"""
    product = Product.query.get_or_404(id)
    return product_schema.jsonify(product), 200


@app.route('/products', methods=['POST'])
def create_product():
    """POST /products: Create a new product"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['product_name', 'price']):
            return jsonify({'error': 'Missing required fields: product_name, price'}), 400
        
        new_product = Product(
            product_name=data['product_name'],
            price=float(data['price'])
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        return product_schema.jsonify(new_product), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    """PUT /products/<id>: Update a product by ID"""
    try:
        product = Product.query.get_or_404(id)
        data = request.get_json()
        
        if 'product_name' in data:
            product.product_name = data['product_name']
        if 'price' in data:
            product.price = float(data['price'])
        
        db.session.commit()
        return product_schema.jsonify(product), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    """DELETE /products/<id>: Delete a product by ID"""
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': f'Product {id} deleted successfully'}), 200


# ============================================================
# ORDER ENDPOINTS
# ============================================================

@app.route('/orders', methods=['POST'])
def create_order():
    """POST /orders: Create a new order (requires user_id and optional order_date)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'user_id' not in data:
            return jsonify({'error': 'Missing required field: user_id'}), 400
        
        # Verify user exists
        user = User.query.get_or_404(data['user_id'])
        
        # Parse order_date if provided, otherwise use current datetime
        order_date = datetime.utcnow()
        if 'order_date' in data:
            try:
                order_date = datetime.fromisoformat(data['order_date'])
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DD HH:MM:SS)'}), 400
        
        new_order = Order(
            user_id=data['user_id'],
            order_date=order_date
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return order_schema.jsonify(new_order), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    """PUT /orders/<order_id>/add_product/<product_id>: Add a product to an order (prevent duplicates)"""
    try:
        order = Order.query.get_or_404(order_id)
        product = Product.query.get_or_404(product_id)
        
        # Check if product is already in the order (prevent duplicates)
        if product in order.products:
            return jsonify({'message': 'Product already exists in this order'}), 400
        
        order.products.append(product)
        db.session.commit()
        
        return order_schema.jsonify(order), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def remove_product_from_order(order_id, product_id):
    """DELETE /orders/<order_id>/remove_product/<product_id>: Remove a product from an order"""
    try:
        order = Order.query.get_or_404(order_id)
        product = Product.query.get_or_404(product_id)
        
        if product not in order.products:
            return jsonify({'error': 'Product not found in this order'}), 404
        
        order.products.remove(product)
        db.session.commit()
        
        return jsonify({'message': f'Product {product_id} removed from order {order_id}'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    """GET /orders/user/<user_id>: Get all orders for a user"""
    user = User.query.get_or_404(user_id)
    orders = Order.query.filter_by(user_id=user_id).all()
    return orders_schema.jsonify(orders), 200


@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_order_products(order_id):
    """GET /orders/<order_id>/products: Get all products for an order"""
    order = Order.query.get_or_404(order_id)
    return products_schema.jsonify(order.products), 200


# ============================================================
# HOME ROUTE
# ============================================================

@app.route('/')
def home():
    """Home route with API documentation"""
    return jsonify({
        'message': 'Welcome to E-commerce API',
        'author': 'Yousaf Zeb',
        'endpoints': {
            'users': {
                'GET /users': 'Retrieve all users',
                'GET /users/<id>': 'Retrieve a user by ID',
                'POST /users': 'Create a new user',
                'PUT /users/<id>': 'Update a user by ID',
                'DELETE /users/<id>': 'Delete a user by ID'
            },
            'products': {
                'GET /products': 'Retrieve all products',
                'GET /products/<id>': 'Retrieve a product by ID',
                'POST /products': 'Create a new product',
                'PUT /products/<id>': 'Update a product by ID',
                'DELETE /products/<id>': 'Delete a product by ID'
            },
            'orders': {
                'POST /orders': 'Create a new order',
                'PUT /orders/<order_id>/add_product/<product_id>': 'Add a product to an order',
                'DELETE /orders/<order_id>/remove_product/<product_id>': 'Remove a product from an order',
                'GET /orders/user/<user_id>': 'Get all orders for a user',
                'GET /orders/<order_id>/products': 'Get all products for an order'
            }
        }
    }), 200


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():
    """Initialize the database and create all tables"""
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully!")


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == '__main__':
    # Uncomment the line below to initialize the database on first run
    init_db()
    
    app.run(debug=True)
