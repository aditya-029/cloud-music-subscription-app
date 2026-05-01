"""
Main Flask backend application.

Run locally from project root:
    python -m backend.app

Available routes:
- GET  /health
- POST /login
- POST /register
- GET  /songs
- GET  /subscriptions
- POST /subscriptions
- DELETE /subscriptions/<email>/<song_id>
"""

from flask import Flask
from flask_cors import CORS

from backend.config import APP_HOST, APP_PORT, FLASK_DEBUG, CORS_ORIGINS
from backend.routes.auth_routes import auth_bp
from backend.routes.music_routes import music_bp
from backend.routes.subscription_routes import subscription_bp
from backend.utils.response import success_response


def create_app():
    app = Flask(__name__)

    CORS(
        app,
        resources={r"/*": {"origins": CORS_ORIGINS}},
        supports_credentials=False,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(music_bp)
    app.register_blueprint(subscription_bp)

    @app.route("/health", methods=["GET"])
    def health_check():
        return success_response(
            data={"status": "healthy"},
            message="Backend is running",
            status_code=200,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=APP_HOST,
        port=APP_PORT,
        debug=FLASK_DEBUG,
    )
