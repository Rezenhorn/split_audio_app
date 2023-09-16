import datetime

from apps import db


class AppRequest(db.Model):
    __tablename__ = "AppRequest"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    link = db.Column(db.Text)
    is_done = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
