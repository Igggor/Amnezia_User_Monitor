def parse_wg_dump(raw_output: str) -> list:
    """
    Парсит вывод команды `wg show wg0 dump`.
    Пропускает первую строчку (информацию об интерфейсе).
    """
    peers = []
    lines = raw_output.strip().split('\n')

    if not lines or len(lines) <= 1:
        return peers  # Команда вернула пустоту или только интерфейс

    # Первая строка — это данные интерфейса (например, wg0 private_key public_key listen_port fwmark)
    # Нас интересуют строки начиная со второй (индексы 1+)
    for line in lines[1:]:
        parts = line.split('\t')
        if len(parts) < 8:
            continue

        try:
            peer_data = {
                "public_key": parts[0],
                "preshared_key": parts[1],
                "endpoint": parts[2],
                "allowed_ips": parts[3].split(',')[0],  # Берем первый IP, если их несколько
                "latest_handshake": int(parts[4]),
                "rx_bytes": int(parts[5]),
                "tx_bytes": int(parts[6]),
                "persistent_keepalive": parts[7]
            }
            peers.append(peer_data)
        except (ValueError, IndexError) as e:
            print(f"Ошибка парсинга строки пира: {e}")
            continue

    return peers