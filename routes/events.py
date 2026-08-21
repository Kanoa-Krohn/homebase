from flask import Blueprint, request, jsonify
from services.db import get_db
from services.events_service import get_upcoming_events, add_event, delete_event

events_bp = Blueprint('events', __name__)


@events_bp.route('/api/events', methods=['GET'])
def list_events():
    db = get_db()
    events = get_upcoming_events(db)
    db.close()
    return jsonify({'success': True, 'events': events})


@events_bp.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    title = data.get('title', '').strip()
    frequency = data.get('frequency', 'once').strip()
    event_time = data.get('time', '').strip() or None

    if not title or frequency not in ('once', 'daily', 'weekly', 'monthly'):
        return jsonify({'success': False, 'error': 'Missing or invalid fields'}), 400

    event_date = None
    weekday = None
    day_of_month = None

    if frequency == 'once':
        event_date = data.get('date', '').strip()
        if not event_date:
            return jsonify({'success': False, 'error': 'Date required for one-time events'}), 400
    elif frequency == 'weekly':
        weekday = data.get('weekday')
        if weekday is None or not (0 <= int(weekday) <= 6):
            return jsonify({'success': False, 'error': 'Valid weekday required'}), 400
        weekday = int(weekday)
    elif frequency == 'monthly':
        day_of_month = data.get('day_of_month')
        if day_of_month is None or not (1 <= int(day_of_month) <= 31):
            return jsonify({'success': False, 'error': 'Valid day of month required'}), 400
        day_of_month = int(day_of_month)

    db = get_db()
    add_event(db, title, frequency, event_date, event_time, weekday, day_of_month)
    db.close()

    return jsonify({'success': True})


@events_bp.route('/api/events/<int:event_id>', methods=['DELETE'])
def remove_event(event_id):
    db = get_db()
    delete_event(db, event_id)
    db.close()
    return jsonify({'success': True})