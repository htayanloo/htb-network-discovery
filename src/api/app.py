"""Flask REST API application."""

from flask import Flask
from flask_cors import CORS

from api.routes import topology, devices, search
from utils.config import get_api_config
from utils.logger import get_logger

logger = get_logger(__name__)


def create_app():
    """
    Create and configure Flask application.

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    # Load configuration
    api_config = get_api_config()

    # Enable CORS for web dashboard
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Configure app
    app.config["JSON_SORT_KEYS"] = False

    # Register blueprints
    app.register_blueprint(topology.bp, url_prefix="/api")
    app.register_blueprint(devices.bp, url_prefix="/api")
    app.register_blueprint(search.bp, url_prefix="/api")

    # Health check endpoint
    @app.route("/")
    def index():
        return {
            "name": "Network Discovery API",
            "version": "0.1.0",
            "status": "running",
        }

    @app.route("/health")
    def health():
        return {"status": "healthy"}, 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {"error": "Internal server error"}, 500

    logger.info("Flask application created successfully")
    return app


if __name__ == "__main__":
    app = create_app()
    config = get_api_config()
    app.run(host=config["host"], port=config["port"], debug=config["debug"])
