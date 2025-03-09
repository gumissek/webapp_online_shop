import datetime
import os
import smtplib
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, logout_user, current_user, login_required
from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, AddItemForm, PlaceOrderForm

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
    orders = relationship('Order', secondary='orders_items', back_populates='order_items')

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    @classmethod
    def from_dict(cls, dict_data):
        return cls(
            id=dict_data['id'],
            name=dict_data['name'],
            description=dict_data['description'],
            category=dict_data['category'],
            sub_category=dict_data['sub_category'],
            price=dict_data['price'],
            img_link=dict_data['img_link'],
            EAN_code=dict_data['EAN_code'],
            manufacturer_code=dict_data['manufacturer_code'],
            shop_code=dict_data['shop_code']
        )


class Order(database.Model):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    date_order: Mapped[str] = mapped_column(String(250), nullable=False)
    time_order: Mapped[str] = mapped_column(String(250), nullable=False)
    address_country: Mapped[str] = mapped_column(String(250), nullable=False)
    address_city: Mapped[str] = mapped_column(String(250), nullable=False)
    address_street: Mapped[str] = mapped_column(String(250), nullable=False)
    address_home: Mapped[str] = mapped_column(String(250), nullable=False)
    address_zip_code: Mapped[str] = mapped_column(String(250), nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    delivery: Mapped[str] = mapped_column(String(250), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(250), nullable=False)

    # jedno zamowienie ma jednego usera
    user = relationship('User', back_populates='orders')
    user_id: Mapped[int] = mapped_column(Integer, database.ForeignKey('users.id'), nullable=True)

    name: Mapped[str] = mapped_column(String(250))
    surname: Mapped[str] = mapped_column(String(250))
    email: Mapped[str] = mapped_column(String(250))

    # jedno zamowienie ma wiele itemow -> tabela posredniczca
    order_items = relationship('Item', secondary='orders_items', back_populates='orders')


# tabela posredniczaca laczaca wiele zamowienie do wielu itemow
class OrderItems(database.Model):
    __tablename__ = 'orders_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_order: Mapped[int] = mapped_column(Integer, database.ForeignKey('orders.id'))
    id_item: Mapped[int] = mapped_column(Integer, database.ForeignKey('items.id'))


with app.app_context():
    database.create_all()


# FUNCTIONS
def calculate_sum_cart():
    sum_cart = 0
    for item in session['cart']:
        sum_cart += float(item['price'])
    return round(sum_cart, 2)


def get_cart_items():
    # szukam itemow w bazie danych w tabeli Item o tym id co ma item w sesji, inaczej jak zrobie z cart = [Item.from_dict(item) for item in session['cart']] to zrobi mi nowe obiekty i SQL bedzie probowac je dodac do bazy danych ale nie doda ich bo juz takie istnieja i wyjebie blad - 2h w plecki :3
    cart = []
    for item in session['cart']:
        cart.append(database.session.execute(database.select(Item).where(Item.id == item['id'])).scalar())
    return cart


def clear_cart():
    session['cart'] = []
    session.modified = True

def send_mail(to_email:str):
    my_smtp=os.getenv('MY_MAIL_SMTP','smtp.gmail.com')
    my_mail=os.getenv('MY_MAIL','pythonkurskurs@gmail.com')
    my_password=os.getenv('MY_MAIL_PASSWORD','svvbtqswtoxdbchw')
    item_names=[item['name'] for item in session['cart']]
    with smtplib.SMTP(my_smtp,port=587) as connection:
        connection.starttls()
        connection.login(user=my_mail,password=my_password)
        connection.sendmail(from_addr=my_mail,to_addrs=to_email,msg=f'Subject:Order from onlineshop-gumissek, date:{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nOrder with items:\n{item_names}\nhas been placed.')

def set_up_session():
    if 'cart' not in session:
        session['cart'] = []

# ROUTES

# pages
@app.route('/')
def start():
    return redirect(url_for('home_page'))


@app.route('/home', methods=['POST', 'GET'])
def home_page():
    set_up_session()
    return render_template('homepage.html')


@app.route('/shop_page')
def items_page():
    all_items = database.session.execute(database.select(Item)).scalars().all()
    return render_template('shop_page.html', all_items=all_items)


@app.route('/shop_page/show_item', methods=['POST', 'GET'])
def show_item():
    item_id = request.args.get('item_id')
    selected_item = database.session.execute(database.select(Item).where(Item.id == item_id)).scalar()
    if request.method == 'POST':
        for i in range(int(request.form['amount'])):
            # dodaje itemki x razy do sesji
            session['cart'].append(selected_item.to_dict())
            session.modified = True
        return render_template('shop_item_page.html', item=selected_item)
    return render_template('shop_item_page.html', item=selected_item)


@app.route('/cart')
def show_cart():
    return render_template('cart_page.html', cart=get_cart_items(), sum=calculate_sum_cart())


@app.route('/cart/add')
def add_to_cart():
    item_id = request.args.get('item_id')
    selected_item = database.session.execute(database.select(Item).where(Item.id == item_id)).scalar()
    session['cart'].append(selected_item.to_dict())
    session.modified = True
    return redirect(url_for('items_page'))


@app.route('/cart/delete')
def delete_from_cart():
    item_index = int(request.args.get('index'))
    session['cart'].remove(session['cart'][item_index])
    session.modified = True
    return redirect(url_for('show_cart'))


@app.route('/place_order', methods=['POST', 'GET'])
def place_order():
    # jesli zalogowany
    if current_user.is_authenticated:
        order_form = PlaceOrderForm(name=current_user.name, surname=current_user.surname, email=current_user.email)
        if order_form.validate_on_submit():
            cart=get_cart_items()
            new_order = Order(price=calculate_sum_cart(), date_order=datetime.datetime.now().strftime('%Y-%m-%d'),
                              time_order=datetime.datetime.now().strftime('%H:%M:%S'),
                              address_country=request.form['country'].title(),
                              address_city=request.form['city'].title(),
                              address_street=request.form['street'].title(), address_home=request.form['home'],
                              address_zip_code=request.form['zip_code'], status=1,
                              delivery=request.form['delivery'], payment_method=request.form['payment_method'],
                              user_id=current_user.id,
                              name=request.form['name'], surname=request.form['surname'], email=request.form['email'],
                              order_items=[] # pierw robie pusta liste zmowienia potem dodaje osobno kazda rzecz
                              )
            send_mail(request.form['email'])
            database.session.add(new_order)
            database.session.commit()

            # relacja many-to-many w bazie danych nie zachowuje duplikatow wiec trzeba je dodac osobno
            # wiec robie taki trick, pierw robie zamowienie z pusta lista a potem do tabeli posredniczacej dodaje dodaje wpisy
            # gdzie id zamowienia to new_order.id a kazdy item z koszyka to osobny wpis
            for item in cart:
                order_item = OrderItems(id_order=new_order.id, id_item=item.id)
                database.session.add(order_item)

            database.session.commit()
            clear_cart()
            flash(f'The order for logged in {request.form['email']} has been placed')
            return redirect(url_for('home_page'))
        return render_template('place_order.html', cart=get_cart_items(), sum=calculate_sum_cart(), form=order_form)

    # jesli wylogowany bez user_id
    else:

        order_form = PlaceOrderForm()
        if order_form.validate_on_submit():
            cart = get_cart_items()
            new_order = Order(price=calculate_sum_cart(), date_order=datetime.datetime.now().strftime('%Y-%m-%d'),
                              time_order=datetime.datetime.now().strftime('%H:%M:%S'),
                              address_country=request.form['country'].title(),
                              address_city=request.form['city'].title(),
                              address_street=request.form['street'].title(), address_home=request.form['home'],
                              address_zip_code=request.form['zip_code'], status=1,
                              delivery=request.form['delivery'], payment_method=request.form['payment_method'],

                              name=request.form['name'], surname=request.form['surname'], email=request.form['email'],
                              order_items=[]  # pierw robie pusta liste zmowienia potem dodaje osobno kazda rzecz
                              )
            send_mail(request.form['email'])
            database.session.add(new_order)
            database.session.commit()
            # relacja many-to-many w bazie danych nie zachowuje duplikatow wiec trzeba je dodac osobno
            # wiec robie taki trick, pierw robie zamowienie z pusta lista a potem do tabeli posredniczacej dodaje dodaje wpisy
            # gdzie id zamowienia to new_order.id a kazdy item z koszyka to osobny wpis
            for item in cart:
                order_item = OrderItems(id_order=new_order.id, id_item=item.id)
                database.session.add(order_item)

            database.session.commit()
            clear_cart()
            flash(f'The order for logged out {request.form['email']} has been placed')
            return redirect(url_for('home_page'))
        return render_template('place_order.html', cart=get_cart_items(), sum=calculate_sum_cart(), form=order_form)


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


@login_required
@app.route('/logout')
def logout():
    # clear_cart()
    logout_user()
    return redirect(url_for('home_page'))


# DASHBOARD

@app.route('/dashboard')
@permitted_only
def dashboard():
    return render_template('dashboard_main.html')


# DASHBOARD ORDERS


@app.route('/dashboard/all_orders')
@permitted_only
def dashboard_all_orders():
    all_orders = database.session.execute(database.select(Order).order_by(Order.status)).scalars().all()
    order_item=database.session.execute(database.select(OrderItems)).scalars().all()
    all_items = database.session.execute(database.select(Item)).scalars().all()
    #niestety sql utrudnia zycie wiec trzeba zrobic to tak a nie inaczej bo nie wyswietla duplikatow -.-
    return render_template('dashboard_all_orders.html', all_orders=all_orders,order_item=order_item,all_items=all_items)


@app.route('/dashboard/update_status')
@permitted_only
def order_update_status():
    requested_order = database.session.execute(
        database.select(Order).where(Order.id == request.args.get('order_id'))).scalar()
    requested_order.status += 1
    database.session.commit()
    return redirect(url_for('dashboard_all_orders'))


@app.route('/dashboard/orders/edit_orders')
@permitted_only
def dashboard_edit_orders():
    all_orders = database.session.execute(database.select(Order).order_by(Order.status)).scalars().all()
    order_item = database.session.execute(database.select(OrderItems)).scalars().all()
    all_items = database.session.execute(database.select(Item)).scalars().all()
    # niestety sql utrudnia zycie wiec trzeba zrobic to tak a nie inaczej bo nie wyswietla duplikatow -.-
    return render_template('dashboard_edit_orders.html', all_orders=all_orders,order_item=order_item,all_items=all_items)


@app.route('/dashboard/orders/edit_order/<int:order_id>', methods=['POST'])
@permitted_only
def dashboard_edit_order(order_id):
    requested_order = database.session.execute(
        database.select(Order).where(Order.id == order_id)).scalar()

    requested_order.name = request.form[f'name{order_id}']
    requested_order.surname = request.form[f'surname{order_id}']
    requested_order.email = request.form[f'email{order_id}']
    requested_order.address_country = request.form[f'address_country{order_id}']
    requested_order.address_city = request.form[f'address_city{order_id}']
    requested_order.address_street = request.form[f'address_street{order_id}']
    requested_order.address_home = request.form[f'address_home{order_id}']
    requested_order.address_zip_code = request.form[f'address_zip_code{order_id}']
    requested_order.price = request.form[f'price{order_id}']
    requested_order.status = request.form[f'status{order_id}']
    database.session.commit()
    return redirect(url_for('dashboard_edit_orders'))


# DASHBOARD ITEMS
@app.route('/dashboard/items/add_item', methods=['POST', 'GET'])
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
            flash(f'Item {request.form['name']} has been added to database')
            return redirect(url_for('dashboard_add_item'))
        else:
            flash('Item with that EAN code exists in database')
    return render_template('dashboard_add_item.html', form=additem_form)


@app.route('/dashboard/items/all_items')
@permitted_only
def dashboard_all_items():
    all_items = database.session.execute(database.select(Item)).scalars().all()
    return render_template('dashboard_all_items.html', all_items=all_items)


@app.route('/dashboard/items/del_item/<int:item_id>')
@permitted_only
def dashboard_delete_item(item_id):
    requested_item = database.session.execute(database.select(Item).where(Item.id == item_id)).scalar()
    database.session.delete(requested_item)
    database.session.commit()
    flash(f'Item with id: {item_id} has been removed from database')
    return redirect(url_for('dashboard_all_items'))


@app.route('/dashboard/items/edit_items', methods=['POST', 'GET'])
@permitted_only
def dashboard_edit_items():
    all_items = database.session.execute(database.select(Item)).scalars().all()
    return render_template('dashboard_edit_items.html', all_items=all_items)


@app.route('/dashboard/items/edit_item/<int:item_id>', methods=['POST'])
@permitted_only
def dashboard_edit_item(item_id):
    requested_item = database.session.execute(database.select(Item).where(Item.id == item_id)).scalar()
    requested_item.name = request.form[f'name{item_id}']
    requested_item.description = request.form[f'description{item_id}']
    requested_item.category = request.form[f'category{item_id}']
    requested_item.sub_category = request.form[f'sub_category{item_id}']
    requested_item.price = request.form[f'price{item_id}']
    requested_item.img_link = request.form[f'img_link{item_id}']
    requested_item.EAN_code = request.form[f'EAN_code{item_id}']
    requested_item.manufacturer_code = request.form[f'manufacturer_code{item_id}']
    requested_item.shop_code = request.form[f'shop_code{item_id}']
    database.session.commit()
    return redirect(url_for('dashboard_edit_items'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
