from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from extensions import db
import json


def create_app():
    app = Flask(
        __name__,
        static_folder="src/static",
        template_folder="src/templates",
    )
    app.config['SECRET_KEY'] = 'e354688fWW1' 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    return app
app = create_app()
from src.models import Product, User, Order, OrderItem, Rating
from src.forms import RegistrationForm, LoginForm, OrderForm
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Требуется вход в систему.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username  # Добавляем имя в сессию
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        session['username'] = new_user.username  # Добавляем имя в сессию
        flash('Регистрация прошла успешно! Вы вошли в систему.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    masked_password = user.password[:4] + '*' * (len(user.password) - 4)
    return render_template('profile.html', user=user, masked_password=masked_password)

@app.route('/logout', methods=['POST'])  # Разрешаем только POST-запросы
def logout():
    session.clear()  # Полная очистка сессии
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('index'))  # Перенаправляем на главную

@app.route('/api/cart', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_cart():
    if request.method == 'GET':
        cart = session.get('cart', [])
        products = []
        total = 0.0
        
        for item in cart:
            product = Product.query.get(item['id'])
            if product:
                item_total = product.price * item['quantity']
                products.append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'quantity': item['quantity'],
                    'total': item_total
                })
                total += item_total
        
        return jsonify({
            'products': products,
            'total': total
        })

    elif request.method == 'POST':
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        cart = session.get('cart', [])
        found = False
        
        for item in cart:
            if item['id'] == product_id:
                item['quantity'] += quantity
                found = True
                break
        
        if not found:
            cart.append({
                'id': product_id,
                'quantity': quantity
            })
        
        session['cart'] = cart
        return jsonify({'success': True})

    elif request.method == 'PUT':
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        
        if not product_id or quantity is None:
            return jsonify({'error': 'Product ID and quantity are required'}), 400
        
        cart = session.get('cart', [])
        
        for item in cart:
            if item['id'] == product_id:
                item['quantity'] = quantity
                break
        
        session['cart'] = cart
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        product_id = request.args.get('product_id')
        
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        cart = session.get('cart', [])
        cart = [item for item in cart if item['id'] != product_id]
        session['cart'] = cart
        return jsonify({'success': True})

@app.route('/cart')
def cart():
    return render_template('cart.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    form = OrderForm()
    items, total_price = get_cart_items()

    if form.validate_on_submit():
        user_id = session['user_id']
        new_order = Order(user_id=user_id,
                          city=form.city.data,
                          street=form.street.data,
                          apartment=form.apartment.data,
                          floor=form.floor.data,
                          delivery_time=form.delivery_time.data,
                          payment_method=form.payment_method.data)
        db.session.add(new_order)
        db.session.commit()

        # Add order items to the OrderItem table
        for item in items:
            order_item = OrderItem(order_id=new_order.id, product_id=item['product']['id'], quantity=item['quantity'])
            db.session.add(order_item)

        db.session.commit()

        # Clear the cart in the session
        session['cart'] = []
        session.modified = True

        flash('Заказ успешно оформлен!', 'success')
        return redirect(url_for('index'))

    return render_template('order.html', form=form, cart_items=items, total=total_price)


@app.route('/delivery')
@login_required
def delivery():
    user_id = session['user_id']
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_date.desc()).all()
    return render_template('delivery.html', orders=orders)

@app.route('/rate', methods=['GET', 'POST'])
@login_required
def rate():
    if request.method == 'POST':
        try:
            rating_value = int(request.form.get('rating', 0))
            if 1 <= rating_value <= 5:
                # Убедитесь, что current_user.id существует
                if hasattr(current_user, 'id'):
                    new_rating = Rating(
                        value=rating_value,
                        user_id=current_user.id
                    )
                    db.session.add(new_rating)
                    db.session.commit()
                    flash('Спасибо за оценку!', 'success')
                else:
                    flash('Ошибка: пользователь не идентифицирован', 'danger')
            else:
                flash('Оценка должна быть от 1 до 5', 'warning')
        except ValueError:
            flash('Некорректная оценка', 'danger')
        return redirect(url_for('index'))
    return render_template('rate.html')

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)