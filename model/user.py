from extensions import db


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(70), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    account_number = db.Column(db.Integer, unique=True, nullable=False)
    account_balance = db.Column(db.Integer, default=20000)
    is_admin = db.Column(db.Boolean, default=False)
    transacts = db.relationship("Transaction",cascade="all, delete", back_populates="users", lazy=True)
