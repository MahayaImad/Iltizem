import os
from decouple import config
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================
SECRET_KEY = config('SECRET_KEY', default='dev-key-change-in-production-iltizem-2024')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,*.iltizem.dz').split(',')

# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

# Applications Django par défaut
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Pour formatage des nombres
]

# Applications tierces
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',  # Pour tokens API
    'corsheaders',
]

# Applications locales - CORRECTION: Préfixe 'apps.' ajouté
LOCAL_APPS = [
    'apps.accounts',  # ✅ CORRIGÉ: était 'accounts'
    'apps.associations',  # ✅ CORRIGÉ: était 'associations'
    'apps.cotisations',  # ✅ CORRIGÉ: était 'cotisations'
    'apps.paiements',  # ✅ CORRIGÉ: était 'paiements'
    'apps.notifications',  # ✅ CORRIGÉ: était 'notifications'
    'apps.rapports',  # ✅ CORRIGÉ: était 'rapports'
    'apps.residents',  # ✅ AJOUTÉ: manquait dans INSTALLED_APPS
    'apps.api',  # ✅ CORRIGÉ: était 'api'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ==============================================================================
# MIDDLEWARE CONFIGURATION
# ==============================================================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Pour l'internationalisation
]

ROOT_URLCONF = 'iltizem.urls'

# ==============================================================================
# AUTHENTICATION - CORRECTION CRITIQUE
# ==============================================================================
# ✅ AJOUTÉ: Configuration du modèle User personnalisé
AUTH_USER_MODEL = 'accounts.User'

# Configuration d'authentification
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ==============================================================================
# TEMPLATES CONFIGURATION
# ==============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # Pour fichiers media
                'django.template.context_processors.static',  # Pour fichiers static
            ],
        },
    },
]

WSGI_APPLICATION = 'iltizem.wsgi.application'

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='iltizem_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        }
    }
}

# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Algiers'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Formats de date français
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATE_FORMAT = 'd/m/Y'

# ==============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# ==============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Finders pour les fichiers statiques
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# ==============================================================================
# MEDIA FILES (Uploads)
# ==============================================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================================================
# DJANGO REST FRAMEWORK
# ==============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# CORS Configuration (pour API)
CORS_ALLOWED_ORIGINS = config('CORS_ORIGINS', default='http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@iltizem.dz')

# ==============================================================================
# CELERY CONFIGURATION (Tâches asynchrones)
# ==============================================================================
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Configuration des tâches périodiques
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Rappels quotidiens à 9h
    'rappels-quotidiens': {
        'task': 'apps.notifications.tasks.envoyer_rappels_automatiques',
        'schedule': crontab(hour=9, minute=0),
    },
    # Génération cotisations le 25 de chaque mois à 10h
    'generation-cotisations-mensuelles': {
        'task': 'apps.cotisations.tasks.generer_cotisations_automatiques',
        'schedule': crontab(day_of_month=25, hour=10, minute=0),
    },
    # Mise à jour statuts retard à 1h du matin
    'mise-a-jour-statuts-retard': {
        'task': 'apps.cotisations.tasks.mettre_a_jour_statuts_retard',
        'schedule': crontab(hour=1, minute=0),
    },
}

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'iltizem.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'] if not DEBUG else ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] if not DEBUG else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'iltizem': {
            'handlers': ['console', 'file'] if not DEBUG else ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# ==============================================================================
# iltizem CUSTOM SETTINGS
# ==============================================================================

# Thème Bootstrap - Couleurs identifiées dans votre projet
iltizem_THEME = {
    'colors': {
        'primary': '#06A3DA',
        'secondary': '#34AD54',
        'dark': '#091E3E',
        'light': '#EEF9FF',
        'body': '#6B6A75',
    },
    'name': 'iltizem Theme',
    'version': '1.0',
}

# Configuration des plans
iltizem_PLANS = {
    'basique': {
        'name': 'Plan Basique',
        'features': ['cotisations', 'paiements_manuels', 'emails', 'rapports_simple'],
        'max_logements': 50,
        'prix_mensuel': 0,  # Gratuit
    },
    'silver': {
        'name': 'Plan Silver',
        'features': ['cotisations', 'paiements_manuels', 'emails', 'rapports_simple',
                     'depenses', 'multi_admins', 'sms', 'export_excel'],
        'max_logements': 200,
        'prix_mensuel': 2000,  # 2000 DA
    },
    'gold': {
        'name': 'Plan Gold',
        'features': ['cotisations', 'paiements_manuels', 'emails', 'rapports_simple',
                     'depenses', 'multi_admins', 'sms', 'export_excel',
                     'paiement_en_ligne', 'sondages', 'statistiques_avancees'],
        'max_logements': 1000,
        'prix_mensuel': 5000,  # 5000 DA
    },
}

# Configuration SMS (pour plans Silver+)
SMS_PROVIDER = config('SMS_PROVIDER', default='local')  # local, twilio, etc.
SMS_API_KEY = config('SMS_API_KEY', default='')
SMS_SENDER_NAME = config('SMS_SENDER_NAME', default='iltizem')

# Configuration paiement en ligne (pour plan Gold)
CIB_MERCHANT_ID = config('CIB_MERCHANT_ID', default='')
CIB_SECRET_KEY = config('CIB_SECRET_KEY', default='')
EDAHABIA_MERCHANT_ID = config('EDAHABIA_MERCHANT_ID', default='')

# ==============================================================================
# DJANGO DEFAULT SETTINGS
# ==============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Session configuration
SESSION_COOKIE_AGE = 86400  # 24 heures
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG  # True en production

# Cache configuration (optionnel - pour améliorer les performances)
if config('REDIS_URL', default=None):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL'),
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# ==============================================================================
# ENVIRONMENT SPECIFIC SETTINGS
# ==============================================================================

# Development specific settings
if DEBUG:
    # Django Debug Toolbar (optionnel)
    try:
        import debug_toolbar

        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass

    # Email backend pour développement
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Production specific settings
else:
    # Force HTTPS
    SECURE_SSL_REDIRECT = True

    # Email backend pour production
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'