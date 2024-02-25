"""
Django settings for fuel_cards project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from .base import *
from .pg_credential import *

# REDIS settings
# docker pull redis:latest
# docker run -p 127.0.0.1:6379:6379 --name redis-celery -d redis
REDIS_HOST = 'redis'  # имя хоста Redis - имя контейнера Docker
REDIS_PORT = '6379'

# CELERY settings
# celery -A fuel_cards worker -l info
# celery -A fuel_cards beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
# celery -A fuel_cards beat -l info
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_TRANSPORT_OPTION = {'visibility_timeout': 3600}
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# MAIN settings
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = 'django-insecure-exj^ph&80h8aes)gjp@he!g)!pf9)_krl95@dy6bio!gosv-eg'
DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
        'HOST': DB_HOST,
        'PORT': '5432',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
    }
}