from flask_smorest import Blueprint, abort
from flask.views import MethodView
from passlib.hash import pbkdf2_sha256
from schema import (
    UserSchema,
    UserLoginschema,
    plainUserSchema,
    transactionByUser,
    TokenReset,
)
from model import User
from extensions import db, mail
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from blocklist import BLOCKLIST
from sqlalchemy import or_
from datetime import timedelta
from flask_mail import Message
import random

blb = Blueprint("user", __name__, description="a user api")

reset_token = random.randint(0000, 9999)


@blb.route("/user/register")
class UserRegister(MethodView):
    @blb.arguments(plainUserSchema)
    def post(self, user_data):
        if User.query.filter(
            or_(
                User.username == user_data["username"], User.email == user_data["email"]
            )
        ).first():
            abort(409, message="A user with that username or email already exists.")

        user = User(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            username=user_data["username"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
            phone_number=user_data["phone_number"],
            account_number=int(user_data["phone_number"]),
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "user created successfully"}


# this is an endpoint that uses the refresh token to generate a new access token
@blb.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(
            identity=current_user, expires_delta=timedelta(hours=2)
        )

        return {"access_token": new_token}


@blb.route("/user/login")
class UserLogin(MethodView):
    @blb.arguments(UserLoginschema)
    def post(self, user_data):
        user = User.query.filter(User.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(fresh=True, identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}
        abort(
            404,
            message="user not found , check if email /username or password is correct",
        )


@blb.route("/user/logout")
class UserLogin(MethodView):
    # the jwt_required indicates that the access token will be required to log out
    @jwt_required()
    def post(self):
        # get the current user's token
        jti = get_jwt()["jti"]
        # send the token to the BLOCKLIST set in the blocklist.py file
        # this will revoke the token. A new access token will be created for you when you log in again
        BLOCKLIST.add(jti)
        # return this message for a successful logout
        return {"message": "Successfully logged out"}


@blb.route("/users")
class GetAllUsers(MethodView):
    @jwt_required()
    @blb.response(200, UserSchema(many=True))
    def get(self):
        if User.query.get(get_jwt_identity()).is_admin:
            users = User.query.all()
            return users
        abort(401, "Unauthorized")


@blb.route("/view_account")
class viewYourAccount(MethodView):
    @blb.response(200, UserSchema)
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        return current_user


@blb.route("/user/<int:user_id>")
class GetSpecificUser(MethodView):
    @jwt_required()
    @blb.response(200, UserSchema)
    def get(self, user_id):
        if User.query.get(get_jwt_identity()).is_admin:
            user = User.query.get_or_404(user_id)
            return user
        abort(401, "Unauthorized")

    @jwt_required()
    def delete(self, user_id):
        if User.query.get(get_jwt_identity()).is_admin:
            if user_id == get_jwt_identity():
                abort(401, message="Cannot delete yourself")
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            return {"message": "user deleted"}
        abort(401, "Unauthorized")

    @jwt_required()
    def patch(self, user_id):
        if User.query.get(get_jwt_identity()).is_admin:
            user = User.query.get_or_404(user_id)
            if user.id == get_jwt_identity():
                abort(401, "Unauthorized")
            if user.is_admin == 1:
                user.is_admin = 0
                db.session.commit()
                return {"message": "user demoted from being an admin"}
            user.is_admin = 1
            db.session.commit()
            return {"message": "user promoted to admin"}
        abort(401, "Unauthorized")


@blb.route("/user/transaction")
class GetUserTransaction(MethodView):
    @jwt_required()
    @blb.response(200, transactionByUser(many=True))
    def get(self):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        return current_user.transacts


@blb.route("/forgot_password/<int:user_id>/<string:username>")
class passwordForgot(MethodView):
    def post(self, user_id, username):
        try:
            user_exist = User.query.get_or_404(user_id)
            if user_exist:
                if user_exist.username == username:
                    msg = Message(
                        "Reset Token",
                        sender=user_exist.email,
                        recipients=[
                            user_exist.email
                        ],
                        )
                    msg.body = f"Your reset token is: {reset_token}"
                    mail.send(msg)
                    return {"message": "Sent successfully"}
                abort(401, message="Credentials does not match")
            abort(404, message="User not found")
        except:
            abort(417, message="Check your data connection/credentials")


@blb.route("/reset_password/<int:user_id>/<string:username>")
class passwordReset(MethodView):
    @blb.arguments(TokenReset)
    def post(self, data, username, user_id):
        res_token = data["res_token"]
        password = data["password"]
        confirm_password = data["confirm_password"]

        if res_token != reset_token:
            abort(401, message="Invalid token")
        if confirm_password != password:
            abort(401, message="Password does not match")

        user = User.query.filter_by(username=username).first()
        if user.id != user_id:
            abort(401, message="Credentials does not match")
        user.password = pbkdf2_sha256.hash(password)
        db.session.commit()
        return {"message": "Password has been reset, you can now login"}
