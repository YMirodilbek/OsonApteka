from pathlib import Path
import environ
import os

env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
SECRET_KEY = env.str('SECRET_KEY')
ONSIGNAL_KEY = env.str('ONSIGNAL_KEY')

DEBUG = False
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'ckeditor',
    'django.contrib.admin',
     'django.contrib.postgres', 
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'rest_framework',
    'rest_framework_simplejwt',
    'main',
    'api',
    'drf_yasg',
    'Product',
    'click_up',
    'tmp'
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'AkmalFarm API',
    'DESCRIPTION': 'API Hujjatlari',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [
        {
            'TokenAuth': ['Bearer Token'],
        }
    ],
    'AUTHENTICATION_WHITELIST': [],
    'COMPONENTS': {
        'securitySchemes': {
            'TokenAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
            }
        }
    }
}

MIDDLEWARE = [
    'Admin.middleware.IPBlockMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
MIDDLEWARE.insert(0, 'Admin.middleware.RequestTimingMiddleware')  # yoki MIDDLEWARE ro'yxatiga qo'shing


ROOT_URLCONF = 'Admin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "Product.context_processors.category_contex"
            ],
        },
    },
]

WSGI_APPLICATION = 'Admin.wsgi.application'
DJANGO_ALLOW_ASYNC_UNSAFE = True

from .set_database import *

DATABASES = LOCAL_DATABASE

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'uz-uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tashkent'
CELERY_ENABLE_UTC = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'celery_task_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'celery_tasks.log'),
            'formatter': 'simple',
        },
        'main_app_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'main_app.log'),
            'formatter': 'verbose',
        },
        'product_app_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'product_app.log'),
            'formatter': 'verbose',
        },
        'click_up_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'click_up.log'),
            'formatter': 'verbose',
        },
        'tmp_app_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'tmp_app.log'),
            'formatter': 'verbose',
        },
        'django_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'celery_tasks': {
            'handlers': ['celery_task_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'main': {
            'handlers': ['main_app_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'Product': {
            'handlers': ['product_app_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'click_up': {
            'handlers': ['click_up_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'tmp': {
            'handlers': ['tmp_app_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['django_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['django_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'simple': {'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'},
#     },
#     'handlers': {
#         'file_perf': {
#             'level': 'INFO',
#             'class': 'logging.FileHandler',
#             'filename': '/var/www/oson_apteka/perf.log',
#             'formatter': 'simple',
#         },
#     },
#     'loggers': {
#         'perf': {
#             'handlers': ['file_perf'],
#             'level': 'INFO',
#             'propagate': False,
#         },
#     },
# }



CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['Table', 'HorizontalRule', 'Smiley', 'SpecialChar'],
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['TextColor', 'BGColor'],
            ['Maximize', 'ShowBlocks'],
            ['Source']
        ],
        'height': 400,
        'width': '100%',
        'extraPlugins': ','.join([
            'uploadimage',  # Rasm yuklash
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
        ]),
        'removePlugins': 'stylesheetparser',
        'allowedContent': True,
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'language': 'ru',  # Til sozlamasi
    }
}

LOGIN_URL = '/auth/send-otp/'

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

STATIC_URL = '/static/' 
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "main.CustomUser"
LOGIN_REDIRECT_URL = '/auth/send-otp/'

CLICK_SERVICE_ID = env.str('CLICK_SERVICE_ID')
CLICK_MERCHANT_ID = env.str('CLICK_MERCHANT_ID')
CLICK_SECRET_KEY = env.str('CLICK_SECRET_KEY')
CLICK_ACCOUNT_MODEL = "Product.models.Order"
CLICK_AMOUNT_FIELD = "amount"

CLICK_COMMISSION_PERCENT = 0
