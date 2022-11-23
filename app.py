from datetime import datetime
from flask import *
from form import *
from flask_mail import Message, Mail
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required, UserMixin, LoginManager
import os

base_dir = os.path.dirname(os.path.realpath(__file__))

# Instantiate the Flask imported from flask
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'wallet.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = '4f557e8e5eb51bfb7c42'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'atmme1992@gmail.com'
app.config['MAIL_PASSWORD'] = 'dvogogdoinarpugn'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


db = SQLAlchemy(app)
# Initialize the database
db.init_app(app)

login_manager = LoginManager(app)


# creating the User table in the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(70), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    account_number = db.Column(db.Integer, unique=True, nullable=False)
    account_balance = db.Column(db.Integer, default=20000)
    transacts = db.relationship('Transaction', backref='author', lazy=True)

    # Define a representation with two attribute 'username' and 'email'
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


# creating the Transaction table in the database
class Transaction(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    transaction_amount = db.Column(db.Integer, nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# The decorator that loads the user using the user's id
@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


# If the user isn't logged in and tries to access a login required route, this decorator allows the page to
# redirect page to the login
@login_manager.unauthorized_handler
def unauthorized_handler():
    flash('Login to access this page', category='info')
    return redirect(url_for('login'))


@app.route('/')
def front_page():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('front.html', date=datetime.utcnow())


@app.route('/account/')
def account():
    return render_template('account.html', date=datetime.utcnow())


@app.route('/home/')
@login_required
def home():
    balance = f'{current_user.account_balance:,}'
    return render_template('home.html', date=datetime.utcnow(), user=current_user, balance=balance)


@app.route('/pay/', methods=['GET', 'POST'])
@login_required
def pay():
    form = SendMoneyForm()
    if request.method == 'POST':
        account_number = form.account_number.data
        amount = form.amount.data
        user1 = User.query.filter_by(account_number=account_number).first()
        if not user1:
            flash('Invalid account number', 'danger')
            return redirect(url_for('pay'))
        if current_user.account_balance < amount:
            flash('Insufficient Funds', 'danger')
            return redirect(url_for('pay'))
        user1.account_balance += amount
        db.session.commit()
        transact1 = Transaction(transaction_type='CRT', transaction_amount=amount, sender=current_user.username, user_id=user1.id)
        db.session.add(transact1)
        db.session.commit()

        current_user.account_balance -= amount
        db.session.commit()
        transact2 = Transaction(transaction_type='DBT', transaction_amount=amount, sender=user1.username, user_id=current_user.id)
        db.session.add(transact2)
        db.session.commit()
        flash(f'{amount} Naira has been sent to {user1.username}', 'success')
        return redirect(url_for('pay'))
    return render_template('pay.html', date=datetime.utcnow(), form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    # If the logged-in user is trying to access the login url, redirects the user to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # Assign the LoginForm created in the form.py file to a variable 'form'
    form = LoginForm()
    # If the form gets validated on submit
    if form.validate_on_submit():
        # Query the User model and assign the queried data to the variable 'user'
        user = User.query.filter_by(email=form.email.data.lower()).first()
        # Check if the user exist in the database and if the inputted password is same with the one attached to the user on the database
        if user and check_password_hash(user.password, form.password.data):
            # If the check passed, login the user and flash a message to the user when redirected to the homepage
            login_user(user, remember=True)
            flash('Login Successful', 'success')
            return redirect(url_for('home', id=user.id, user=current_user))
        else:
            # If the check failed, flash a message to the user while still on the same page
            flash('Check your Email / Password', 'danger')
            return redirect(url_for('login'))
    # This for a get request, if u click on the link that leads to the login page, this return statement get called upon
    return render_template('login.html', date=datetime.utcnow(), form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    # If the logged-in user is trying to access the login url, redirects the user to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # Assign the RegistrationForm created in the form.py file to a variable 'form'
    form = RegistrationForm()
    # If the request is a post request and the form doesn't get validated, redirect the user to that same page
    if request.method == 'POST':
        if not form.validate_on_submit():
            return redirect(url_for('register'))
        # If the form gets validated on submit
        else:
            # Check if the username already exist
            user = User.query.filter_by(username=form.username.data.lower()).first()
            # if the username exist
            if user:
                # Flash this message to the user and redirect the user to that same page
                flash('User with this username already exist', category='danger')
                return redirect(url_for('register'))

            # Check if email exist
            existing_email = User.query.filter_by(email=form.email.data.lower()).first()
            # if the email exist
            if existing_email:
                # Flash this message to the user and redirect the user to that same page
                flash('User with this email already exist', category='danger')
                return redirect(url_for('register'))

            # Check if phone number exist
            existing_phone = User.query.filter_by(email=form.phone_number.data).first()
            # if the phone number exist
            if existing_phone:
                # Flash this message to the user and redirect the user to that same page
                flash('User with this phone number already exist', category='danger')
                return redirect(url_for('register'))

            first_name = form.first_name.data.lower()
            last_name = form.last_name.data.lower()
            username = form.username.data.lower()
            email = form.email.data.lower()
            phone_number = str(form.phone_number.data)
            account_number = int(str(phone_number)[1:])
            password_hash = generate_password_hash(form.password.data)

            # to check if the password is the mixture of uppercase, lowercase and a number at least
            letters = set(form.password.data)
            mixed = any(letter.islower() for letter in letters) and any(letter.isupper() for letter in letters) and any(letter.isdigit() for letter in letters)
            if not mixed:
                flash('Password should contain at least an uppercase, lowercase and a number', 'danger')
                return redirect(url_for('register'))

            # variable 'new_user'
            new_user = User(first_name=first_name, last_name=last_name, username=username, phone_number=phone_number, email=email, account_number=account_number, password=password_hash)
            # Add the 'new_user'
            db.session.add(new_user)
            db.session.commit()
            flash('Registration Successful, You can now Login', category='success')
            return redirect(url_for('login'))

    return render_template('register.html', date=datetime.utcnow(), form=form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You\'ve been logged out successfully', 'success')
    return redirect(url_for('front_page'))


@app.route('/send/')
@login_required
def display_profile():
    return render_template('display-profile.html', date=datetime.utcnow())


@app.route('/contact/', methods=['GET', 'POST'])
@login_required
def contact():
    form = ContactForm()
    if request.method == "POST":
        if not form.name.data and not form.email.data and not form.message.data:
            flash('All fields are required', 'danger')
            return redirect(url_for('contact'))
        name = form.name.data.title()
        email = form.email.data.lower()
        message = form.message.data.title()
        msg = Message('EasyTransact: from ' + name, sender=email, recipients=['atmme1992@gmail.com', 'greatsoma2019@gmail.com', 'vnoah410@gmail.com'])
        msg.body = f'{message}\nMy email address is: {email}'
        mail.send(msg)
        flash('Message Sent', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form, date=datetime.utcnow())


if __name__ == '__main__':
    app.run(debug=True)
