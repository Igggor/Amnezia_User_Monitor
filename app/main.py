from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from database import init_db
from scheduler import start_scheduler, shutdown_scheduler
from api.clients import router as clients_router
from pathlib import Path

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Инициализация базы данных...")
    init_db()
    print("Запуск фонового сборщика метрик...")
    start_scheduler()
    yield
    print("Остановка фонового сборщика...")
    shutdown_scheduler()

app = FastAPI(
    title="Amnezia Monitor",
    version="0.1.0",
    lifespan=lifespan
)

# Настраиваем папки со статикой и шаблонами
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Подключаем API
app.include_router(clients_router)

# Вместо старого read_root отдаем красивую HTML страницу
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})