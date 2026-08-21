function updateEventFrequencyFields() {
    const freq = document.getElementById('event-frequency-select').value;
    document.getElementById('event-date-input').style.display = freq === 'once' ? 'block' : 'none';
    document.getElementById('event-weekday-select').style.display = freq === 'weekly' ? 'block' : 'none';
    document.getElementById('event-dom-input').style.display = freq === 'monthly' ? 'block' : 'none';
}

function openAddEventModal() {
    document.getElementById('event-title-input').value = '';
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('event-date-input').value = today;
    document.getElementById('event-time-input').value = '';
    document.getElementById('event-frequency-select').value = 'once';
    document.getElementById('event-weekday-select').value = '0';
    document.getElementById('event-dom-input').value = '';
    updateEventFrequencyFields();
    document.getElementById('add-event-modal').style.display = 'block';
}

function closeAddEventModal() {
    document.getElementById('add-event-modal').style.display = 'none';
}

function loadEvents() {
    fetch('/api/events')
        .then(r => r.json())
        .then(data => {
            const list = document.getElementById('events-list');
            if (data.success && data.events.length > 0) {
                list.innerHTML = data.events.map(e =>
                    `<div class="event-item">
                        <span>${e.title}</span>
                        <span class="event-item-right">
                            <span class="event-time">${e.time}</span>
                            <button class="event-delete-btn" onclick="deleteEvent(${e.id})">✕</button>
                        </span>
                    </div>`
                ).join('');
            } else {
                list.innerHTML = '<div class="empty-state">No upcoming events</div>';
            }
        })
        .catch(() => {
            document.getElementById('events-list').innerHTML = '<div class="empty-state">No upcoming events</div>';
        });
}

function deleteEvent(id) {
    fetch(`/api/events/${id}`, { method: 'DELETE' })
        .then(() => loadEvents());
}

function submitNewEvent() {
    const title = document.getElementById('event-title-input').value.trim();
    const time = document.getElementById('event-time-input').value;
    const frequency = document.getElementById('event-frequency-select').value;

    if (!title) return;

    const payload = { title, time, frequency };

    if (frequency === 'once') {
        payload.date = document.getElementById('event-date-input').value;
        if (!payload.date) return;
    } else if (frequency === 'weekly') {
        payload.weekday = parseInt(document.getElementById('event-weekday-select').value, 10);
    } else if (frequency === 'monthly') {
        const dom = document.getElementById('event-dom-input').value;
        if (!dom) return;
        payload.day_of_month = parseInt(dom, 10);
    }

    fetch('/api/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            closeAddEventModal();
            loadEvents();
        }
    });
}