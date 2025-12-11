from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ORIGIN_ALLOW_ALL = True


CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://172.22.80.1:3000",
    "http://192.168.1.70:3000",
]


STATIC_URL = "static/"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


CSRF_COOKIE_SAMESITE = "None"

DATABASES = {
    "default": {
        "ENGINE": config("DATABASE_ENGINE"),
        "NAME": config("DATABASE_NAME"),
        "USER": config("DATABASE_USERNAME"),
        "PASSWORD": config("DATABASE_PASSWORD"),
        "HOST": config("DATABASE_HOST"),
        "PORT": config("DATABASE_PORT", cast=int)
    }
}
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
print("⚠️ Using DEV settings")
