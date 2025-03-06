import os
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
from forms import RegisterForm, LoginForm

load_dotenv()

# app and config
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')
bootstrap = Bootstrap5(app)

#data base


@app.route('/', methods=['POST', 'GET'])
def home_page():
    return render_template('homepage.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    register_form=RegisterForm()
    return render_template('register.html',register_form=register_form)

@app.route('/login',methods=['POST','GET'])
def login():
    login_form=LoginForm()
    return render_template('login.html', login_form=login_form)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
