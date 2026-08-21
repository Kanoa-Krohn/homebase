from flask import Blueprint, jsonify
from services.news_service import get_news

news_bp = Blueprint('news', __name__)


@news_bp.route('/api/news', methods=['GET'])
def news():
    try:
        data = get_news()
        return jsonify({'success': True, **data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 502