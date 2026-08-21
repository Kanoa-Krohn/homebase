from flask import Blueprint, render_template, jsonify
from services.weather_service import get_weather

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return render_template('index.html')

@home_bp.route('/api/weather')
def weather():
    try:
        data = get_weather()
        return jsonify({'success': True, **data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 502