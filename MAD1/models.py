from datetime import datetime, date
from flask_login import UserMixin
from MAD1.database import db
from MAD1 import login_manager



# Association table for the many-to-many relationship between User and Product
user_product_association = db.Table(
    'user_product_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

# Association table for the many-to-many relationship between User and Category
user_category_association = db.Table(
    'user_category_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    carts = db.relationship('Cart', backref='user', lazy=True)
    purchased_products = db.relationship('Product', secondary=user_product_association, backref=db.backref('users', lazy=True))
    favorite_categories = db.relationship('Category', secondary=user_category_association, backref=db.backref('users', lazy=True))

    def get_id(self):
        return self.id

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    manufacturer = db.Column(db.String(80))
    expiry_date = db.Column(db.Date, nullable = False)
    rate_per_unit = db.Column(db.Float)
    unit = db.Column(db.String(10))  # e.g., 'Rs/Kg', 'Rs/Litre'
    units_available = db.Column(db.Integer, nullable = False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    product = db.relationship('Product', backref='carts')

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
