from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_PATH
from models import Base, Client, TrafficHistory
from datetime import datetime

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def save_metrics(parsed_peers: list):
    db = SessionLocal()
    try:
        current_time = datetime.utcnow()
        for peer in parsed_peers:
            client = db.query(Client).filter(Client.public_key == peer['public_key']).first()
            if not client:
                client = Client(
                    public_key=peer['public_key'],
                    ip=peer['allowed_ips'],
                    name=None
                )
                db.add(client)
                db.flush()

            # Обновляем динамические данные клиента из дампа
            client.ip = peer['allowed_ips']
            client.latest_handshake = peer['latest_handshake']  # Сохраняем реальный хэндшейк

            # Записываем историю трафика
            history_entry = TrafficHistory(
                client_id=client.id,
                rx=peer['rx_bytes'],
                tx=peer['tx_bytes'],
                timestamp=current_time
            )
            db.add(history_entry)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Ошибка сохранения в БД: {e}")
    finally:
        db.close()