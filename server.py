import os
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from forms import RegisterForm, LoginForm

load_dotenv()

# app and config
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY', '1234')
bootstrap = Bootstrap5(app)


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

    #jeden user ma wiele zamowien
    orders = relationship('Order', back_populates='user')
class Item(database.Model):
    __tablename__ = 'items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(String(5000), nullable=False)
    category: Mapped[str] = mapped_column(String(250), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    img_link: Mapped[str] = mapped_column(String(250), nullable=False)
    EAN_code: Mapped[int] = mapped_column(Integer, nullable=False)
    manufacturer_code: Mapped[str] = mapped_column(String(250), nullable=False)
    shop_code: Mapped[int] = mapped_column(Integer, nullable=False)

    #jeden item nalezy do wielu zamowien -> tabela posredniczca
    orders = relationship('Order',secondary='orders_items',back_populates='items')

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

    #jedno zamowienie ma jednego usera
    user = relationship('User',back_populates='orders')
    user_id : Mapped[int] = mapped_column(Integer,database.ForeignKey('users.id'))

    #jedno zamowienie ma wiele itemow -> tabela posredniczca
    items = relationship('Item',secondary='orders_items',back_populates='orders')

#tabela posredniczaca laczaca wiele zamowienie do wielu itemow
class OrderItems(database.Model):
    __tablename__ = 'orders_items'
    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_order : Mapped[int]  = mapped_column(Integer,database.ForeignKey('orders.id'))
    id_item : Mapped[int] = mapped_column(Integer,database.ForeignKey('items.id'))

with app.app_context():
    database.create_all()

@app.route('/', methods=['POST', 'GET'])
def home_page():
    return render_template('homepage.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    register_form = RegisterForm()
    return render_template('register.html', register_form=register_form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    return render_template('login.html', login_form=login_form)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
