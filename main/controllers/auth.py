import datetime

import jwt

from main import app, config, db
from main.commons.decorators import validate_request_body
from main.commons.exceptions import Unauthorized, ValueExistedError
from main.libs.controller_helpers import (
    check_hashed_password,
    generate_hashed_password_and_salt,
)
from main.models.user import UserModel
from main.schemas.user import UserSchema


@app.route("/users", methods=["POST"])
@validate_request_body(schema_class=UserSchema)
def register(**kwargs):
    data = kwargs["data"]

    # Check if another user with the same email exists in the database.
    user = UserModel.get_by_email(data["email"])
    if user:
        raise ValueExistedError(error_data={"email": ["Email already exists."]})

    password_hash, password_salt = generate_hashed_password_and_salt(data["password"])
    # Create new user and save to database
    user = UserModel(data["email"], password_hash, password_salt)
    db.session.add(user)
    db.session.commit()

    return UserSchema().dump(user)


@app.route("/tokens", methods=["POST"])
@validate_request_body(schema_class=UserSchema)
def login(**kwargs):
    data = kwargs["data"]

    # Check if another user with the same email exists in the database.
    user = UserModel.get_by_email(data["email"])
    if not user:
        raise Unauthorized(error_message="Email or Password not correct.")

    if not check_hashed_password(
        user.password_hash, user.password_salt, data["password"]
    ):
        raise Unauthorized(error_message="Email or Password not correct.")

    payload = {
        "id": user.id,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(seconds=config.TOKEN_EXPIRATION_SECONDS),
    }

    # Generate a JWT
    access_token = jwt.encode(payload, config.SECRET_KEY)
    return {"access_token": access_token}
