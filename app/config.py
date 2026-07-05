import os
import yaml
from pathlib import Path

DATA_DIR = Path("data")
CONFIG_PATH = DATA_DIR / "config.yaml"
DB_PATH = DATA_DIR / "monitor.db"
CLIENTS_MAPPING = {
    "5WRwALDKwUz+g6EQ+66md8uqubeGGnJIqxFsVvrEq0E=": "Tema1",
    "A8BajQOhivMHu5OvV5JSsxtHT+Eeo2v38MvbeWRD3RU=": "Tema2",
    "HN+o1gh0RSPGf0+pZAYjbnrgbTxgU0r28LRrEt/0hjU=": "Tema3",
    "lHh2a/Twtw+DpF4m3uAieUn3P6wQRp/2VkXr+tYevxg=": "Tema4",
    "PWs4i+t5mX2i8nFIjdni/2Dvs4iB53Ltu6jbVkjuxBA=": "Tema5",
}

# Создаем директорию для данных, если её нет
DATA_DIR.mkdir(exist_ok=True)

AMNEZIA_CONTAINER_NAME = os.getenv("AMNEZIA_CONTAINER_NAME", "amnezia-awg")
WG_INTERFACE = os.getenv("WG_INTERFACE", "wg0")


def load_clients_config():
    if not CONFIG_PATH.exists():
        # Создаем дефолтный пустой конфиг
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump({"clients": {}}, f)
        return {}

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            return config.get("clients", {})
    except Exception as e:
        print(import_error := f"Ошибка чтения config.yaml: {e}")
        return {}


def get_client_name(public_key: str) -> str:
    # 1. Сначала проверяем наш жестко заданный словарь CLIENTS_MAPPING
    if public_key in CLIENTS_MAPPING:
        return CLIENTS_MAPPING[public_key]

    # 2. Если в словаре нет, пытаемся посмотреть в config.yaml
    clients = load_clients_config()
    if public_key in clients:
        return clients[public_key].get("name", public_key[:8] + "...")

    # 3. Если ключа вообще нигде нет, возвращаем первые 8 символов ключа
    return public_key[:8] + "..."