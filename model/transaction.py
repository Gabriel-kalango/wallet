from db import db
import datetime
class Transaction(db.Model):
    __tablename__="transaction"
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    transaction_amount = db.Column(db.Integer, nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    users=db.relationship("User",back_populates="transacts")