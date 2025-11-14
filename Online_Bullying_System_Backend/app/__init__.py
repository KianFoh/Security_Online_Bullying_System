import os
import logging
from flask import Flask, Request, jsonify, redirect, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ensure logger prints INFO+ to the console
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.info("App create_app() initializing")

    db.init_app(app)

    # Import models here so Flask-Migrate can detect them
    from app import models

    migrate.init_app(app, db)

    # enable CORS for frontend connections (adjust origins in Config if needed)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    _register_transport_security(app)

    # ensure upload directories exist
    upload_root = app.config.get("UPLOAD_FOLDER")
    avatar_subdir = app.config.get("AVATAR_SUBDIR", "avatars")
    complaint_subdir = app.config.get("COMPLAINT_ATTACHMENT_SUBDIR", "complaints")
    if upload_root:
        try:
            os.makedirs(os.path.join(upload_root, avatar_subdir), exist_ok=True)
            os.makedirs(os.path.join(upload_root, complaint_subdir), exist_ok=True)
        except OSError:
            app.logger.warning("Could not create upload directory at %s", upload_root)

    # Import and register routes
    from .routes import bp
    app.register_blueprint(bp)

    from .routes_user import user_bp
    app.register_blueprint(user_bp)

    # register new API blueprint for frontend
    from .routes_api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    return app


def _register_transport_security(app: Flask) -> None:
    require_https = bool(app.config.get("REQUIRE_HTTPS"))
    hsts_seconds = max(0, int(app.config.get("HSTS_SECONDS", 0) or 0))

    if require_https:
        @app.before_request
        def _force_https():
            if _request_is_secure(request):
                return None
            if request.method in ("GET", "HEAD", "OPTIONS"):
                secure_url = request.url.replace("http://", "https://", 1)
                return redirect(secure_url, code=301)
            return (
                jsonify(
                    {
                        "error": "https_required",
                        "message": "HTTPS is required for this endpoint.",
                    }
                ),
                400,
            )

    @app.after_request
    def _add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        if require_https and hsts_seconds:
            hsts_value = f"max-age={hsts_seconds}; includeSubDomains"
            if hsts_seconds >= 60 * 60 * 24 * 365:
                hsts_value += "; preload"
            response.headers.setdefault("Strict-Transport-Security", hsts_value)
        return response


def _request_is_secure(req: Request) -> bool:
    """Return True when the incoming request already traveled over HTTPS."""
    if req.is_secure:
        return True
    forwarded_proto = req.headers.get("X-Forwarded-Proto", "")
    if forwarded_proto:
        proto = forwarded_proto.split(",", 1)[0].strip().lower()
        if proto == "https":
            return True
    forwarded_ssl = req.headers.get("X-Forwarded-Ssl", "")
    if forwarded_ssl and forwarded_ssl.lower() == "on":
        return True
    return False
