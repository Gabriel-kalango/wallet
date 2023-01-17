from flask_smorest import Blueprint,abort
from flask.views import MethodView
from passlib.hash import pbkdf2_sha256
from schema import UserSchema,UserLoginschema
from model import User
from db import db
from flask_jwt_extended import create_access_token,create_refresh_token,get_jwt,get_jwt_identity
from sqlalchemy import or_
blb=Blueprint("user",__name__,description="a user api")
@blb.route("/user/register")
class UserRegister(MethodView):
    @blb.arguments(UserSchema)
    def post(self,user_data):
        if User.query.filter(
            or_(
                User.username == user_data["username"],
                User.email == user_data["email"]
            )
        ).first():
            abort(409, message="A user with that username or email already exists.")

        user=User(first_name=user_data["first_name"],last_name=user_data["last_name"],username=user_data["username"],email=user_data["email"],password=pbkdf2_sha256.hash(user_data["password"]),phone_number=user_data["phone_number"],account_number=user_data["account_number"])
        db.session.add(user)
        db.session.commit()
        return {"message":"user created successfully"}

@blb.route("/user/login")
class UserLogin(MethodView):
    @blb.arguments(UserLoginschema)
    def post(self,user_data):
        user=User.query.filter(or_(User.username==user_data["username"],User.email==user_data["email"])).first()
        
        if (user and pbkdf2_sha256.verify(user_data["password"],user.password)):
            access_token=create_access_token(fresh=True,identity=user.id)
            refresh_token=create_refresh_token(identity=user.id)
            return {"access_token":access_token,"refresh_token":refresh_token}
        abort(404, message="user not found , check if email /username or password is correct")


