FROM python:3.11-alpine

RUN apk add --no-cache docker-cli

# Копируем всё содержимое нашей локальной папки app в корень контейнера /app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app .

EXPOSE 8000

# Запускаем uvicorn напрямую, так как main.py лежит в корне /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]