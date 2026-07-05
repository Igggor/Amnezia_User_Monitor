# Остановке контейнера
docker-compose down

# Удаляем старый файл базы данных (он лежит в папке data/)
rm -f data/monitor.db

# Чистим старый образ и запускаем чистую сборку
docker rmi amnezia_user_monitor_amnezia-monitor
docker-compose up --build -d