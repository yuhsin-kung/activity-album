"""
Django settings for activity_album project.
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────
# Security
# ──────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-0#u&epm*do@wzl2p$#dxe4&g)2%+h@duw@%63=-o10d^z3i_g^'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = ALLOWED_HOSTS_ENV.split(',') if ALLOWED_HOSTS_ENV else ['*', 'kryhhtoi.pythonanywhere.com']

# ──────────────────────────────────────────
# Application definition
# ──────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'albums',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # ← 靜態檔案
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'activity_album.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'activity_album.wsgi.application'

# ──────────────────────────────────────────
# Database
# ──────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL:
    # Railway PostgreSQL
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # 本機開發用 SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ──────────────────────────────────────────
# Password validation
# ──────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = []

# ──────────────────────────────────────────
# Internationalization
# ──────────────────────────────────────────
LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────
# Static files
# ──────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ──────────────────────────────────────────
# Media files (照片 & 附件)
# ──────────────────────────────────────────
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL', '')

if CLOUDINARY_URL:
    # Railway 上用 Cloudinary 儲存媒體檔案
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api

    cloudinary.config(cloudinary_url=CLOUDINARY_URL)

    DEFAULT_FILE_STORAGE = 'storages.backends.cloudinary.CloudinaryStorage'
    MEDIA_URL = '/media/'
else:
    # 本機用本地資料夾
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# ──────────────────────────────────────────
# Login
# ──────────────────────────────────────────
LOGIN_URL = '/accounts/login/'

CSRF_TRUSTED_ORIGINS = [
    'https://web-production-08513.up.railway.app',
]
