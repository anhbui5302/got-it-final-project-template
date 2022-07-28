from importlib import import_module

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .commons.error_handlers import register_error_handlers
from .config import config

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

CORS(app)


# Decorated function will run before the first request to the app
# @app.before_first_request
# def create_tables():
#     from main.models.user import UserModel
#     from main.models.item import ItemModel
#     from main.models.category import CategoryModel
#     db.drop_all()  # Drop all tables
#     db.create_all()  # Create all tables
#     # Test data
#     user_infos = [
#         ("user@abc.com", "Password123"),
#         ("me@example.com", "Password123"),
#     ]
#
#     category_infos = [
#         (1, "category1"),
#         (1, "category2"),
#         (2, "category3"),
#         (2, "category4")
#     ]
#
#     item_infos = [
#         (1, "item1", "description1", 1),
#         (2, "item2", "description1", 2),
#         (1, "item3", "description1", 3),
#         (2, "item4", "description1", 4),
#         (1, "item5", "description1", 1),
#         (2, "item6", "description1", 2)
#     ]
#     for info in user_infos:
#         # Hash the password
#         hash_output = generate_password_hash(info[1])
#         split_hash_output = hash_output.split("$")
#         _, salt, password_hash = split_hash_output
#
#         # Create new user and save to database
#         user = UserModel(info[0], password_hash, salt)
#         db.session.add(user)
#
#     for info in category_infos:
#         category = CategoryModel(*info)
#         db.session.add(category)
#
#     for info in item_infos:
#         item = ItemModel(*info)
#         db.session.add(item)
#
#     db.session.commit()
# print("id of db.session in main init:{}".format(id(db.session)))
# user = UserModel.query.all()
# print(user)


def register_subpackages():
    from main import models

    for m in models.__all__:
        import_module("main.models." + m)

    import main.controllers  # noqa


register_subpackages()
register_error_handlers(app)
