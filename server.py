from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    abort,
    session
)
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from src.database import Database

app = Flask(
    __name__,
    static_folder="src/static", # Задаем static-папку
    template_folder="src/template", # Задаем папку для шаблонов (hmtl-файлов)
)
app.config['SECRET_KEY'] = 'e354688fWW1' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    special_offer = db.Column(db.Text)  

    def __repr__(self):
        return f'<MenuItem {self.name}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    payment_method = db.Column(db.String(50)) 

    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f'<Order {self.id} - User: {self.user.username}>'


def is_admin_user():
    """Checks if the current user is an admin."""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return user and user.is_admin
    return False

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        is_admin = 'admin' in username.lower()

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    if not is_admin_user():
        return redirect(url_for('login'))

    num_users = User.query.count()
    num_menu_items = MenuItem.query.count()
    num_orders = Order.query.count()

    return render_template('admin_dashboard.html', num_users=num_users, num_menu_items=num_menu_items, num_orders=num_orders)


@app.route('/admin/menu')
def admin_menu():
  if not is_admin_user():
      return redirect(url_for('login'))
  menu_items = MenuItem.query.all() 

  return render_template('admin_menu.html', menu_items = menu_items)


@app.route('/admin/menu/add', methods=['GET', 'POST'])
def add_menu_item():
    if not is_admin_user():
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        image = request.form['image'] 
        special_offer = request.form['special_offer']

        new_item = MenuItem(name=name, price=price, description=description, image=image, special_offer=special_offer)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('admin_menu')) 

    return render_template('add_menu_item.html')  


@app.route('/admin/menu/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id):
    if not is_admin_user():
        return redirect(url_for('login'))

    item = MenuItem.query.get_or_404(item_id)

    if request.method == 'POST':
        item.name = request.form['name']
        item.price = float(request.form['price'])
        item.description = request.form['description']
        item.image = request.form['image']
        item.special_offer = request.form['special_offer']

        db.session.commit()
        return redirect(url_for('admin_menu')) 

    return render_template('edit_menu_item.html', item=item)


@app.route('/admin/menu/delete/<int:item_id>')
def delete_menu_item(item_id):
    if not is_admin_user():
        return redirect(url_for('login'))

    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin_menu')) 

@app.route('/admin/orders')
def admin_orders():
    if not is_admin_user():
        return redirect(url_for('login'))

    orders = Order.query.all()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/orders/edit/<int:order_id>', methods=['GET', 'POST'])
def edit_order_status(order_id):
    if not is_admin_user():
        return redirect(url_for('login'))

    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        order.status = request.form['status']
        db.session.commit()
        return redirect(url_for('admin_orders'))

    return render_template('edit_order_status.html', order=order)

@app.route('/customer')
def customer_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('customer_dashboard.html')

@app.route('/')
def index():
    return render_template("index.html")
@app.route('/menu')
def menu():
    menu_items = MenuItem.query.all()
    return render_template('menu.html', menu_items=menu_items)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)