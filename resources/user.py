# import all dependencies
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

# create an instance of the Blueprint imported from flask_smorest
blb = Blueprint("user", __name__, description="a user api")

# generate a random token for resetting the password
reset_token = random.randint(0000, 9999)


# use the instance to create a route
# this is the route to register a user
@blb.route("/user/register")
class UserRegister(MethodView):
    # the argument schema, the input for this registration should have the fields from the schema
    # go to the schema.py file and see the fields in the plainUserSchema
    @blb.arguments(plainUserSchema)
    def post(self, user_data):
        # query the database to check if the username and email already exist in the database
        if User.query.filter(
            or_(
                User.username == user_data["username"], User.email == user_data["email"]
            )
        ).first():
            # if any of those details already exist in the database, abort the registration process with
            # a status code of 409
            abort(409, message="A user with that username or email already exists.")

        # if the email and username does not exist in the database, then add and commit the user into the database
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
        # after a successful registration, return this message to the user
        return {"message": "user created successfully"}


# this is an endpoint that uses the refresh token to generate a new access token
@blb.route("/refresh")
class TokenRefresh(MethodView):
    # jwt_required simply means a token will be required to access this route
    # for you to generate a token, you need too login first
    @jwt_required(refresh=True)
    def post(self):
        # get the current user's id, use it as an identity to create a new access token using the refresh token
        current_user = get_jwt_identity()
        new_token = create_access_token(
            identity=current_user, expires_delta=timedelta(hours=2)
        )

        # return the new generated token
        return {"access_token": new_token}


# the login route
@blb.route("/user/login")
class UserLogin(MethodView):
    # the data to be provided during the login process should follow this schema's convention
    @blb.arguments(UserLoginschema)
    def post(self, user_data):
        # query the database to check if the username exist
        user = User.query.filter(User.username == user_data["username"]).first()

        # if the username exist, verify if the password matches
        # if the password is valid, create an access token along with s refresh token
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(fresh=True, identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            # return the created tokens
            return {"access_token": access_token, "refresh_token": refresh_token}
        # if the username and the password are invalid, abort with a status code of 404
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


# route to get all users in the database
@blb.route("/users")
class GetAllUsers(MethodView):
    # a valid jwt token is required to access this endpoint
    @jwt_required()
    # in this endpoint, what we need is a response and not to enter some datas
    # the response should be serialized using the fields from this UserSchema
    # "many=True" :- return the response in a list
    @blb.response(200, UserSchema(many=True))
    def get(self):
        # use the current user's id (i.e get_jwt_identity()) to check if the current user is an admin
        if User.query.get(get_jwt_identity()).is_admin:
            # if the current user is an admin, then query the database for all the users available
            users = User.query.all()
            # return the users queried in a list
            return users
        # if the current user is not an admin, this operation cannot be performed
        abort(401, "Unauthorized")


# the route for accessing your account details
@blb.route("/view_account")
class viewYourAccount(MethodView):
    # the response schema
    @blb.response(200, UserSchema)
    # a valid token is required to access this route
    @jwt_required()
    def get(self):
        # use the current user's id to fetch from the database the user's details
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        # return to the user the details fetched
        return current_user


# the route to perform an operation on a specific user
@blb.route("/user/<int:user_id>")
class GetSpecificUser(MethodView):
    # a valid access token is required for this endpoint
    @jwt_required()
    # the response schema with a success code, 200
    @blb.response(200, UserSchema)
    def get(self, user_id):
        # check if the current user is an admin
        # if yes, then go ahead with the operation
        if User.query.get(get_jwt_identity()).is_admin:
            user = User.query.get_or_404(user_id)
            return user
        # if not, abort the operation
        abort(401, "Unauthorized")

    @jwt_required()
    def delete(self, user_id):
        # check if the current user is an admin
        # if yes, go ahead with the operation
        if User.query.get(get_jwt_identity()).is_admin:
            # check if the admin is trying to delete his/her own account
            # if yes, abort the operation
            if user_id == get_jwt_identity():
                abort(401, message="Cannot delete yourself")
            # if the current user is an admin and not trying to delete his/her own account
            # then go ahead and delete the user's account
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            return {"message": "user deleted"}
        # if the current user is not an admin, abort the operation
        abort(401, "Unauthorized")

    # valid token is required
    @jwt_required()
    # update method
    # update the admin status of a user
    def patch(self, user_id):
        # this operation can also be performed by an admin
        if User.query.get(get_jwt_identity()).is_admin:
            user = User.query.get_or_404(user_id)
            # the admin can't change the admin status of his/her own account
            if user.id == get_jwt_identity():
                abort(401, "Unauthorized")
            # if the user is already an admin, demote the user
            if user.is_admin == 1:
                user.is_admin = 0
                db.session.commit()
                return {"message": "user demoted from being an admin"}
            # if the user is not an admin, promote the user
            user.is_admin = 1
            db.session.commit()
            return {"message": "user promoted to admin"}
        # a non admin user cannot access this endpoint
        abort(401, "Unauthorized")


# route for users to get all transaction made by them
@blb.route("/user/transaction")
class GetUserTransaction(MethodView):
    # a valid token is required
    @jwt_required()
    @blb.response(200, transactionByUser(many=True))
    def get(self):
        # get the user from the database using the current user's id
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        # return the transactions the user has made ( statement of account )
        return current_user.transacts


# route to set a get the pin to create a new password
# the user's id and username is needed in this route
@blb.route("/forgot_password/<int:user_id>/<string:username>")
class passwordForgot(MethodView):
    def post(self, user_id, username):
        try:
            # get the user from the database using the user's id
            user_exist = User.query.get_or_404(user_id)
            # if the user exist
            if user_exist:
                # check the username in the route and the username associated with the id
                # if the data matches, then continue the operation
                if user_exist.username == username:
                    # set the title of the email with the recipient
                    # in this case, the recipient is the user, the mail will be sent to the user's email
                    msg = Message(
                        "Reset Token",
                        sender=user_exist.email,
                        recipients=[
                            user_exist.email
                        ],
                        )
                    # the body of the mail
                    msg.body = f"Your reset token is: {reset_token}"
                    # the imported 'mail' is used to send the message to the user
                    mail.send(msg)
                    return {"message": "Sent successfully"}
                # if the user's id and username dies not match, abort the operation
                abort(401, message="Credentials does not match")
            # if the user's id is not a valid one, abort
            abort(404, message="User not found")
        # if an error is encountered, run this block
        except:
            abort(417, message="Check your data connection/credentials")


# you get to provide the pin sent to your mail as an argument in this route
@blb.route("/reset_password/<int:user_id>/<string:username>")
class passwordReset(MethodView):
    @blb.arguments(TokenReset)
    def post(self, data, username, user_id):
        # provide the reset token, password and confirm password
        res_token = data["res_token"]
        password = data["password"]
        confirm_password = data["confirm_password"]

        # if the reset token is not same with the one sent to you, abort the operation
        if res_token != reset_token:
            abort(401, message="Invalid token")
        # if the password and confirm password is different, abort the operation
        if confirm_password != password:
            abort(401, message="Password does not match")
        # if the reset token is valid, the password fields matches, then continue the operation
        # fetch the user using the user's username
        user = User.query.filter_by(username=username).first()
        # if the id passed is different from the one from the database, abort the operation
        if user.id != user_id:
            abort(401, message="Credentials does not match")
        # if everything is okay, hash the password and update the password column in the database
        user.password = pbkdf2_sha256.hash(password)
        # commit your changes
        db.session.commit()
        # return a successful update message
        return {"message": "Password has been reset, you can now login"}
