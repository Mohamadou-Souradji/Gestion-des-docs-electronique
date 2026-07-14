"""
Fichier de configuration principal du projet GED ESCEP-Niger.
Contient tous les reglages : base de données, applications, securite, etc.
"""

from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# SECURITE
# -------------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY')
DEBUG      = config('DEBUG', cast=bool)
ALLOWED_HOSTS = ['*']

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
    'rest_framework',           # API REST pour Vue.js
    'rest_framework_simplejwt', # Connexion par token JWT
    'corsheaders',              # Autorise Vue.js à communiquer avec Django
    # Nos applications
    'apps.users',       # Comptes et profils
    'apps.courriers',   # Cycle de vie des courriers
    'apps.archives',    # Archivage et recherche
    'apps.dashboard',   # Statistiques et audit (DG uniquement)
]

# -------------------------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Doit etre en premier
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
# BASE DE DONNEES - PostgreSQL via Docker
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
STATIC_URL = 'static/'
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

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
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# -------------------------------------------------------------------
# JWT - durée de vie des tokens
# -------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=8),  # Duree d'une journee de travail
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# -------------------------------------------------------------------
# CORS - autorise Vue.js à appeler Django
# -------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:5174',
]
# Autoriser l authentification par token dans l URL (pour les exports directs)
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
    'rest_framework_simplejwt.authentication.JWTAuthentication',
    'rest_framework.authentication.SessionAuthentication',
)


# -------------------------------------------------------------------
# EMAIL - Configuration pour la double authentification (2FA)
# Lire les paramètres depuis .env (changer en production avec SMTP réel)
# -------------------------------------------------------------------
from decouple import config as env_config

# Backend: par défaut SMTP, peut être remplacé par console en dev via .env
EMAIL_BACKEND       = env_config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST          = env_config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT          = env_config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS       = env_config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_HOST_USER     = env_config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env_config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = env_config('DEFAULT_FROM_EMAIL', default=env_config('EMAIL_HOST_USER', default='noreply@escep.ne'))
