from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
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
