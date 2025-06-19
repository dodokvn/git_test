import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


SECRET_KEY = ("django-insecure-_r7g5djd!tg#61&ngkt_-4k_9euvmyncvtvfs*9!wj^lhw&+85",)


DEBUG = True

ALLOWED_HOSTS = []


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "iradodo@gmail.com"
EMAIL_HOST_PASSWORD = "iradodo@gmail.com"  # <-- le mot de passe d'application
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
