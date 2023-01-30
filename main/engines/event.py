from main import db
from main.models.event import EventModel


def create_event(name: str, account_id: int, meta_data: dict):
    event = EventModel(name=name, account_id=account_id, meta_data=meta_data)
    db.session.add(event)
