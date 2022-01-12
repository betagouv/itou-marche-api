"""
Django settings for lemarche project.

Generated by 'django-admin startproject' using Django 3.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os

import environ
from django.contrib.messages import constants as messages


# django-environ eases the application of twelve-factor methodology :
# it makes it easier and less error-prone to integrate
# environment variables into Django application settings.
#
# https://www.12factor.net/
# https://django-environ.readthedocs.io/en/latest/
#
# "env" is the object that wil contain the defined environment, along some
# default settings
env = environ.Env(DEBUG=(bool, False), SECRET_KEY=(str, "SOME_SECRET_KEY"))

# Build paths inside the project like this: ROOT_DIR / 'subdir'.
ROOT_DIR = environ.Path(__file__) - 3  # (ROOT/config/settings/base.py - 3 = ROOT )
APPS_DIR = ROOT_DIR.path("lemarche")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)

ALLOWED_HOSTS = []

# Bitoubi env
BITOUBI_ENV = env.str("ENV", "dev")

# Static Files
STATIC_URL = "/static/"
# Path to the directory where collectstatic will collect static files for deployment.
STATIC_ROOT = os.path.join(APPS_DIR, "staticfiles")
STATICFILES_DIRS = (os.path.join(APPS_DIR, "static"),)
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_FINDERS += ["compressor.finders.CompressorFinder"]

COMPRESS_ENABLED = env.bool("COMPRESS_ENABLED", default=True)
COMPRESS_OFFLINE = True
COMPRESS_STORAGE = "compressor.storage.GzipCompressorFileStorage"
COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_PRECOMPILERS = [
    ("text/x-scss", "django_libsass.SassCompiler"),
]
LIBSASS_OUTPUT_STYLE = "compressed"

# Application definition

AUTH_USER_MODEL = "users.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

PRIORITY_APPS = [
    # Force whitenoise to serve assets in debug mode
    "whitenoise.runserver_nostatic"
]

DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "django.contrib.gis",
]

THIRD_PARTY_APPS = [
    "anymail",
    "django_filters",
    "bootstrap4",
    "rest_framework",
    "drf_spectacular",
    "compressor",
    "corsheaders",  # django-cors-headers
    "ckeditor",  # django-ckeditor
    "fieldsets_with_inlines",  # django-fieldsets-with-inlines
    "huey.contrib.djhuey",  # Async tasks lib
]

LOCAL_APPS = [
    # Core
    "lemarche.utils",
    "lemarche.cocorico",
    "lemarche.users",
    "lemarche.siaes",
    "lemarche.sectors",
    "lemarche.networks",
    "lemarche.perimeters",
    "lemarche.favorites",
    # Flatpages
    "lemarche.pages",
    # Api
    "lemarche.api",
]

INSTALLED_APPS = PRIORITY_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Third-party Middlewares
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Custom Middlewares
    "lemarche.utils.tracker.TrackerMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR.path("templates"))],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # custom
                "lemarche.utils.settings_context_processors.expose_settings",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"

# for review apps
# if none, will use Site.objects.get_current().domain instead
DEPLOY_URL = env.str("DEPLOY_URL", None)


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# Compatible with clevercloud add-ons
# TODO: Use django-environ DSN parsing functionality
# Something like env.db("POSTGRESQL_ADDON_URI")
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": env.str("POSTGRESQL_ADDON_HOST", "localhost"),
        "PORT": env.str("POSTGRESQL_ADDON_PORT", "5432"),
        "NAME": env.str("POSTGRESQL_ADDON_DB", "marche"),
        "USER": env.str("POSTGRESQL_ADDON_USER", "user"),
        "PASSWORD": env.str("POSTGRESQL_ADDON_PASSWORD", "password"),
    },
}


# Authentication
# ------------------------------------------------------------------------------

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "lemarche.utils.password_validation.CnilCompositionPasswordValidator"},
]

LOGIN_URL = "auth:login"
LOGIN_REDIRECT_URL = "pages:home"
LOGOUT_REDIRECT_URL = "pages:home"


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
# ------------------------------------------------------------------------------

# App is in french
LANGUAGE_CODE = "fr-fr"

# France timezone
TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1


# Emails
# ------------------------------------------------------------------------------

ANYMAIL = {
    "MAILJET_API_KEY": env.str("MAILJET_API_KEY", ""),
    "MAILJET_SECRET_KEY": env.str("MAILJET_API_SECRET", ""),
    # "WEBHOOK_SECRET": env.str("MAILJET_WEBHOOK_SECRET", ""),
}

MAILJET_API_URL = "https://api.mailjet.com/v3.1"

EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"

DEFAULT_FROM_EMAIL = "noreply@inclusion.beta.gouv.fr"
CONTACT_EMAIL = env("CONTACT_EMAIL", default="contact@example.com")
NOTIFY_EMAIL = env("NOTIFY_EMAIL", default="notif@example.com")


# Security
# ------------------------------------------------------------------------------

CSRF_COOKIE_HTTPONLY = True

CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

# Load the site over HTTPS only.
# TODO: use a small value for testing, once confirmed that HSTS didn't break anything increase it.
# https://docs.djangoproject.com/en/dev/ref/middleware/#http-strict-transport-security
SECURE_HSTS_SECONDS = 30

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SECURE = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

X_FRAME_OPTIONS = "DENY"

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGIN_REGEXES = [
    # local
    r"^http://localhost:[0-9]*$",
    r"^http://127.0.0.1:[0-9]*$",
    # deployed
    r"^https://\w+\.cleverapps\.io$",
    r"^https://\w+\.inclusion\.beta\.gouv\.fr$",
    r"^https://\w+\.beta\.gouv\.fr$",
    # API Swagger
    r"^https://\w+\.swagger\.io$",
    # API Gouv
    r"^https://\w+\.api\.gouv\.fr$",
    r"^https://\w+\.gouv\.fr$",
]


# S3 uploads
# ------------------------------------------------------------------------------

S3_STORAGE_ACCESS_KEY_ID = env.str("CELLAR_ADDON_KEY_ID", "")
S3_STORAGE_SECRET_ACCESS_KEY = env.str("CELLAR_ADDON_KEY_SECRET", "")
S3_STORAGE_ENDPOINT_DOMAIN = env.str("CELLAR_ADDON_HOST", "")
S3_STORAGE_BUCKET_NAME = env.str("S3_STORAGE_BUCKET_NAME", "")
S3_STORAGE_BUCKET_REGION = env.str("S3_STORAGE_BUCKET_REGION", "")

SIAE_LOGO_FOLDER_NAME = "siae_logo"
SIAE_IMAGE_FOLDER_NAME = "siae_image"
SIAE_CLIENT_REFERENCE_LOGO_FOLDER_NAME = "client_reference_logo"
USER_IMAGE_FOLDER_NAME = "user_image"
SIAE_EXPORT_FOLDER_NAME = "siae_export"

STORAGE_UPLOAD_KINDS = {
    "default": {
        "allowed_mime_types": ["image/png", "image/svg+xml", "image/gif", "image/jpg", "image/jpeg"],  # ["image/*"] ?
        "upload_expiration": 60 * 60,  # in seconds
        "key_path": "default",  # appended before the file key. No backslash!
        "max_files": 1,  # 3,
        "max_file_size": 5,  # in mb
        "timeout": 20000,  # in ms
    },
    "siae_logo": {
        "key_path": SIAE_LOGO_FOLDER_NAME,
    },
    "siae_image": {
        "key_path": SIAE_IMAGE_FOLDER_NAME,
    },
    "client_reference_logo": {
        "key_path": SIAE_CLIENT_REFERENCE_LOGO_FOLDER_NAME,
    },
    "user_image": {
        "key_path": USER_IMAGE_FOLDER_NAME,
    },
}


# APIs
# ------------------------------------------------------------------------------

API_PERIMETER_AUTOCOMPLETE_MAX_RESULTS = 20

# Base Adresse Nationale (BAN).
# https://adresse.data.gouv.fr/faq
API_BAN_BASE_URL = "https://api-adresse.data.gouv.fr"
# https://api.gouv.fr/api/api-geo.html#doc_tech
API_GEO_BASE_URL = "https://geo.api.gouv.fr"

# API Entreprise.
# https://dashboard.entreprise.api.gouv.fr/login (login is done through auth.api.gouv.fr)
# https://doc.entreprise.api.gouv.fr/
API_ENTREPRISE_BASE_URL = "https://entreprise.api.gouv.fr/v2"
API_ENTREPRISE_CONTEXT = "emplois.inclusion.beta.gouv.fr"
API_ENTREPRISE_RECIPIENT = env.str("API_ENTREPRISE_RECIPIENT", "")
API_ENTREPRISE_TOKEN = env.str("API_ENTREPRISE_TOKEN", "")

# API QPV
# API_QPV_RELATIVE_DAYS_TO_UPDATE is used to check last modification of SIAE.is_QPV
#   if SIAE.is_QPV was update after `today-API_QPV_RELATIVE_DAYS_TO_UPDATE`, we call the API to QPV
API_QPV_RELATIVE_DAYS_TO_UPDATE = env.int("API_QPV_RELATIVE_DAYS_TO_UPDATE", 60)

API_GOUV_URL = "https://api.gouv.fr/les-api/api-structures-inclusion"


# Django REST Framework (DRF)
# https://www.django-rest-framework.org/
# ------------------------------------------------------------------------------

REST_FRAMEWORK = {
    # YOUR SETTINGS
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
}


# DRF Spectacular
# https://drf-spectacular.readthedocs.io/en/latest/settings.html
# ------------------------------------------------------------------------------

API_DESCRIPTION = """
Une initiative de <a href="https://inclusion.beta.gouv.fr/" target="_blank" rel="noopener">
la Plateforme de l'inclusion</a>

