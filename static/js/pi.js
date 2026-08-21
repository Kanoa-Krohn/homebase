let piStatsPollTimer = null;
let statPairs = [];
let currentStatPairIndex = 0;
let statCycleTimer = null;

function loadSystemStats() {
    fetch('/api/system_stats')
        .then(r => r.json())
        .then(data => {
            document.getElementById('net-wifi-signal').textContent =
                data.wifi_signal !== null ? `${data.wifi_signal}%` : 'N/A';
            document.getElementById('net-wifi-ssid').textContent = data.wifi_ssid || 'N/A';
            document.getElementById('net-ip').textContent = data.ip_address || 'N/A';
            document.getElementById('net-uptime').textContent = data.uptime || 'N/A';

            const entries = [
                {
                    label: 'CPU Temp',
                    value: data.cpu_temp !== null ? `${data.cpu_temp}°C` : 'N/A',
                    warn: data.cpu_temp !== null && data.cpu_temp >= 70
                },
                { label: 'CPU Load', value: data.cpu_usage !== null ? `${data.cpu_usage}%` : 'N/A' },
                { label: 'Memory', value: data.mem_used_pct !== null ? `${data.mem_used_pct}%` : 'N/A' },
                { label: 'Disk', value: data.disk_used_pct !== null ? `${data.disk_used_pct}%` : 'N/A' },
            ];

            const newPairs = [];
            for (let i = 0; i < entries.length; i += 2) {
                newPairs.push(entries.slice(i, i + 2));
            }
            statPairs = newPairs;

            if (currentStatPairIndex >= statPairs.length) {
                currentStatPairIndex = 0;
            }

            renderStatsDots();
            updateStatPairText(currentStatPairIndex);

            if (!statCycleTimer) {
                statCycleTimer = setInterval(cycleStats, 4000);
            }
        })
        .catch(() => {});
}

function renderStatsDots() {
    document.getElementById('stats-dots').innerHTML = statPairs.map((_, i) =>
        `<span class="news-dot${i === currentStatPairIndex ? ' active' : ''}"></span>`
    ).join('');
}

function updateStatPairText(index) {
    const pair = statPairs[index];
    if (!pair) return;

    const value1El = document.getElementById('stat-value-1');
    document.getElementById('stat-label-1').textContent = pair[0].label;
    value1El.textContent = pair[0].value;
    value1El.classList.toggle('temp-warn', !!pair[0].warn);

    const box2 = document.getElementById('stat-box-2');
    const value2El = document.getElementById('stat-value-2');
    if (pair[1]) {
        document.getElementById('stat-label-2').textContent = pair[1].label;
        value2El.textContent = pair[1].value;
        value2El.classList.toggle('temp-warn', !!pair[1].warn);
        box2.style.visibility = 'visible';
    } else {
        box2.style.visibility = 'hidden';
    }
}

function showStatPair(index) {
    const box1 = document.getElementById('stat-box-1');
    const box2 = document.getElementById('stat-box-2');
    box1.style.opacity = 0;
    box2.style.opacity = 0;

    setTimeout(() => {
        updateStatPairText(index);
        box1.style.opacity = 1;
        box2.style.opacity = 1;
    }, 250);
}

function cycleStats() {
    if (statPairs.length === 0) return;
    currentStatPairIndex = (currentStatPairIndex + 1) % statPairs.length;
    showStatPair(currentStatPairIndex);
    renderStatsDots();
}

function startPiPolling() {
    loadSystemStats();
    if (piStatsPollTimer) clearInterval(piStatsPollTimer);
    piStatsPollTimer = setInterval(loadSystemStats, 5000);
}

function stopPiPolling() {
    if (piStatsPollTimer) {
        clearInterval(piStatsPollTimer);
        piStatsPollTimer = null;
    }
    if (statCycleTimer) {
        clearInterval(statCycleTimer);
        statCycleTimer = null;
    }
}

function reconnectWifi() {
    const btn = document.getElementById('wifi-reconnect-btn');
    btn.disabled = true;
    btn.textContent = 'Reconnecting...';

    fetch('/api/wifi/reconnect', { method: 'POST' })
        .then(r => r.json())
        .then(() => {
            setTimeout(() => {
                btn.disabled = false;
                btn.textContent = 'Reconnect';
                loadSystemStats();
            }, 6000);
        })
        .catch(() => {
            btn.disabled = false;
            btn.textContent = 'Reconnect';
        });
}

onPanelShow('panel-pi', startPiPolling);
onPanelHide('panel-pi', stopPiPolling);