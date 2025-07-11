from pathlib import Path
import os
import dj_database_url

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key: use env var in production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key')

# Debug mode: set to False in production
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Allowed hosts
ALLOWED_HOSTS = ['ets-production-c3dc.up.railway.app', 'localhost', '127.0.0.1']

# Custom user model
AUTH_USER_MODEL = 'Tracker.CustomUser'

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Tracker',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URL
ROOT_URLCONF = 'ExpenseTracker.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'Tracker' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'ExpenseTracker.wsgi.application'

# Database config
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3', conn_max_age=600)
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Login redirect
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Session
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 86400  # 1 day

# CSRF + HTTPS security
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
CSRF_TRUSTED_ORIGINS = ['https://ets-production-c3dc.up.railway.app']

# Default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'