from .base import *

DEBUG = False

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": config("database_name"),
        "USER": config("database_user"),
        "PASSWORD": config("database_password"),
        "HOST": config("database_host"),
        "PORT": config("database_port"),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/django.log",
        },
    },
    "root": {
        "handlers": ["file"],
        "level": "INFO",
    },
}
