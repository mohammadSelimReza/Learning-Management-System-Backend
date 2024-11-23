from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lms_db',
        'USER': 'postgres',
        'PASSWORD': 'sr',
        'HOST': 'localhost',
        'PORT': '8912'
    }
}