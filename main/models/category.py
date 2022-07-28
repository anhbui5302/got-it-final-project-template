from datetime import datetime

from sqlalchemy import func

from main import db


class CategoryModel(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.VARCHAR(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created = db.Column(db.TIMESTAMP, default=datetime.now)
    updated = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    # One-to-many relationships
    items = db.relationship("ItemModel", lazy=True, cascade="all, delete")

    def __init__(self, user_id, name):
        self.name = name
        self.user_id = user_id

    @classmethod
    def get_by_id(cls, id_):
        return cls.query.filter_by(id=id_).one_or_none()

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).one_or_none()

    @classmethod
    def get_multiple(cls, start_id, end_id):
        # page = 2, per_page = 2
        # start_id = 2, end_id = 4
        # slice(start_id, end_id) returns the 3rd and 4th row
        return cls.query.slice(start_id, end_id).all()

    @classmethod
    def get_count(cls):
        # SELECT count(categories.id) AS count_1
        # FROM categories
        return db.session.query(func.count(cls.id)).scalar()
