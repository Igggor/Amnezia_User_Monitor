from apscheduler.schedulers.background import BackgroundScheduler
from app.collector import collect_and_store_metrics

scheduler = BackgroundScheduler()

def start_scheduler():
    """Запускает фоновый сборщик данных."""
    if not scheduler.running:
        # Добавляем задачу с интервалом в 5 секунд
        scheduler.add_job(
            collect_and_store_metrics,
            trigger="interval",
            seconds=5,
            id="wg_metrics_collector",
            replace_existing=True
        )
        scheduler.start()
        print("Планировщик сбора метрик успешно запущен (интервал: 5с).")

def shutdown_scheduler():
    """Останавливает планировщик при выключении приложения."""
    if scheduler.running:
        scheduler.shutdown()
        print("Планировщик сбора метрик остановлен.")