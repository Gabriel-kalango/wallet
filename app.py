from datetime import datetime
from flask import *
from form import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '4f557e8e5eb51bfb7c42'


@app.route('/')
def home():
    return render_template('front.html', date=datetime.utcnow())


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', date=datetime.utcnow(), form=form)


@app.route('/')
def register():
    return render_template('register.html', date=datetime.utcnow())


if __name__ == '__main__':
    app.run(debug=True)
