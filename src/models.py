from extensions import db 
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    orders = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}')"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    apartment = db.Column(db.String(10), nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    delivery_time = db.Column(db.String(50), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Принят')
    items = db.relationship('OrderItem', backref='order', lazy=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Order({self.id}, {self.user_id}, {self.status})"

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product = db.relationship('Product')
    def __repr__(self):
        return f"OrderItem({self.order_id}, {self.product_id}, {self.quantity})"

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='ratings')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)