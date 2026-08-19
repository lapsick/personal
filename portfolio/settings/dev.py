"""Local development settings: SQLite, DEBUG, console email backend."""

from .base import *  # noqa: F403
from .base import BASE_DIR

DEBUG = True

# Not a secret: development only. Production reads SECRET_KEY from the environment.
SECRET_KEY = "django-insecure-dev-only-key-do-not-use-in-production"  # noqa: S105

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # noqa: S104

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Print outgoing email to the console so the contact flow is observable locally.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "website@localhost"

# Faster, deterministic hashing for local test runs.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Serve static files from the finders in development so WhiteNoise works
# without a prior `collectstatic` (and does not warn about a missing root).
WHITENOISE_USE_FINDERS = True

try:
    from .local import *  # noqa: F403
except ImportError:
    pass
