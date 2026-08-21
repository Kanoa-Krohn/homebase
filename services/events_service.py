from datetime import datetime, date, timedelta
import calendar


def next_occurrence_date(now, frequency, event_date_str, weekday, day_of_month, event_time_str):
    today = now.date()
    event_time = datetime.strptime(event_time_str, '%H:%M').time() if event_time_str else None
    time_passed_today = event_time is not None and now.time() > event_time

    if frequency == 'once':
        return date.fromisoformat(event_date_str)

    if frequency == 'daily':
        return today + timedelta(days=1) if time_passed_today else today

    if frequency == 'weekly':
        days_ahead = (weekday - today.weekday()) % 7
        if days_ahead == 0 and time_passed_today:
            days_ahead = 7
        return today + timedelta(days=days_ahead)

    if frequency == 'monthly':
        year, month = today.year, today.month
        last_day_this_month = calendar.monthrange(year, month)[1]
        this_month_day = min(day_of_month, last_day_this_month)
        candidate = date(year, month, this_month_day)

        if candidate < today or (candidate == today and time_passed_today):
            month += 1
            if month > 12:
                month = 1
                year += 1
            last_day_next_month = calendar.monthrange(year, month)[1]
            candidate = date(year, month, min(day_of_month, last_day_next_month))

        return candidate

    return today


def format_event_label(next_date, today, event_time_str):
    if next_date == today:
        label = "Today"
    else:
        label = f"{next_date.strftime('%b')} {next_date.day}"

    time_str = ""
    if event_time_str:
        t = datetime.strptime(event_time_str, '%H:%M')
        hour_12 = t.hour % 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        ampm = 'AM' if t.hour < 12 else 'PM'
        time_str = f"{hour_12}:{t.minute:02d} {ampm}"

    return f"{label} {time_str}".strip() if time_str else label


def init_events_table(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            frequency TEXT NOT NULL DEFAULT 'once',
            event_date TEXT,
            event_time TEXT,
            weekday INTEGER,
            day_of_month INTEGER
        )
    """)
    db.commit()


def get_upcoming_events(db, limit=2):
    now = datetime.now()
    today = now.date()

    rows = db.execute("SELECT * FROM events").fetchall()

    computed = []
    for row in rows:
        if row['frequency'] == 'once':
            next_date = date.fromisoformat(row['event_date'])
            if next_date < today:
                continue
        else:
            next_date = next_occurrence_date(
                now, row['frequency'], row['event_date'], row['weekday'], row['day_of_month'], row['event_time']
            )

        computed.append({
            'id': row['id'],
            'title': row['title'],
            'next_date': next_date,
            'event_time': row['event_time'],
        })

    computed.sort(key=lambda e: (e['next_date'], e['event_time'] or ''))
    computed = computed[:limit]

    return [{
        'id': e['id'],
        'title': e['title'],
        'time': format_event_label(e['next_date'], today, e['event_time']),
    } for e in computed]


def add_event(db, title, frequency, date_str=None, time_str=None, weekday=None, day_of_month=None):
    db.execute(
        "INSERT INTO events (title, frequency, event_date, event_time, weekday, day_of_month) VALUES (?, ?, ?, ?, ?, ?)",
        (title, frequency, date_str, time_str, weekday, day_of_month)
    )
    db.commit()


def delete_event(db, event_id):
    db.execute("DELETE FROM events WHERE id = ?", (event_id,))
    db.commit()