import os
from apscheduler.schedulers.background import BackgroundScheduler
from prometheus_client import Counter
from database import save_metrics, clean_old_metrics
from config import get_client_name

scheduler = BackgroundScheduler()

WG_RX_COUNTER = Counter('amnezia_wireguard_rx_bytes_total', 'Total received bytes', ['public_key', 'name'])
WG_TX_COUNTER = Counter('amnezia_wireguard_tx_bytes_total', 'Total transmitted bytes', ['public_key', 'name'])

LAST_SEEN_TRAFFIC = {}
DUMP_FILE_PATH = "/tmp/wg0.dump"


def parse_wg_dump():
    if not os.path.exists(DUMP_FILE_PATH):
        print(f"[Collector Error] Файл дампа не найден по пути: {DUMP_FILE_PATH}")
        return []

    try:
        with open(DUMP_FILE_PATH, "r") as f:
            lines = f.read().strip().split("\n")
    except Exception as e:
        print(f"[Collector Error] Не удалось прочитать файл дампа: {e}")
        return []

    parsed_peers = []
    for line in lines:
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 5:
            continue

        try:
            pub_key = parts[0]
            latest_handshake = int(parts[4]) if parts[4] != '(none)' else 0
            rx_bytes = int(parts[5])
            tx_bytes = int(parts[6])
            allowed_ips = parts[3]

            parsed_peers.append({
                'public_key': pub_key,
                'allowed_ips': allowed_ips,
                'latest_handshake': latest_handshake,
                'rx_bytes': rx_bytes,
                'tx_bytes': tx_bytes
            })

            name = get_client_name(pub_key)

            if pub_key not in LAST_SEEN_TRAFFIC:
                LAST_SEEN_TRAFFIC[pub_key] = {'rx': rx_bytes, 'tx': tx_bytes}
                WG_RX_COUNTER.labels(public_key=pub_key, name=name).inc(rx_bytes)
                WG_TX_COUNTER.labels(public_key=pub_key, name=name).inc(tx_bytes)
            else:
                diff_rx = rx_bytes - LAST_SEEN_TRAFFIC[pub_key]['rx']
                diff_tx = tx_bytes - LAST_SEEN_TRAFFIC[pub_key]['tx']

                if diff_rx >= 0:
                    WG_RX_COUNTER.labels(public_key=pub_key, name=name).inc(diff_rx)
                    LAST_SEEN_TRAFFIC[pub_key]['rx'] = rx_bytes
                if diff_tx >= 0:
                    WG_TX_COUNTER.labels(public_key=pub_key, name=name).inc(diff_tx)
                    LAST_SEEN_TRAFFIC[pub_key]['tx'] = tx_bytes

        except (IndexError, ValueError) as parse_err:
            continue

    return parsed_peers


def collect_job():
    peers = parse_wg_dump()
    if peers:
        save_metrics(peers)


def cleanup_job():
    """Задача очистки старых метрик (храним историю 3 дня)"""
    print("[Scheduler] Запуск ежедневной очистки базы данных...")
    clean_old_metrics(days_to_keep=3)

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(collect_job, 'interval', seconds=5, id='wg_collector_job')

        scheduler.add_job(
            cleanup_job,
            'cron',
            hour=4,
            minute=0,
            id='db_cleanup_job',
            replace_existing=True
        )

        scheduler.start()
        print("Планировщик сбора метрик успешно запущен (интервал: 5с).")


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
