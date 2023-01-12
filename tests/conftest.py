# TODO: to be open sourced
import logging
import os
import sys

import pytest
from alembic.command import upgrade
from alembic.config import Config
from flask_migrate import Migrate

from main import app as _app
from main import db
from tests.sample_config import sample_config

if os.getenv('ENVIRONMENT') != 'test':
    print('Tests should be run with "ENVIRONMENT=test"')
    sys.exit(1)

ALEMBIC_CONFIG = os.path.join(
    os.path.dirname(__file__), '..', 'migrations', 'alembic.ini'
)


def pytest_addoption(parser):
    parser.addoption(
        '--log', action='store', default='WARNING', help='set logging level'
    )


def recreate_database():
    """Run the alembic migrations"""
    db.reflect()
    db.drop_all()
    config = Config(ALEMBIC_CONFIG)
    upgrade(config, 'heads')


def configure_logging():
    # loglevel = pytest.config.getoption("--log")
    loglevel = 'WARNING'
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)

    logging.getLogger().setLevel(numeric_level)


@pytest.fixture(scope='session', autouse=True)
def app(request):
    ctx = _app.test_request_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session', autouse=True)
def database(request, app):
    Migrate(_app, db)
    recreate_database()


@pytest.fixture(scope='function', autouse=True)
def session(request, monkeypatch):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    # TODO(rohan): This shouldn't be necessary but it is. UGH
    # Patch Flask-SQLAlchemy to use our connection
    monkeypatch.setattr(db, 'get_engine', lambda *args: connection)

    db.session = session

    def teardown():
        session.close()
        transaction.rollback()
        connection.close()

    request.addfinalizer(teardown)
    return session


# Any configuration which must be created before running tests must be put here. The reason we add the database fixture
# to this although we don't use it at all is to ensure that this fixture will run after database fixture. Otherwise the
# configuration created here will be removed.
@pytest.fixture(scope='session', autouse=True)
def create_config(database):
    configure_logging()
    sample_config.create(db)
