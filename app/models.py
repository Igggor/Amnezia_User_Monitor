from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    public_key = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    ip = Column(String, nullable=True)

    # Связь с историей трафика
    traffic_history = relationship("TrafficHistory", back_populates="client", cascade="all, delete-orphan")


class TrafficHistory(Base):
    __tablename__ = 'traffic_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    rx = Column(BigInteger, default=0)  # Принято байт
    tx = Column(BigInteger, default=0)  # Отправлено байт
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    client = relationship("Client", back_populates="traffic_history")