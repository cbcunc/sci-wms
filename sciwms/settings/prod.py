#!python
# coding=utf-8
from .defaults import *

DEBUG          = False
TESTING        = False
TEMPLATES[0]['OPTIONS']['debug'] = False

ALLOWED_HOSTS  = ["*"]

LOGFILE = os.path.join(BASE_DIR, "logs", "sci-wms.log")
if not os.path.exists(os.path.dirname(LOGFILE)):
    os.makedirs(os.path.dirname(LOGFILE))

# Celery
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
BROKER_TRANSPORT_OPTIONS = {'fanout_patterns': True}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB' : 2,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
        }
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'backupCount': 5,
            'maxBytes': 1024*1024*20,  # 20MB
            'filename': LOGFILE,
            'formatter': 'verbose'
        },
        'syslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'syslog'],
            'level': 'WARNING',
            'propagate': True,
        },
        'celery': {
            'handlers': ['file', 'syslog'],
            'level': 'WARNING',
        },
        'celery.task': {
            'propagate': True,
        },
        'sciwms': {
            'handlers': ['file', 'syslog'],
            'level': 'WARNING',
            'propagate': True,
        },
        'wms': {
            'handlers': ['file', 'syslog'],
            'level': 'WARNING',
            'propagate': True,
        },
    }
}

LOCAL_APPS = ()
try:
    from local_settings import *
except ImportError:
    pass
try:
    from local.settings import *
except ImportError:
    pass
INSTALLED_APPS += LOCAL_APPS
