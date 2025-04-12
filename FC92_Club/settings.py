"""
Django settings for FC92_Club project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""
import os
from pathlib import Path
import dj_database_url
from decouple import config, Csv  # Import Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

# Add CSRF_TRUSTED_ORIGINS, read from environment
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost:8000,http://127.0.0.1:8000', cast=Csv())

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
     # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',

    # Local apps
    'users.apps.UsersConfig',
    'finances.apps.FinancesConfig',
    'pages.apps.PagesConfig',
    'django.contrib.humanize',
    'gallery.apps.GalleryConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add Whitenoise middleware BELOW SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'FC92_Club.admin_access.AdminAccessMiddleware',  # Add our custom middleware
]

ROOT_URLCONF = 'FC92_Club.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),  # Make sure this points to your templates directory
        ],
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

WSGI_APPLICATION = 'FC92_Club.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Construct LOCAL_DB_URL using defaults for config() to avoid errors when env vars are missing
# These defaults are primarily for preventing errors during checks/imports on Heroku;
# the actual values from .env will be used locally if present.
LOCAL_DB_URL = f"postgres://{config('SQL_USER', default='localuser')}:{config('SQL_PASSWORD', default='localpass')}@localhost:{config('SQL_PORT', default='5433')}/{config('SQL_DATABASE', default='localdb')}"

# Let dj_database_url read DATABASE_URL directly from the environment (Heroku provides this)
# Use the constructed LOCAL_DB_URL as the fallback default for local development
DATABASES = {
    'default': dj_database_url.config(default=LOCAL_DB_URL, conn_max_age=600)
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Directory where collectstatic gathers files
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Your project's static files
]

# Add Whitenoise storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Create static directory if it doesn't exist
os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'staticfiles'), exist_ok=True)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Crispy Forms Settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login/Logout Redirects
LOGIN_REDIRECT_URL = 'pages:home'  # Redirect to home after login
LOGIN_URL = 'login'  # URL to redirect to for login
LOGOUT_REDIRECT_URL = 'pages:home'  # Redirect to home after logout

# Email Configuration
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'mailhog'  # Service name from docker-compose
    EMAIL_PORT = 1025       # MailHog SMTP port
    EMAIL_USE_TLS = False
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
else:
    # Production email settings (read from .env/Config Vars)
    EMAIL_HOST = config('EMAIL_HOST', default=None) # Provide default=None

    if EMAIL_HOST: # Only configure SMTP if EMAIL_HOST is actually set
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int) # Provide default
        EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='') # Provide default
        EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='') # Provide default
        EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool) # Provide default
        DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost') # Provide default
    else:
        # Fallback to console backend if EMAIL_HOST is not configured
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
        print("WARNING: EMAIL_HOST not set, using console email backend.") # Optional warning


# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = True  # Use only with HTTPS
SESSION_SAVE_EVERY_REQUEST = True

# CSRF Settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

# Configure Django App for Heroku
# Ensure django-heroku is not configuring settings automatically
# import django_heroku
# django_heroku.settings(locals())
