import os
import yaml
from pathlib import Path

DATA_DIR = Path("data")
CONFIG_PATH = DATA_DIR / "config.yaml"
DB_PATH = DATA_DIR / "monitor.db"

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
    clients = load_clients_config()
    # Ищем по публичному ключу (или по IP, если решим привязаться к IP)
    return clients.get(public_key, {}).get("name", public_key[:8] + "...")