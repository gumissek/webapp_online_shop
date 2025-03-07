import os
from functools import wraps

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, logout_user, current_user
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from forms import RegisterForm, LoginForm, AddItemForm

load_dotenv()

# app and config
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY', '1234')
bootstrap = Bootstrap5(app)

# login manager - LOGIN
loginmanager = LoginManager()
loginmanager.init_app(app)


# current_user
@loginmanager.user_loader
def load_user(user_id):
    logged_user = database.session.execute(database.select(User).where(User.id == user_id)).scalar()
    if logged_user:
        return logged_user


# decorators
def permitted_only(function):
    @wraps(function)
    def wrapped_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.permission_level > 1:
            return function(*args, **kwargs)
        else:
            return render_template('not_permitted.html')

    return wrapped_function


# database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///backup_shop_online.db')
database = SQLAlchemy(model_class=Base)
database.init_app(app)


class User(UserMixin, database.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    surname: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    permission_level: Mapped[str] = mapped_column(Integer, nullable=False)

    # jeden user ma wiele zamowien
    orders = relationship('Order', back_populates='user')


class Item(database.Model):
    __tablename__ = 'items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(String(5000), nullable=False)
    category: Mapped[str] = mapped_column(String(250), nullable=False)
    sub_category: Mapped[str] = mapped_column(String(250), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    img_link: Mapped[str] = mapped_column(String(250), nullable=False)
    EAN_code: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    manufacturer_code: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    shop_code: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    # jeden item nalezy do wielu zamowien -> tabela posredniczca
    orders = relationship('Order', secondary='orders_items', back_populates='items')


class Order(database.Model):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    date_order: Mapped[str] = mapped_column(String(250), nullable=False)
    address_country: Mapped[str] = mapped_column(String(250), nullable=False)
    address_city: Mapped[str] = mapped_column(String(250), nullable=False)
    address_street: Mapped[str] = mapped_column(String(250), nullable=False)
    address_home: Mapped[str] = mapped_column(String(250), nullable=False)
    address_zip_code: Mapped[str] = mapped_column(String(250), nullable=False)
    status: Mapped[str] = mapped_column(String(250), nullable=False)

    # jedno zamowienie ma jednego usera
    user = relationship('User', back_populates='orders')
    user_id: Mapped[int] = mapped_column(Integer, database.ForeignKey('users.id'))

    # jedno zamowienie ma wiele itemow -> tabela posredniczca
    items = relationship('Item', secondary='orders_items', back_populates='orders')


# tabela posredniczaca laczaca wiele zamowienie do wielu itemow
class OrderItems(database.Model):
    __tablename__ = 'orders_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_order: Mapped[int] = mapped_column(Integer, database.ForeignKey('orders.id'))
    id_item: Mapped[int] = mapped_column(Integer, database.ForeignKey('items.id'))


with app.app_context():
    database.create_all()


@app.route('/', methods=['POST', 'GET'])
def home_page():
    return render_template('homepage.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
        retype_password = request.form['retype_password']
        if password == retype_password:
            user = database.session.execute(database.select(User).where(User.email == email)).scalar()
            if not user:
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=10)
                new_user = User(name=name, surname=surname, email=email, password=hashed_password, permission_level=1)
                database.session.add(new_user)
                database.session.commit()
                login_user(new_user)
                return redirect(url_for('home_page'))
            else:
                flash('User with that email already exists, try login.')
                return redirect(url_for('login'))
        else:
            flash('Passwords dont match.')

    return render_template('register.html', register_form=register_form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = request.form['email']

        if database.session.execute(database.select(User).where(User.email == email)).scalar():
            user = database.session.execute(database.select(User).where(User.email == email)).scalar()
            password = request.form['password']
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home_page'))
            else:
                flash('Incorrect password.')
                return redirect(url_for('login'))

        else:
            flash('There is not user with that email. Register instead.')
            return redirect(url_for('register'))

    return render_template('login.html', login_form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))


@app.route('/dashboard')
@permitted_only
def dashboard():
    return render_template('dashboard_main.html')


@app.route('/dashboard/add_item', methods=['POST', 'GET'])
@permitted_only
def dashboard_add_item():
    additem_form = AddItemForm()
    if additem_form.validate_on_submit():
        ean_code = request.form['EAN_code']
        if not database.session.execute(database.select(Item).where(Item.EAN_code == ean_code)).scalar():
            new_item = Item(name=request.form['name'], description=request.form['description'],
                            category=request.form['category'], sub_category=request.form['sub_category'],
                            price=request.form['price'], img_link=request.form['img_link'], EAN_code=ean_code,
                            manufacturer_code=request.form['manufacturer_code'], shop_code=request.form['shop_code'])
            database.session.add(new_item)
            database.session.commit()
            flash('Item has been added to database')
            return redirect(url_for('dashboard'))
        else:
            flash('Item with that EAN code exists in database')
    return render_template('dashboard_add_item.html', form=additem_form)


@app.route('/dashboard/all_items')
@permitted_only
def dashboard_all_items():
    all_items = database.session.execute(database.select(Item)).scalars().all()
    return render_template('dashboard_all_items.html', all_items=all_items)


@app.route('/dashboard/del_item/<int:item_id>')
@permitted_only
def dashboard_delete_item(item_id):
    requested_item = database.session.execute(database.select(Item).where(Item.id == item_id)).scalar()
    database.session.delete(requested_item)
    database.session.commit()
    flash(f'Item with id: {item_id} has been removed from database')
    return redirect(url_for('dashboard_all_items'))

@app.route('/dashboard/edit_items',methods=['POST','GET'])
def dashboard_edit_items():
    all_items = database.session.execute(database.select(Item)).scalars().all()
    return render_template('dashboard_edit_items.html',all_items=all_items)

@app.route('/dashboard/edit_item/<int:item_id>',methods=['POST'])
def edit_item(item_id):
    requested_item = database.session.execute(database.select(Item).where(Item.id == item_id)).scalar()
    requested_item.name = request.form[f'name{item_id}']
    requested_item.description=request.form[f'description{item_id}']
    requested_item.category=request.form[f'category{item_id}']
    requested_item.sub_category=request.form[f'sub_category{item_id}']
    requested_item.price = request.form[f'price{item_id}']
    requested_item.img_link = request.form[f'img_link{item_id}']
    requested_item.EAN_code = request.form[f'EAN_code{item_id}']
    requested_item.manufacturer_code = request.form[f'manufacturer_code{item_id}']
    requested_item.shop_code=request.form[f'shop_code{item_id}']
    database.session.commit()
    return redirect(url_for('dashboard_edit_items'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
