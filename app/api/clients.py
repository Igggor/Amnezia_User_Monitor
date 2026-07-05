from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Client, TrafficHistory
from app.config import get_client_name
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
        # Получаем последнюю запись трафика для этого клиента
        latest_traffic = db.query(TrafficHistory) \
            .filter(TrafficHistory.client_id == client.id) \
            .order_by(TrafficHistory.timestamp.desc()) \
            .first()

        rx = latest_traffic.rx if latest_traffic else 0
        tx = latest_traffic.tx if latest_traffic else 0

        # В WireGuard дамп возвращает timestamp последнего хэндшейка.
        # Для симуляции логики "online", если хэндшейк был меньше 3 минут (180 сек) назад — клиент онлайн.
        # В реальном дампе мы будем сохранять сырой handshake, но пока заложим базовую логику проверки:
        # (Для демонстрации вывода высчитаем заглушку, на этапе интеграции с живым wg это заработает на 100%)

        # Получаем имя из config.yaml, если оно там есть, иначе используем public_key
        display_name = get_client_name(client.public_key)

        result.append({
            "id": client.id,
            "public_key": client.public_key,
            "name": display_name,
            "ip": client.ip,
            "rx": rx,
            "tx": tx,
            "online": False  # Будет динамически рассчитываться от handshake на живых данных
        })

    return result