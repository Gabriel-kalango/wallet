# import the dependencies
from flask_smorest import Blueprint, abort
from flask.views import MethodView

from schema import TransactionSchema, transaction2schema
from model import Transaction, User
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

# from sqlalchemy import or_

blb = Blueprint("transaction", __name__, description="a transaction api")


# the route to send funds to another user
@blb.route("/transaction")
class SendMoney(MethodView):
    # the schema for the response
    @blb.response(200, transaction2schema)
    # the schema for the arguments to be passed
    @blb.arguments(TransactionSchema)
    # a valid access token is required
    @jwt_required()
    def post(self, info):
        # get the current user's id
        current_user = get_jwt_identity()
        # use the current user's id to query the database for the current user
        sender = User.query.get(current_user)
        # use the account number from the argument to fetch the receiver's details
        receiver = User.query.filter_by(account_number=info["account_number"]).first()
        # if there is no receiver with such account number, abort the operation with that 404 'not found' status code
        if not receiver:
            abort(404, message="user with this account number not found")
        # if the sender's account balance is lower than the amount to be sent, abort the operation with a message of 'insufficient fund'
        if sender.account_balance < info["amount"]:
            abort(400, message="insufficient fund")
        # get the receiver's account balance and add the amount sent to it
        receiver.account_balance += info["amount"]
        # commit your changes
        db.session.commit()
        # send the statement of credit transaction to the database
        transact1 = Transaction(
            transaction_type="CRT",
            transaction_amount=info["amount"],
            sender=sender.username,
            user_id=receiver.id,
        )
        # add and commit your changes
        db.session.add(transact1)
        db.session.commit()
        # get the sender's account balance, deduct the money sent from it
        sender.account_balance -= info["amount"]
        # commit your changes to the database
        db.session.commit()
        # send the statement of debit transaction to the database
        transact2 = Transaction(
            transaction_type="DBT",
            transaction_amount=info["amount"],
            sender=receiver.username,
            user_id=sender.id,
        )
        # add and commit your changes to the database
        db.session.add(transact2)
        db.session.commit()
        # return the debit transaction to the user
        return transact2
        # return {"message":"transmission was successful thank you for trusting us.Have a good day"}


# route to view the transactions made by the user
@blb.route("/view_transaction")
class GetTransaction(MethodView):
    # the response schema
    @blb.response(200, transaction2schema(many=True))
    # a valid jwt token is required
    @jwt_required()
    def get(self):
        # use the current user's id to get both debit and credit transactions from the database
        transactions = Transaction.query.filter_by(user_id=get_jwt_identity())
        # return the transactions
        return transactions
