from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db
from scheduler import start_scheduler, shutdown_scheduler
from api.clients import router as clients_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действия при старте приложения
    print("Инициализация базы данных...")
    init_db()
    print("Запуск фонового сборщика метрик...")
    start_scheduler()

    yield

    # Действия при остановке приложения
    print("Остановка фонового сборщика...")
    shutdown_scheduler()


app = FastAPI(
    title="Amnezia Monitor API",
    version="0.1.0",
    lifespan=lifespan
)

# Подключаем API эндпоинты
app.include_router(clients_router)


@app.get("/")
def read_root():
    return {"status": "running", "project": "Amnezia Monitor"}