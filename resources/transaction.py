from flask_smorest import Blueprint, abort
from flask.views import MethodView

from schema import TransactionSchema, transaction2schema
from model import Transaction, User
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

# from sqlalchemy import or_

blb = Blueprint("transaction", __name__, description="a transaction api")


@blb.route("/transaction")
class SendMoney(MethodView):
    @blb.response(200, transaction2schema)
    @blb.arguments(TransactionSchema)
    @jwt_required()
    def post(self, info):
        current_user = get_jwt_identity()
        sender = User.query.get(current_user)
        receiver = User.query.filter_by(account_number=info["account_number"]).first()
        if not receiver:
            abort(404, message="user with this account number not found")
        if sender.account_balance < info["amount"]:
            abort(400, message="insufficient fund , go hustle")
        receiver.account_balance += info["amount"]
        db.session.commit()
        transact1 = Transaction(
            transaction_type="CRT",
            transaction_amount=info["amount"],
            sender=sender.username,
            user_id=receiver.id,
        )
        db.session.add(transact1)
        db.session.commit()
        sender.account_balance -= info["amount"]
        db.session.commit()
        transact2 = Transaction(
            transaction_type="DBT",
            transaction_amount=info["amount"],
            sender=receiver.username,
            user_id=sender.id,
        )
        db.session.add(transact2)
        db.session.commit()
        return transact2
        # return {"message":"transmission was successful thank you for trusting us.Have a good day"}


@blb.route("/view_transaction")
class GetTransaction(MethodView):
    @blb.response(200, transaction2schema(many=True))
    @jwt_required()
    def get(self):
        transactions = Transaction.query.filter_by(user_id=get_jwt_identity())
        return transactions
