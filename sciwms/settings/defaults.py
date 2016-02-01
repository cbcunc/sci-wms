#!python
# coding=utf-8
import os
import shutil
from datetime import timedelta

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

ADMINS = ()
MANAGERS = ADMINS
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "notasecret!")

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "db"))
if not os.path.isdir(db_path):
    os.makedirs(db_path)
old_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sci-wms.db"))
new_path = os.path.join(db_path, "sci-wms.db")
if os.path.exists(old_path) and not os.path.exists(new_path):
    shutil.move(old_path, new_path)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  new_path,
    }
}

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'wms',
    'wmsrest',
    'rest_framework',
    'djcelery'
]

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.static",
                "django.core.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.core.context_processors.request",
                "wms.context_processors.globals"
            ],
        },
    },
]

TESTING            = False
ROOT_URLCONF       = 'sciwms.urls'
WSGI_APPLICATION   = 'sciwms.wsgi.application'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
LANGUAGE_CODE      = 'en-us'
TIME_ZONE          = 'UTC'
USE_I18N           = False
USE_L10N           = False
USE_TZ             = True
STATIC_URL         = '/static/'
STATIC_ROOT        = os.path.join(BASE_DIR, 'static')
MEDIA_URL          = '/media/'
MEDIA_ROOT         = 'media'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_ACCESS': ('rest_framework.permissions.IsAdminUser',),
    'PAGINATE_BY': 10
}

# Celery
CELERY_ACCEPT_CONTENT    = ['json']
CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE          = 'UTC'
CELERYD_MAX_TASKS_PER_CHILD = 500
CELERY_IMPORTS = ('wms.tasks', )
CELERYBEAT_SCHEDULE = {
    'regulate': {
        'task': 'wms.tasks.regulate',
        'schedule': timedelta(hours=1)
    }
}

# Where to store the Topology data?
TOPOLOGY_PATH = os.path.join(BASE_DIR, "wms", "topology")
if not os.path.exists(TOPOLOGY_PATH):
    os.makedirs(TOPOLOGY_PATH)

# Used for showing log on the website
LOGFILE = None

import matplotlib  # noqa
matplotlib.use("Agg")
