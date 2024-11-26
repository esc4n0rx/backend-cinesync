import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Adicione o caminho da aplicação ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import Room, RoomUser

# Configure o banco de dados (substitua pelas suas credenciais)
DATABASE_URI = "sqlite:///instance/users.db"  # Caminho correto para o banco
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def clean_rooms():
    try:
        rooms_without_users = (
            session.query(Room)
            .outerjoin(RoomUser, Room.id == RoomUser.room_id)
            .filter(RoomUser.id == None)  
        ).all()

        threshold_date = datetime.utcnow() - timedelta(days=3)
        old_test_rooms = (
            session.query(Room)
            # .filter(Room.created_at < threshold_date)
        ).all()

        rooms_to_delete = set(rooms_without_users + old_test_rooms)

        for room in rooms_to_delete:
            session.query(RoomUser).filter(RoomUser.room_id == room.id).delete()
            session.delete(room)

        session.commit()
        print(f"{len(rooms_to_delete)} sala(s) removida(s) com sucesso.")
    except Exception as e:
        print(f"Erro ao limpar salas: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    clean_rooms()
