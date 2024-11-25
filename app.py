from app import create_app, db
from app.routes import auth
from app.models import User
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room

# Inicializar a aplicação
app = create_app()
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Inicializar SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Registrar Blueprint
app.register_blueprint(auth, url_prefix='/api/auth')

# Eventos de WebSocket
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

# Criar banco de dados se não existir
with app.app_context():
    db.create_all()

# Iniciar o servidor com suporte a WebSocket
if __name__ == '__main__':
    socketio.run(app, debug=True, port=4000)
