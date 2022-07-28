from datetime import datetime

from main import db


class ItemModel(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.VARCHAR(255), unique=True, nullable=False)
    description = db.Column(db.TEXT, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    created = db.Column(db.TIMESTAMP, default=datetime.now)
    updated = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    def __init__(self, user_id, name, description, category_id):
        self.name = name
        self.description = description
        self.user_id = user_id
        self.category_id = category_id

    @classmethod
    def get_by_id(cls, id_):
        return cls.query.get(id_)

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).one_or_none()

    @classmethod
    def get_multiple(cls, start_id, end_id, category_id=None):
        if category_id:
            return (
                cls.query.filter_by(category_id=category_id)
                .slice(start_id, end_id)
                .all()
            )
        return cls.query.slice(start_id, end_id).all()

    @classmethod
    def get_count(cls, category_id=None):
        if category_id:
            return cls.query.filter(cls.category_id == category_id).count()
        return cls.query.count()
