import datetime

import jwt

# from werkzeug.security import generate_password_hash
#
# from main import app, db
# from main.models.category import CategoryModel
# from main.models.item import ItemModel
# from main.models.user import UserModel


# def insert_test_data():
#     return
#     user_infos = [
#         ("user@abc.com", "Password123"),
#         ("me@example.com", "Password123"),
#     ]
#
#     category_infos = [
#         (1, "category1"),
#         (2, "category2"),
#         (1, "category3"),
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
#
#     for info in user_infos:
#         # Hash the password
#         hash_output = generate_password_hash(info[1])
#         split_hash_output = hash_output.split("$")
#         _, password_salt, password_hash = split_hash_output
#
#         # Create new user and save to database
#         user = UserModel(info[0], password_hash, password_salt)
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


def generate_mock_user_token(app, user_id):
    token = jwt.encode(
        {
            "id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=15),
        },
        app.config["SECRET_KEY"],
    )
    return token
