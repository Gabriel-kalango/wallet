from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TelField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SendMoneyForm(FlaskForm):
    username = StringField('Wallet Username', validators=[DataRequired(), Length(min=2)])
    amount = IntegerField('Amount', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Send')


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = TelField('Phone Number', validators=[DataRequired(), Length(max=11)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
