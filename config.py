import os

class Config:
    """Base configuration — switch DATABASE_URL to MySQL/PostgreSQL for production."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'traveloop-hackathon-2026-secret')

    # ── DATABASE ──────────────────────────────────────────────────────────
    # SQLite (demo/prototype) fallback, handle Render's postgres:// prefix
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'traveloop.db'))
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url

    # MySQL (production — uncomment and set credentials):
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/traveloop'

    # PostgreSQL (production — uncomment and set credentials):
    # SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/traveloop'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set True to see SQL queries in console

    # ── SECURITY ──────────────────────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True

    # ── VALIDATION RULES ──────────────────────────────────────────────────
    PASSWORD_MIN_LENGTH = 6
    NAME_MIN_LENGTH = 2
    NAME_MAX_LENGTH = 50
    TRIP_NAME_MAX_LENGTH = 100
