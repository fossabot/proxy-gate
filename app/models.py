from sqlalchemy.dialects.postgresql import JSON

from . import db


class SecretKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    secret_key = db.Column(db.String(50), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    inactive_since = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<secret_key {self.secret_key}>"


class RunTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(), unique=True, nullable=False)
    value = db.Column(JSON, nullable=False)

    def __repr__(self):
        return f"<value {self.value}>"
