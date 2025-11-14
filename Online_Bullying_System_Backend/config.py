import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _get_bool(env_key: str, default: bool = False) -> bool:
    value = os.getenv(env_key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = _get_bool("DEBUG", False)
    API_KEY = os.getenv("API_KEY")

    # File uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    AVATAR_SUBDIR = os.getenv("AVATAR_SUBDIR", "avatars")
    COMPLAINT_ATTACHMENT_SUBDIR = os.getenv("COMPLAINT_ATTACHMENT_SUBDIR", "complaints")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 32 * 1024 * 1024))  # allow up to ~32 MB

    # Mailer
    MAIL_ENABLED = _get_bool("MAIL_ENABLED", True)
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_USE_TLS = _get_bool("MAIL_USE_TLS", False)
    MAIL_USE_SSL = _get_bool("MAIL_USE_SSL", True)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
    MAIL_TIMEOUT = int(os.getenv("MAIL_TIMEOUT", 30))

    # Authentication + portal configuration
    PORTAL_LOGIN_URL = os.getenv("PORTAL_LOGIN_URL")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", 60 * 60 * 12))  # default 12 hours
    SESSION_MAX_IDLE_SECONDS = int(os.getenv("SESSION_MAX_IDLE_SECONDS", 60 * 60 * 2))  # 2 hours idle timeout
    SESSION_ROTATE_SECONDS = int(os.getenv("SESSION_ROTATE_SECONDS", 60 * 60 * 6))  # reissue token every 6h
    SESSION_TOKEN_BYTES = int(os.getenv("SESSION_TOKEN_BYTES", 48))
    TWO_FACTOR_CODE_LENGTH = int(os.getenv("TWO_FACTOR_CODE_LENGTH", 6))
    TWO_FACTOR_TTL_SECONDS = int(os.getenv("TWO_FACTOR_TTL_SECONDS", 10 * 60))
    TWO_FACTOR_MAX_ATTEMPTS = int(os.getenv("TWO_FACTOR_MAX_ATTEMPTS", 5))

    # Transport security / TLS
    REQUIRE_HTTPS = _get_bool("REQUIRE_HTTPS", False)
    SSL_CERT_PATH = os.getenv("SSL_CERT_PATH")
    SSL_KEY_PATH = os.getenv("SSL_KEY_PATH")
    SSL_KEY_PASSWORD = os.getenv("SSL_KEY_PASSWORD")
    SSL_CA_BUNDLE = os.getenv("SSL_CA_BUNDLE")
    HSTS_SECONDS = int(os.getenv("HSTS_SECONDS", 60 * 60 * 24 * 365))  # default 1 year
    PREFERRED_URL_SCHEME = "https" if REQUIRE_HTTPS else "http"
    SESSION_COOKIE_SECURE = _get_bool("SESSION_COOKIE_SECURE", REQUIRE_HTTPS)
    REMEMBER_COOKIE_SECURE = _get_bool("REMEMBER_COOKIE_SECURE", REQUIRE_HTTPS)
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Strict" if REQUIRE_HTTPS else "Lax")
    SESSION_COOKIE_HTTPONLY = _get_bool("SESSION_COOKIE_HTTPONLY", True)
