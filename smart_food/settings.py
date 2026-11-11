"""
Django settings for smart_food_ordering project.
"""

import os
import socket
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Try installing PyMySQL as MySQLdb for platforms without compiled mysqlclient
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', os.getenv('EMAIL_HOST_USER'))

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Correctly load GEMINI_API_KEY and GEMINI_MODEL from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'models/gemini-3.8-flash')

# ------------------------------
# SECURITY SETTINGS
# ------------------------------

# Use your ORIGINAL Django Secret Key
SECRET_KEY = 'd=91h2u!zy(_983z10qootrsflp(-gx01+49kebd%b!^#eymj(q)'
DEBUG = True
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',') if DEBUG else os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ------------------------------
# INSTALLED APPS
# ------------------------------
INSTALLED_APPS = [
    # Default Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your project apps
    'users',
    'menu',
    'orders',
    'payments',
    'analytics',
    'smart_features',
    'reviews',
    'chatbot',
]

# ------------------------------
# MIDDLEWARE
# ------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ------------------------------
# URLS AND TEMPLATES
# ------------------------------
ROOT_URLCONF = 'smart_food.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Your global templates folder
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

WSGI_APPLICATION = 'smart_food.wsgi.application'

# ------------------------------
# DATABASE CONFIGURATION
# ------------------------------
def _is_mysql_reachable(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        result = s.connect_ex((host, int(port)))
        s.close()
        return result == 0
    except Exception:
        return False

DB_ENGINE = os.getenv('DB_ENGINE', '').lower()
USE_SQLITE = os.getenv('USE_SQLITE', '').lower() in ('true', '1')

MYSQL_NAME = os.getenv('DB_NAME', 'smart_food_db')
MYSQL_USER = os.getenv('DB_USER', 'root')
MYSQL_PASSWORD = os.getenv('DB_PASSWORD', 'mYSQL908#2310')
MYSQL_HOST = os.getenv('DB_HOST', 'localhost')
MYSQL_PORT = os.getenv('DB_PORT', '3306')

if USE_SQLITE or DB_ENGINE == 'sqlite' or not _is_mysql_reachable(MYSQL_HOST, MYSQL_PORT):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': MYSQL_NAME,
            'USER': MYSQL_USER,
            'PASSWORD': MYSQL_PASSWORD,
            'HOST': MYSQL_HOST,
            'PORT': MYSQL_PORT,
        }
    }

# ------------------------------
# PASSWORD VALIDATION
# ------------------------------
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# ------------------------------
# INTERNATIONALIZATION
# ------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ------------------------------
# STATIC FILES
# ------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # For collectstatic in production

# ------------------------------
# MEDIA FILES (if needed)
# ------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ------------------------------
# DEFAULT PRIMARY KEY
# ------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'menu_home'

# ------------------------------
# LOGGING CONFIGURATION
# ------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'users': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}