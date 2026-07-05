from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Client, TrafficHistory
from config import get_client_name
import time

router = APIRouter(prefix="/api/clients", tags=["Clients"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def get_clients_statuses(db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    result = []

    current_time = int(time.time())

    for client in clients:
        latest_traffic = db.query(TrafficHistory) \
            .filter(TrafficHistory.client_id == client.id) \
            .order_by(TrafficHistory.timestamp.desc()) \
            .first()

        rx = latest_traffic.rx if latest_traffic else 0
        tx = latest_traffic.tx if latest_traffic else 0

        # Стандарт WireGuard: если последнее рукопожатие было меньше 180 секунд назад,
        # сессия активна и клиент отправляет/принимает keepalive пакеты.
        is_online = False
        if client.latest_handshake > 0:
            is_online = (current_time - client.latest_handshake) < 180

        display_name = get_client_name(client.public_key)

        result.append({
            "id": client.id,
            "public_key": client.public_key,
            "name": display_name,
            "ip": client.ip,
            "rx": rx,
            "tx": tx,
            "online": is_online
        })

    return result