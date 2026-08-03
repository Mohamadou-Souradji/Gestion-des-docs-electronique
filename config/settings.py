"""
Fichier de configuration principal du projet GED ESCEP-Niger.
Contient tous les reglages : base de données, applications, securite, etc.
"""

from pathlib import Path
from decouple import config
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# SECURITE
# -------------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY')
DEBUG      = config('DEBUG', cast=bool)
ALLOWED_HOSTS = ['*'] if DEBUG else [
    '.onrender.com',
    os.environ.get('RENDER_EXTERNAL_HOSTNAME', ''),
]
# -------------------------------------------------------------------
# APPLICATIONS INSTALLEES
# -------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Packages tiers
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'cloudinary',
    'cloudinary_storage',
    # Nos applications
    'apps.organisations',
    'apps.users',
    'apps.courriers',
    'apps.archives',
    'apps.dashboard',
]

# -------------------------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.organisations.middleware.TenantMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# -------------------------------------------------------------------
# BASE DE DONNEES
# -------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     config('DB_NAME'),
        'USER':     config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST'),
        'PORT':     config('DB_PORT'),
    }
}

# En production — utiliser DATABASE_URL de Render
import dj_database_url
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True,
    )

# -------------------------------------------------------------------
# VALIDATION DES MOTS DE PASSE
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------------------------
# LANGUE ET FUSEAU HORAIRE
# -------------------------------------------------------------------
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Africa/Niamey'
USE_I18N      = True
USE_TZ        = True

# -------------------------------------------------------------------
# FICHIERS STATIQUES ET MEDIA
# -------------------------------------------------------------------
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -------------------------------------------------------------------
# CLOUDINARY — stockage media en production
# -------------------------------------------------------------------
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', config('CLOUDINARY_CLOUD_NAME', default='')),
    'API_KEY':    os.environ.get('CLOUDINARY_API_KEY',    config('CLOUDINARY_API_KEY',    default='')),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', config('CLOUDINARY_API_SECRET', default='')),
}

if CLOUDINARY_STORAGE['CLOUD_NAME']:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# -------------------------------------------------------------------
# MODELE UTILISATEUR PERSONNALISE
# -------------------------------------------------------------------
AUTH_USER_MODEL    = 'users.Utilisateur'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------------------------
# DJANGO REST FRAMEWORK
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# -------------------------------------------------------------------
# JWT
# -------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------
_frontend = os.environ.get('FRONTEND_URL', '')
CORS_ALLOWED_ORIGINS = list(filter(None, [
    'http://localhost:5173',
    'http://localhost:5174',
    _frontend,
]))
CORS_ALLOW_CREDENTIALS = True
# -------------------------------------------------------------------
# EMAIL
# -------------------------------------------------------------------
from decouple import config as env_config

EMAIL_BACKEND       = env_config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST          = env_config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT          = env_config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS       = env_config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_HOST_USER     = env_config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env_config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = env_config('DEFAULT_FROM_EMAIL', default=env_config('EMAIL_HOST_USER', default='noreply@escep.ne'))