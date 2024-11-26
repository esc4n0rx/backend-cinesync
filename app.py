from app import create_app, db
from app.routes import auth
from app.models import User
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room

app = create_app()
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(auth, url_prefix='/api/auth')

@socketio.on('join')
def on_join(data):
    room = data['room']
    nickname = data['nickname']
    join_room(room)
    socketio.emit('user_joined', {'nickname': nickname}, to=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    nickname = data['nickname']
    leave_room(room)
    socketio.emit('user_left', {'nickname': nickname}, to=room)


@socketio.on('setContent')
def handle_set_content(data):
    room = data.get('room')
    content_url = data.get('content_url')
    content_type = data.get('content_type')
    timestamp = data.get('timestamp', 0)

    socketio.emit('updateContent', {
        'content_url': content_url,
        'content_type': content_type,
        'timestamp': timestamp
    }, to=room)

@socketio.on('play')
def handle_play(data):
    room = data.get('room')
    timestamp = data.get('timestamp')

    socketio.emit('playerPlay', {'timestamp': timestamp}, to=room)

@socketio.on('pause')
def handle_pause(data):
    room = data.get('room')
    timestamp = data.get('timestamp')

    socketio.emit('playerPause', {'timestamp': timestamp}, to=room)

@socketio.on('seek')
def handle_seek(data):
    room = data.get('room')
    timestamp = data.get('timestamp')

    socketio.emit('playerSeek', {'timestamp': timestamp}, to=room)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=4000)
