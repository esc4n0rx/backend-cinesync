from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nickname = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_private = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(100), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('RoomUser', backref='room', cascade="all, delete-orphan")
    content_url = db.Column(db.String(300), nullable=True)  # URL do conteúdo
    content_type = db.Column(db.String(10), nullable=True)  # Tipo (youtube/hls)
    current_timestamp = db.Column(db.Float, default=0)  # Tempo atual do player
    is_paused = db.Column(db.Boolean, default=True)  # Estado do player

    def __repr__(self):
        return f'<Room {self.name}>'





class RoomUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RoomUser Room: {self.room_id}, User: {self.user_id}>'
