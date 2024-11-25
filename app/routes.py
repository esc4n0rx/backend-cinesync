from flask import Blueprint, request, jsonify
from .models import User
from .models import User, Room, RoomUser
from . import db
import bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/user-by-nickname', methods=['GET'])
def get_user_by_nickname():
    try:
        nickname = request.args.get('nickname')
        if not nickname:
            return jsonify({'error': 'Nickname é obrigatório'}), 400

        user = User.query.filter_by(nickname=nickname).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        return jsonify({'id': user.id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']
        password = data['password']
        nickname = data['nickname']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Usuário já registrado'}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = User(name=name, email=email, password=hashed_password, nickname=nickname)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Usuário registrado com sucesso', 'nickname': nickname}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'error': 'Credenciais inválidas'}), 401

        return jsonify({'message': 'Login bem-sucedido', 'nickname': user.nickname}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#cria uma sala
@auth.route('/create', methods=['POST'])
def create_room():
    try:
        data = request.get_json()
        name = data.get('name')
        is_private = data.get('is_private', False)
        password = data.get('password') if is_private else None
        created_by = data.get('created_by')

        if not name or not created_by:
            return jsonify({'error': 'Nome da sala e criador são obrigatórios'}), 400

        existing_room = Room.query.filter_by(name=name).first()
        if existing_room:
            return jsonify({'error': 'Nome de sala já existe'}), 400


        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if password else None
        new_room = Room(name=name, is_private=is_private, password=hashed_password, created_by=created_by)
        db.session.add(new_room)
        db.session.commit()

        return jsonify({'message': 'Sala criada com sucesso', 'room_id': new_room.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#entra na sala
@auth.route('/join', methods=['POST'])
def join_room():
    try:
        data = request.get_json()
        room_id = data['room_id']
        user_id = data['user_id']
        password = data.get('password')

       
        room = Room.query.get(room_id)
        if not room:
            return jsonify({'error': 'Sala não encontrada'}), 404

       
        if len(room.users) >= 5:
            return jsonify({'error': 'Sala cheia'}), 400

       
        if room.is_private:
            if not password or not bcrypt.checkpw(password.encode('utf-8'), room.password.encode('utf-8')):
                return jsonify({'error': 'Senha incorreta'}), 401

        existing_user = RoomUser.query.filter_by(room_id=room_id, user_id=user_id).first()
        if existing_user:
            return jsonify({'error': 'Usuário já está na sala'}), 400

        new_room_user = RoomUser(room_id=room_id, user_id=user_id)
        db.session.add(new_room_user)
        db.session.commit()

        return jsonify({'message': 'Usuário entrou na sala com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#lista salas publicas
@auth.route('/public', methods=['GET'])
def list_public_rooms():
    try:
        rooms = Room.query.filter_by(is_private=False).all()
        public_rooms = [
            {'id': room.id, 'name': room.name, 'people': len(room.users)}
            for room in rooms
        ]
        return jsonify(public_rooms), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#sai da sala
@auth.route('/leave', methods=['POST'])
def leave_room():
    try:
        data = request.get_json()
        room_id = data['room_id']
        user_id = data['user_id']

        room_user = RoomUser.query.filter_by(room_id=room_id, user_id=user_id).first()
        if not room_user:
            return jsonify({'error': 'Usuário não está nesta sala'}), 400

        db.session.delete(room_user)
        db.session.commit()

        if not RoomUser.query.filter_by(room_id=room_id).first():
            Room.query.filter_by(id=room_id).delete()
            db.session.commit()

        return jsonify({'message': 'Usuário saiu da sala com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#busca sala por id
@auth.route('/users/<int:room_id>', methods=['GET'])
def list_room_users(room_id):
    try:
        room = Room.query.get(room_id)
        if not room:
            return jsonify({'error': 'Sala não encontrada'}), 404

        users = [
            {'id': user.user_id, 'nickname': User.query.get(user.user_id).nickname}
            for user in room.users
        ]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@auth.route('/room/<int:room_id>', methods=['GET'])
def get_room_details(room_id):
    try:
        # Buscar a sala pelo ID
        room = Room.query.get(room_id)
        if not room:
            return jsonify({'error': 'Sala não encontrada'}), 404

        # Buscar os participantes da sala
        participants = RoomUser.query.filter_by(room_id=room_id).all()
        participant_data = [
            {
                'id': participant.user_id,
                'nickname': User.query.get(participant.user_id).nickname
            }
            for participant in participants
        ]

        # Retornar os dados da sala e dos participantes
        return jsonify({
            'room': {
                'id': room.id,
                'name': room.name,
                'is_private': room.is_private,
                'created_by': room.created_by,
            },
            'participants': participant_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


