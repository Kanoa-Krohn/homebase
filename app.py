from flask import Flask
from routes.home import home_bp
from routes.pi import pi_bp
from routes.events import events_bp
from routes.news import news_bp
from services.db import get_db
from services.events_service import init_events_table


def create_app():
    app = Flask(__name__)
    app.register_blueprint(home_bp)
    app.register_blueprint(pi_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(news_bp)

    db = get_db()
    init_events_table(db)
    db.close()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)