import django
from os import path


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = ['django_kadabra']

MIDDLEWARE_CLASSES = (
    'django_kadabra.middleware.KadabraMiddleware',
)

SECRET_KEY = 'test'
