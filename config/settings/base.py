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
    "ckeditor",  # django-ckeditor
    "fieldsets_with_inlines",  # django-fieldsets-with-inlines
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
    # Flatpages
    "lemarche.pages",
    # Api
    "lemarche.api",
]

INSTALLED_APPS = PRIORITY_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
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


# Authentication.
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

# API is in french
LANGUAGE_CODE = "fr-fr"

# France timezone
TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1


# Emails.
# ------------------------------------------------------------------------------

ANYMAIL = {
    "MAILJET_API_KEY": env.str("MAILJET_API_KEY", ""),
    "MAILJET_SECRET_KEY": env.str("MAILJET_API_SECRET", ""),
    # "WEBHOOK_SECRET": env.str("MAILJET_WEBHOOK_SECRET", ""),
}

MAILJET_API_URL = "https://api.mailjet.com/v3.1"

EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"

DEFAULT_FROM_EMAIL = "noreply@inclusion.beta.gouv.fr"
NOTIFY_EMAIL = env("NOTIFY_EMAIL", default="test@example.com")


# Security.
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


# S3 uploads
# ------------------------------------------------------------------------------
S3_STORAGE_ACCESS_KEY_ID = env.str("CELLAR_ADDON_KEY_ID", "")
S3_STORAGE_SECRET_ACCESS_KEY = env.str("CELLAR_ADDON_KEY_SECRET", "")
S3_STORAGE_ENDPOINT_DOMAIN = env.str("CELLAR_ADDON_HOST", "")
S3_STORAGE_BUCKET_NAME = env.str("S3_STORAGE_BUCKET_NAME", "")
S3_STORAGE_BUCKET_REGION = env.str("S3_STORAGE_BUCKET_REGION", "")

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
        "key_path": "siae_logo",
    },
    "client_reference_logo": {
        "key_path": "client_reference_logo",
    },
    "user_image": {
        "key_path": "user_image",
    },
}


# APIs.
# ------------------------------------------------------------------------------

# Base Adresse Nationale (BAN).
# https://adresse.data.gouv.fr/faq
API_BAN_BASE_URL = "https://api-adresse.data.gouv.fr"

# https://api.gouv.fr/api/api-geo.html#doc_tech
API_GEO_BASE_URL = "https://geo.api.gouv.fr"


# Django REST Framework settings.
# https://www.django-rest-framework.org/
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    # YOUR SETTINGS
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
}


# Spectacular settings.
# https://drf-spectacular.readthedocs.io/en/latest/settings.html
# ------------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Le marché de l'inclusion",
    "DESCRIPTION": """
[en construction]

Une initiative de la Plateforme de l'inclusion

Certaines ressources nécessitent un <strong>token</strong> pour accéder complètement à la donnée.
Vous pouvez en faire la demande via notre formulaire de contact.
    """,
    "VERSION": "0.1.0",
    "CONTACT": {
        "name": "Une question ? Contactez-nous en cliquand ici",
        "url": "https://lemarche.inclusion.beta.gouv.fr/contact/",
    },
    "ENUM_NAME_OVERRIDES": {
        "kind": "lemarche.siaes.models.Siae.KIND_CHOICES",
        "department": "lemarche.siaes.models.Siae.DEPARTMENT_CHOICES",
    },
}


# Trackers
# ------------------------------------------------------------------------------
TRACKER_HOST = env.str("TRACKER_HOST", "http://localhost")
HOTJAR_ID = int(env.str("HOTJAR_ID", 0))
MATOMO_SITE_ID = int(env.str("MATOMO_SITE_ID", 0))
MATOMO_HOST = env.str("MATOMO_HOST", "")
CRISP_ID = env.str("CRISP_ID", "")


# django-bootstrap4.
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


# Logging.
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


# django-ckeditor settings.
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
