from flask_smorest import Blueprint,abort
from flask.views import MethodView

from schema import TransactionSchema,transaction2schema
from model import Transaction,User
from db import db
from flask_jwt_extended import jwt_required, create_access_token,create_refresh_token,get_jwt,get_jwt_identity
from sqlalchemy import or_
blb=Blueprint("transaction",__name__,description="a transaction api")
@blb.route("/transaction")
class SendMoney(MethodView):
    @blb.response(200,transaction2schema)
    @blb.arguments(TransactionSchema)
    @jwt_required()
    def post(self,info):
        current_user=get_jwt_identity()
        senderr=User.query.get(current_user)
        reciever=User.query.filter(User.account_number==info["account_number"]).first()
        if not reciever:
            abort(404, message="user with this account number not found")
        if senderr.account_balance<info["amount"]:
            abort(400,message="insufficent fund , go hustle")
        reciever.account_balance+=info["amount"]
        db.session.commit()
        transact1=Transaction(transaction_type="CRT",transaction_amount=info["amount"],sender=senderr.username,user_id=reciever.id)
        db.session.add(transact1)
        db.session.commit()
        senderr.account_balance-=info["amount"]
        db.session.commit()
        transact2=Transaction(transaction_type="   DBT",transaction_amount=info["amount"],sender=reciever.username,user_id=senderr.id)
        db.session.add(transact2)
        db.session.commit()
        return transact1
        # return {"message":"transmission was successful thank you for trusting us.Have a good day"}