Certaines ressources nécessitent un <strong>token</strong> pour accéder complètement à la donnée.<br />
Plus de détails pour l'obtenir <a href="https://lemarche.inclusion.beta.gouv.fr/api/#auth">ici</a>.
"""

SPECTACULAR_SETTINGS = {
    "TITLE": "API du marché de l'inclusion",
    "DESCRIPTION": API_DESCRIPTION,
    "VERSION": "1.0",
    "CONTACT": {
        "name": "Une question ? Contactez-nous via notre formulaire",
        "url": "https://lemarche.inclusion.beta.gouv.fr/contact/",
    },
    "ENUM_NAME_OVERRIDES": {
        "kind": "lemarche.siaes.models.Siae.KIND_CHOICES",
        "department": "lemarche.siaes.models.Siae.DEPARTMENT_CHOICES",
    },
    "SWAGGER_UI_SETTINGS": {"defaultModelsExpandDepth": -1},  # hide model schemas
}


# Trackers
# ------------------------------------------------------------------------------

TRACKER_HOST = env.str("TRACKER_HOST", "http://localhost")
HOTJAR_ID = int(env.str("HOTJAR_ID", 0))
MATOMO_SITE_ID = int(env.str("MATOMO_SITE_ID", 0))
MATOMO_HOST = env.str("MATOMO_HOST", "")
CRISP_ID = env.str("CRISP_ID", "")


# Metabase
# ------------------------------------------------------------------------------

METABASE_SITE_URL = "https://stats.inclusion.beta.gouv.fr"
METABASE_PUBLIC_DASHBOARD_ID = 137
METABASE_PUBLIC_DASHBOARD_UUID = "fdf2580a-aeea-441c-98fe-ef2c27e79d6b"
METABASE_PUBLIC_DASHBOARD_URL = f"{METABASE_SITE_URL}/embed/dashboard/{METABASE_PUBLIC_DASHBOARD_UUID}#titled=false"


# django-bootstrap4
# https://django-bootstrap4.readthedocs.io/en/latest/settings.html
# ------------------------------------------------------------------------------

BOOTSTRAP4 = {
    "required_css_class": "form-group-required",
    "set_placeholder": False,
    # Remove the default `.is-valid` class that Bootstrap will style in green
    # otherwise empty required fields will be marked as valid. This might be
    # a bug in django-bootstrap4, it should be investigated.
    "success_css_class": "",
}


# Connect Bootstrap alerts to Django message tags
# https://ordinarycoders.com/blog/article/django-messages-framework
# ------------------------------------------------------------------------------

MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}


# Logging
# https://docs.djangoproject.com/en/dev/topics/logging
# ------------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "null": {"class": "logging.NullHandler"},
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env.str("DJANGO_LOG_LEVEL", "INFO"),
        },
        # Silence `Invalid HTTP_HOST header` errors.
        # This should be done at the HTTP server level when possible.
        # https://docs.djangoproject.com/en/3.0/topics/logging/#django-security
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
        "lemarche": {
            "handlers": ["console"],
            "level": env.str("DJANGO_LOG_LEVEL", "DEBUG"),
        },
    },
}


# django-ckeditor
# https://django-ckeditor.readthedocs.io/en/latest/#optional-customizing-ckeditor-editor
# ------------------------------------------------------------------------------

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            ["Format", "Bold", "Italic", "Underline"],
            ["NumberedList", "BulletedList"],
            ["Link", "Unlink"],
            ["SpecialChar"],
            # ['HorizontalRule', 'Smiley'],
            ["Undo", "Redo"],
            ["RemoveFormat", "Source"],
        ],
        # avoid special characters encoding
        "basicEntities": False,
        "entities": False,
    }
}


# External URLs
# (if you need these settings in the template, add them to settings_context_processor.expose_settings)
# ------------------------------------------------------------------------------

FACILITATOR_SLIDE = "https://docs.google.com/presentation/d/e/2PACX-1vRd5lfQWHNEiUNw8yQqBfBnkGyaud5g440IsBvZm9XLEuawQNOfG91MwBlP24Z66A/pub?start=false&loop=false&delayms=3000&slide=id.p1"  # noqa
FACILITATOR_LIST = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRtavj-NHym5wjgDu9KRTIDPVZtujFlaSL9Z_BYQ7nWrmkcbGRuL12-VxiNctaOTsgdjQURuPLr57R/pubhtml"  # noqa


# Misc
# ------------------------------------------------------------------------------

# header env notice (not displayed in prod)
ENV_COLOR_MAPPING = {
    "dev": "#dc3545",  # red
    "review_app": "#fd7e14",  # orange
    "staging": "#ffc107",  # yellow
    "prod": "",
}
BITOUBI_ENV_COLOR = ENV_COLOR_MAPPING.get(BITOUBI_ENV, "")

# controls how many objects are updated in a single query
# avoid timeout exception
# https://docs.djangoproject.com/en/4.0/ref/models/querysets/#bulk-update
BATCH_SIZE_BULK_UPDATE = env.int("BATCH_SIZE_BULK_UPDATE", 200)

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", False)

# Async Configuration Options

# Huey / async
# Workers are run in prod via `CC_WORKER_COMMAND = django-admin run_huey`.
# ------------------------------------------------------------------------------

# Redis server URL:
# Provided by the Redis addon (itou-redis)
# Redis database to use with async (must be different for each environement)
# 1 <= REDIS_DB <= 100 (number of dbs available on CleverCloud)
REDIS_DB = env.int("REDIS_DB", 1)
# Complete URL (containing the instance password)
REDIS_URL = env.str("REDIS_URL", "localhost")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_PASSWORD = env.str("REDIS_PASSWORD", "")

CONNECTION_MODES_HUEY = {
    # immediate mode
    "direct": {"immediate": True},
    "sqlite": {
        "class_name": "huey.SqliteHuey",
        "connection": {"cache_mb": 8, "fsync": True},
    },
    # redis
    "redis": {
        "huey_class": "huey.RedisHuey",
        "connection": {"db": REDIS_DB, "host": REDIS_URL, "port": REDIS_PORT, "password": REDIS_PASSWORD},
    },
}

CONNECTION_MODE_TASKS = env.str("CONNECTION_MODE_TASKS", "sqlite")

CONF_HUEY = CONNECTION_MODES_HUEY.get("CONNECTION_MODE_TASKS", CONNECTION_MODES_HUEY["sqlite"])

# Huey instance
# If any performance issue, increasing the number of workers *can* be a good idea
# Parameter `immediate` means `synchronous` (async here)
HUEY = {
    "name": "ITOU_MARCHE",
    # Don't store task results (see our Redis Post-Morten in documentation for more information)
    "results": False,
    "huey_class": CONF_HUEY.get("class_name"),
    "immediate": CONF_HUEY.get("immediate", False),
    "connection": CONF_HUEY.get("connection"),
    "consumer": {"workers": 2, "worker_type": "thread"},
}
