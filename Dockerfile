FROM python:3.11-slim

# Устанавливаем системные утилиты, включая wireguard-tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    wireguard-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Копируем ТОЛЬКО содержимое папки app внутрь /app контейнера
COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]