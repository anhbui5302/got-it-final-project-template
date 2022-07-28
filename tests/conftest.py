import os
import sys
from pathlib import Path

import pytest
from alembic.command import upgrade
from alembic.config import Config
from werkzeug.security import generate_password_hash

from main import app as _app
from main import db
from main.models.category import CategoryModel
from main.models.item import ItemModel
from main.models.user import UserModel

if os.getenv("ENVIRONMENT") != "test":
    print('Tests should be run with "ENVIRONMENT=test"')
    sys.exit(1)

ALEMBIC_CONFIG = (
    (Path(__file__) / ".." / ".." / "migrations" / "alembic.ini").resolve().as_posix()
)


@pytest.fixture(scope="session", autouse=True)
def app():
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope="session", autouse=True)
def recreate_database(app):
    db.reflect()
    db.drop_all()
    _config = Config(ALEMBIC_CONFIG)
    upgrade(_config, "heads")

    user_infos = [
        ("user@abc.com", "Password123"),
        ("me@example.com", "Password123"),
    ]

    category_infos = [
        (1, "category1"),
        (2, "category2"),
        (1, "category3"),
        (2, "category4"),
    ]

    item_infos = [
        (1, "item1", "description1", 1),
        (2, "item2", "description1", 2),
        (1, "item3", "description1", 3),
        (2, "item4", "description1", 4),
        (1, "item5", "description1", 1),
        (2, "item6", "description1", 2),
    ]

    for info in user_infos:
        # Hash the password
        hash_output = generate_password_hash(info[1])
        split_hash_output = hash_output.split("$")
        _, password_salt, password_hash = split_hash_output

        # Create new user and save to database
        user = UserModel(info[0], password_hash, password_salt)
        db.session.add(user)

    for info in category_infos:
        category = CategoryModel(*info)
        db.session.add(category)

    for info in item_infos:
        item = ItemModel(*info)
        db.session.add(item)

    db.session.commit()


@pytest.fixture(scope="function", autouse=True)
def session(monkeypatch):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session
    # print(id(db.session))
    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function", autouse=True)
def client(app, session):
    return app.test_client()
