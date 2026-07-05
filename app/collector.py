import subprocess
from config import AMNEZIA_CONTAINER_NAME, WG_INTERFACE
from parser import parse_wg_dump
from database import save_metrics


def fetch_wg_dump() -> str:
    """
    Вызывает команду wg show dump через docker exec на хосте.
    """
    cmd = [
        "docker", "exec",
        AMNEZIA_CONTAINER_NAME,
        "wg", "show", WG_INTERFACE, "dump"
    ]

    try:
        # Запускаем команду и собираем вывод
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=4)

        if result.returncode != 0:
            print(f"Ошибка выполнения команды в контейнере {AMNEZIA_CONTAINER_NAME}: {result.stderr.strip()}")
            return ""

        return result.stdout
    except subprocess.TimeoutExpired:
        print("Превышено время ожидания ответа от контейнера WireGuard (Timeout).")
        return ""
    except Exception as e:
        print(f"Непредвиденная ошибка при попытке собрать метрики: {e}")
        return ""


def collect_and_store_metrics():
    """
    Основная точка входа для сборщика.
    Вызывается планировщиком задач.
    """
    raw_dump = fetch_wg_dump()
    if not raw_dump:
        return

    parsed_peers = parse_wg_dump(raw_dump)
    if parsed_peers:
        save_metrics(parsed_peers)