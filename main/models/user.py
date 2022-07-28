from datetime import datetime

from main import db


class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.VARCHAR(254), unique=True, nullable=False)
    password_hash = db.Column(db.CHAR(64), nullable=False)
    password_salt = db.Column(db.CHAR(16), nullable=False)
    created = db.Column(db.TIMESTAMP, default=datetime.now)
    updated = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    # One-to-many relationships
    categories = db.relationship("CategoryModel", backref="owner", lazy=True)
    items = db.relationship("ItemModel", backref="owner", lazy=True)

    def __init__(self, email, password_hash, salt):
        self.email = email
        self.password_hash = password_hash
        self.password_salt = salt

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).one_or_none()
