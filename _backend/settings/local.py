from .base import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "lms_db_backend",
        "USER": "postgres",
        "PASSWORD": "srreza",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
