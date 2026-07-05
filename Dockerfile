FROM python:3.11-alpine

# Устанавливаем docker-cli
RUN apk add --no-cache docker-cli

# Корневой директорией делаем /app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# КОПИРУЕМ папку app внутрь /app/app, чтобы пути вида 'from app.models ...' работали корректно
COPY ./app ./app

EXPOSE 8000

# Запускаем uvicorn из корня, указывая модуль app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]