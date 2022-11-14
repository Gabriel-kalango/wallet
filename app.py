from datetime import datetime
from flask import *
from form import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '4f557e8e5eb51bfb7c42'


@app.route('/')
def front_page():
    return render_template('front.html', date=datetime.utcnow())


@app.route('/account/')
def account():
    return render_template('account.html', date=datetime.utcnow())


@app.route('/home/')
def home():
    return render_template('home.html', date=datetime.utcnow())


@app.route('/pay/')
def pay():
    form = SendMoneyForm()
    return render_template('pay.html', date=datetime.utcnow(), form=form)


@app.route('/login/')
def login():
    form = LoginForm()
    return render_template('login.html', date=datetime.utcnow(), form=form)


@app.route('/register/')
def register():
    return render_template('register.html', date=datetime.utcnow())


if __name__ == '__main__':
    app.run(debug=True)
