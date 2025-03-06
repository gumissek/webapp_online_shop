import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
load_dotenv()

#app and config
app= Flask(__name__)
app.config['SECRET_KEY']=os.getenv('FLASK_KEY')
bootstrap=Bootstrap5(app)





@app.route('/',methods=['POST','GET'])
def home_page():
    return render_template('homepage.html')


if __name__=='__main__':
    app.run(debug=True,port=5001)