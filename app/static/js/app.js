// Функция для форматирования байт в понятные MiB/GiB
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KiB', 'MiB', 'GiB', 'TiB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

async function loadDashboardData() {
    try {
        const response = await fetch('/api/clients');
        const clients = await response.json();

        const container = document.getElementById('clients-container');
        container.innerHTML = ''; // Очищаем старый список

        let onlineCount = 0;

        if (clients.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">Клиенты не найдены. Ждем дамп WireGuard...</p>';
            return;
        }

        clients.forEach(client => {
            if (client.online) onlineCount++;

            const statusDot = client.online ? '🟢' : '⚫';
            const statusText = client.online ? 'Online' : 'Offline';

            const card = document.createElement('div');
            card.className = 'p-4 bg-gray-900 rounded-lg border border-gray-700 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2';

            card.innerHTML = `
                <div>
                    <div class="flex items-center gap-2">
                        <span>${statusDot}</span>
                        <h3 class="font-bold text-white text-lg">${client.name}</h3>
                    </div>
                    <p class="text-sm text-gray-400">IP: <span class="font-mono">${client.ip}</span></p>
                    <p class="text-xs text-gray-500 font-mono mt-1">${client.public_key}</p>
                </div>
                <div class="text-left sm:text-right w-full sm:w-auto mt-2 sm:mt-0 border-t sm:border-t-0 border-gray-800 pt-2 sm:pt-0">
                    <div class="text-sm">
                        <span class="text-blue-400">↓ ${formatBytes(client.rx)}</span> 
                        <span class="text-gray-600 mx-1">|</span> 
                        <span class="text-green-400">↑ ${formatBytes(client.tx)}</span>
                    </div>
                    <p class="text-xs text-gray-400 mt-1">${statusText}</p>
                </div>
            `;
            container.appendChild(card);
        });

        // Обновляем счетчики сверху
        document.getElementById('total-clients').innerText = clients.length;
        document.getElementById('online-clients').innerText = onlineCount;
        document.getElementById('last-update').innerText = new Date().toLocaleTimeString();

    } catch (error) {
        console.error("Ошибка обновления дашборда:", error);
    }
}

// Первоначальная загрузка и запуск интервала обновления (каждые 3 секунды)
loadDashboardData();
setInterval(loadDashboardData, 3000);