import os
from flask import jsonify
from resources.transaction import blb as transactionblueprint
from resources.user import blb as Userblueprint
from extensions import db, app, api, jwt, mail
from flask_migrate import Migrate
from datetime import timedelta
from blocklist import BLOCKLIST

# import model


def create_app(db_url=None):

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "WALLET REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///wallet.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "442830361741531832645899122519391798179"

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USERNAME"] = "atmme1992@gmail.com"
    app.config["MAIL_PASSWORD"] = "dvogogdoinarpugn"
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True

    db.init_app(app)
    migrate = Migrate(app, db)
    api.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    # @jwt.token_in_blocklist_loader
    # def check_if_token_in_blocklist(jwt_header, jwt_payload):
    #     return  BlockliskModel.query.filter_by(jwt=jwt_payload["jti"] ).first()

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    @jwt.additional_claims_loader
    def add_additional_claims(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    # this is going to check the BLOCKLIST set if the token you're trying to use exist in the set
    # if the token is present in the set, it will return a 'token revoked' message
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    # with app.app_context():
    #     #     db.create_all()
    api.register_blueprint(transactionblueprint)

    api.register_blueprint(Userblueprint)

    return app
