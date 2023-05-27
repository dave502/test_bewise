from sqlalchemy import UniqueConstraint
from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class User(db.Model):
    __tablename__ = "users"

    # id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(64), unique=False, nullable=False)
    unique_name = db.Column(db.String(64), unique=True, nullable=False)
    tracks = db.relationship('Track', backref='owner', lazy='dynamic')

    def __init__(self, name: str, unique_name):
        self.name = name
        self.unique_name = unique_name

    def as_dict(self) -> dict:
        return {'unique_name': self.unique_name, 'uuid': self.uuid}


class Track(db.Model):
    __tablename__ = "tracks"
    __table_args__ = (UniqueConstraint('user', 'timestamp', name='_user_timestamp_uc'),
                      )
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    user = db.Column(UUID(as_uuid=True), db.ForeignKey('users.uuid', ondelete="CASCADE"))

    def __init__(self, name: str, user: User, timestamp: str):
        self.name = name
        self.user = user.uuid
        self.timestamp = timestamp

    def get_link(self):
        return {'id': self.id, 'user': self.user}
