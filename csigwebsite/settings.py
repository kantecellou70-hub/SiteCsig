

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=%vyebcd3ji7gvqxr=7jxhlno!^g3*77_-vl%0ec6p332mbetn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_ckeditor_5',
    'sfront',
    'content_management',
    'users',
    'oauth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'csigwebsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'csigwebsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd672frb1qrepab',
        'USER': 'udm5hhg4g373g',
        'PASSWORD': 'p0fcb6f00dda197180b72ba49623bc95c53b5ef8a132964b319634d5d33a5eca5',
        'HOST': 'c34u0gd6rbe7bo.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
       
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'Africa/Conakry'

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site ID
SITE_ID = 1


import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


AWS_STORAGE_BUCKET_NAME = 'csigs3'
AWS_S3_REGION_NAME = 'eu-north-1'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# Custom User Model
AUTH_USER_MODEL = 'users.User'
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
# En-têtes de sécurité
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies sécurisés
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Login URLs
LOGIN_URL = '/oauth/login/'
LOGIN_REDIRECT_URL = '/content-management/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# CKEditor 5 Configuration
customColorPalette = [
    {"color": "0d4786", "label": "CSIG Blue"},
    {"color": "ffffff", "label": "White"},
    {"color": "f8f9fa", "label": "Light Gray"},
    {"color": "6c757d", "label": "Dark Gray"},
    {"color": "28a745", "label": "Green"},
    {"color": "dc3545", "label": "Red"},
    {"color": "ffc107", "label": "Yellow"},
    {"color": "17a2b8", "label": "Info"},
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                   'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
    },
    'blog_content': {
        'toolbar': {
            'items': [
                'heading', '|',
                'bold', 'italic', 'underline', 'strikethrough', '|',
                'link', '|',
                'bulletedList', 'numberedList', '|',
                'indent', 'outdent', '|',
                'blockQuote', 'insertTable', '|',
                'undo', 'redo'
            ]
        },
        'language': 'fr',
        'placeholder': 'Commencez à écrire votre contenu...',
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraphe', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Titre 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Titre 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Titre 3', 'class': 'ck-heading_heading3'},
                {'model': 'heading4', 'view': 'h4', 'title': 'Titre 4', 'class': 'ck-heading_heading4'}
            ]
        },
        'table': {
            'contentToolbar': [
                'tableColumn',
                'tableRow',
                'mergeTableCells'
            ]
        },
        'link': {
            'addTargetToExternalLinks': True,
            'defaultProtocol': 'https://'
        }
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                   'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                   'bulletedList', 'numberedList', 'todoList', '|', 'blockQuote', 'imageInsert', 'insertTable', 'mediaEmbed',
                   '|', 'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|', 'alignment', '|',
                   'horizontalLine', '|', 'pageBreak', '|', 'textPartLanguage', '|', 'linkImage', '|', 'specialCharacters'],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                       'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side', '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': [
                'tableColumn',
                'tableRow',
                'mergeTableCells'
            ]
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
                {'model': 'heading4', 'view': 'h4', 'title': 'Heading 4', 'class': 'ck-heading_heading4'},
                {'model': 'heading5', 'view': 'h5', 'title': 'Heading 5', 'class': 'ck-heading_heading5'},
                {'model': 'heading6', 'view': 'h6', 'title': 'Heading 6', 'class': 'ck-heading_heading6'}
            ]
        }
    }
}

# ============================================================================
# CONFIGURATION CELERY ET REDIS
# ============================================================================

# Ajouter l'application jobs
INSTALLED_APPS += ['jobs', 'django_celery_results']

# Configuration Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Configuration des tâches Celery
CELERY_TASK_ROUTES = {
    'jobs.tasks.send_newsletter_email': {'queue': 'newsletter'},
    'jobs.tasks.send_bulk_newsletter': {'queue': 'newsletter'},
    'jobs.tasks.send_scheduled_newsletter': {'queue': 'newsletter'},
}

# Configuration des workers
CELERY_WORKER_CONCURRENCY = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_TIME_LIMIT = 3600  # 1 heure
CELERY_TASK_SOFT_TIME_LIMIT = 3000  # 50 minutes

# ============================================================================
# CONFIGURATION EMAIL (GMAIL)
# ============================================================================

# Configuration email pour Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Ces informations doivent être configurées dans les variables d'environnement
# ou dans un fichier .env pour la sécurité
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'support@csig.edu.gn'
EMAIL_HOST_PASSWORD = 'yhmffdfjgqgkyltg'

# Configuration du site
SITE_URL = 'http://localhost:8000'  # À modifier selon votre configuration

# ============================================================================
# CONFIGURATION LOGGING
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'jobs': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Créer le dossier logs s'il n'existe pas
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
