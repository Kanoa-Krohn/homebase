from flask import Blueprint, jsonify
from services.system_service import get_system_stats, reconnect_wifi

pi_bp = Blueprint('pi', __name__)


@pi_bp.route('/api/system_stats')
def system_stats():
    return jsonify({'success': True, **get_system_stats()})


@pi_bp.route('/api/wifi/reconnect', methods=['POST'])
def wifi_reconnect():
    success = reconnect_wifi()
    return jsonify({'success': success})