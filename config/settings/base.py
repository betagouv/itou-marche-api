"""
Django settings for lemarche project.

Generated by 'django-admin startproject' using Django 3.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import locale
import os

import environ
import sib_api_v3_sdk
from django.contrib.messages import constants as messages


locale.setlocale(locale.LC_TIME, "")
# locale.setlocale(locale.LC_ALL, "fr_FR")
# this contig doesn't work, produce this error
# locale.Error: unsupported locale setting


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

# media files
MEDIA_ROOT = os.path.join(APPS_DIR, "media")
MEDIA_URL = "/media/"

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
    "django.contrib.humanize",
    "django.forms",
]

THIRD_PARTY_APPS = [
    "anymail",  # django-anymail
    "bootstrap4",  # django-bootstrap4
    "ckeditor",  # django-ckeditor
    "compressor",  # django-compressor
    "corsheaders",  # django-cors-headers
    "django_admin_filters",  # django-admin-list-filters
    "django_better_admin_arrayfield",  # django-better-admin-arrayfield
    "django_filters",  # django-filter
    "django_htmx",  # django-htmx
    "django_select2",  # django-select2
    "drf_spectacular",  # drf-spectacular
    "fieldsets_with_inlines",  # django-fieldsets-with-inlines
    "formtools",  # django-formtools (Multistep and preview forms)
    "huey.contrib.djhuey",  # huey (Async tasks)
    "rest_framework",  # djangorestframework
]

LOCAL_APPS = [
    # Core
    "lemarche.utils",
    "lemarche.cocorico",
    "lemarche.users",
    "lemarche.conversations",
    "lemarche.companies",
    "lemarche.siaes",
    "lemarche.sectors",
    "lemarche.networks",
    "lemarche.labels",
    "lemarche.perimeters",
    "lemarche.favorites",
    "lemarche.tenders",
    "lemarche.notes",
    "lemarche.cpv",
    # Flatpages
    "lemarche.pages",
    # API
    "lemarche.api",
    # Stats
    "lemarche.stats",
    # CMS (Wagtail)
    "lemarche.cms",
]

WAGTAIL_APPS = [
    "wagtail.contrib.routable_page",
    "wagtail.contrib.search_promotions",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    "storages",
]

INSTALLED_APPS = PRIORITY_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + WAGTAIL_APPS

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
    "django_htmx.middleware.HtmxMiddleware",
    # wagtail
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
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
# ------------------------------------------------------------------------------

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
    "stats": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env.str("STATS_POSTGRESQL_ADDON_HOST", "localhost"),
        "PORT": env.str("STATS_POSTGRESQL_ADDON_PORT", "5432"),
        "NAME": env.str("STATS_POSTGRESQL_ADDON_DB", "marchetracker"),
        "USER": env.str("STATS_POSTGRESQL_ADDON_USER", "itou"),
        "PASSWORD": env.str("STATS_POSTGRESQL_ADDON_PASSWORD", "password"),
    },
}
DATABASE_ROUTERS = ["config.settings.StatsRouter.StatsRouter"]


# controls how many objects are updated in a single query
# avoid timeout exception
# https://docs.djangoproject.com/en/4.0/ref/models/querysets/#bulk-update
BATCH_SIZE_BULK_UPDATE = env.int("BATCH_SIZE_BULK_UPDATE", 200)


# Authentication
# ------------------------------------------------------------------------------

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "sesame.backends.ModelBackend",
]

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
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# Django Sesame
# https://django-sesame.readthedocs.io/en/stable/index.html
# ------------------------------------------------------------------------------

SESAME_TOKEN_NAME = "token"


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

MAILJET_API_KEY = env.str("MAILJET_API_KEY", "")
MAILJET_API_SECRET = env.str("MAILJET_API_SECRET", "")
ANYMAIL = {
    "MAILJET_API_KEY": MAILJET_API_KEY,
    "MAILJET_SECRET_KEY": MAILJET_API_SECRET,
    # "WEBHOOK_SECRET": env.str("MAILJET_WEBHOOK_SECRET", ""),
}

MAILJET_API_URL = "https://api.mailjet.com/v3.1"

EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"

DEFAULT_FROM_EMAIL = "noreply@inclusion.beta.gouv.fr"
DEFAULT_FROM_NAME = "Marché de l'inclusion"
CONTACT_EMAIL = env("CONTACT_EMAIL", default="contact@example.com")
TEAM_CONTACT_EMAIL = env("TEAM_CONTACT_EMAIL", default="team.contact@example.com")
NOTIFY_EMAIL = env("NOTIFY_EMAIL", default="notif@example.com")
GIP_CONTACT_EMAIL = env("GIP_CONTACT_EMAIL", default="gip.contact@example.com")

# Transactional email templates
# -- user: new user password reset
MAILJET_NEW_USER_PASSWORD_RESET_ID = env.int("MAILJET_NEW_USER_PASSWORD_RESET_ID", 4216730)

# -- siae: completion
MAILJET_SIAE_COMPLETION_REMINDER_TEMPLATE_ID = env.int("MAILJET_SIAE_COMPLETION_REMINDER_TEMPLATE_ID", 4791779)

# -- siae: user invitation emails
MAILJET_SIAEUSERREQUEST_ASSIGNEE_TEMPLATE_ID = env.int("MAILJET_SIAEUSERREQUEST_ASSIGNEE_TEMPLATE_ID", 3658653)
MAILJET_SIAEUSERREQUEST_INITIATOR_RESPONSE_POSITIVE_TEMPLATE_ID = env.int(
    "MAILJET_SIAEUSERREQUEST_INITIATOR_RESPONSE_POSITIVE_TEMPLATE_ID", 3662344
)
MAILJET_SIAEUSERREQUEST_INITIATOR_RESPONSE_NEGATIVE_TEMPLATE_ID = env.int(
    "MAILJET_SIAEUSERREQUEST_INITIATOR_RESPONSE_NEGATIVE_TEMPLATE_ID", 3662592
)
MAILJET_SIAEUSERREQUEST_REMINDER_1_ASSIGNEE_TEMPLATE_ID = env.int(
    "MAILJET_SIAEUSERREQUEST_REMINDER_1_ASSIGNEE_TEMPLATE_ID", 3661739
)
MAILJET_SIAEUSERREQUEST_REMINDER_2_ASSIGNEE_TEMPLATE_ID = env.int(
    "MAILJET_SIAEUSERREQUEST_REMINDER_2_ASSIGNEE_TEMPLATE_ID", 3662063
)
MAILJET_SIAEUSERREQUEST_REMINDER_1_INITIATOR_TEMPLATE_ID = env.int(
    "MAILJET_SIAEUSERREQUEST_REMINDER_1_INITIATOR_TEMPLATE_ID", 3662658
)
MAILJET_SIAEUSERREQUEST_REMINDER_2_INITIATOR_TEMPLATE_ID = env.int(
    "MAILJET_SIAEUSERREQUEST_REMINDER_2_INITIATOR_TEMPLATE_ID", 3662684
)

# -- tender: siae & partners
MAILJET_TENDERS_PRESENTATION_TEMPLATE_ID = env.int("MAILJET_TENDERS_PRESENTATION_TEMPLATE_ID", 3679205)
MAILJET_TENDERS_PRESENTATION_TEMPLATE_PARTNERS_ID = env.int(
    "MAILJET_TENDERS_PRESENTATION_TEMPLATE_PARTNERS_ID", 3868179
)
MAILJET_TENDERS_CONTACTED_REMINDER_2D_TEMPLATE_ID = env.int(
    "MAILJET_TENDERS_CONTACTED_REMINDER_2D_TEMPLATE_ID", 4716371
)
MAILJET_TENDERS_CONTACTED_REMINDER_3D_TEMPLATE_ID = env.int(
    "MAILJET_TENDERS_CONTACTED_REMINDER_3D_TEMPLATE_ID", 4716387
)
MAILJET_TENDERS_CONTACTED_REMINDER_4D_TEMPLATE_ID = env.int(
    "MAILJET_TENDERS_CONTACTED_REMINDER_4D_TEMPLATE_ID", 4716426
)
MAILJET_TENDERS_INTERESTED_REMINDER_2D_TEMPLATE_ID = env.int(
    "MAILJET_TENDERS_INTERESTED_REMINDER_2D_TEMPLATE_ID", 4744896
)
# -- tender: author
MAILJET_TENDERS_AUTHOR_CONFIRMATION_PUBLISHED_TEMPLATE_ID = env.int(
    "MAILJET_TENDERS_AUTHOR_CONFIRMATION_PUBLISHED_TEMPLATE_ID", 3896680
)
MAILJET_TENDERS_SIAE_INTERESTED_1_TEMPLATE_ID = env.int("MAILJET_TENDERS_SIAE_INTERESTED_1_TEMPLATE_ID", 3867188)
MAILJET_TENDERS_SIAE_INTERESTED_2_TEMPLATE_ID = env.int("MAILJET_TENDERS_SIAE_INTERESTED_2_TEMPLATE_ID", 4306699)
MAILJET_TENDERS_SIAE_INTERESTED_5_TEMPLATE_ID = env.int("MAILJET_TENDERS_SIAE_INTERESTED_5_TEMPLATE_ID", 4306770)
MAILJET_TENDERS_SIAE_INTERESTED_5_MORE_TEMPLATE_ID = env.int(
    "MAILJET_TENDERS_SIAE_INTERESTED_5_MORE_TEMPLATE_ID", 3867200
)
MAILJET_TENDERS_AUTHOR_INCREMENTAL_2D_TEMPLATE_ID = env.int(
    "MAILJET_TENDERS_AUTHOR_INCREMENTAL_2D_TEMPLATE_ID", 4585824
)
MAILJET_TENDERS_AUTHOR_FEEDBACK_30D_TEMPLATE_ID = env.int("MAILJET_TENDERS_AUTHOR_FEEDBACK_30D_TEMPLATE_ID", 4017446)
MAILJET_TENDERS_AUTHOR_TRANSACTIONED_QUESTION_30D_TEMPLATE_ID = env.int(
    "MAILJET_TENDERS_AUTHOR_TRANSACTIONED_QUESTION_30D_TEMPLATE_ID", 4951625
)


# -- Sendinblue (BREVO)

BREVO_API_KEY = env.str("BREVO_API_KEY", "set-it")
brevo_configuration = sib_api_v3_sdk.Configuration()
brevo_configuration.api_key["api-key"] = BREVO_API_KEY
INBOUND_PARSING_DOMAIN_EMAIL = env.str("INBOUND_PARSING_DOMAIN_EMAIL", "reply.staging.lemarche.inclusion.beta.gouv.fr")

INBOUND_EMAIL_IS_ACTIVATED = env.bool("INBOUND_EMAIL_IS_ACTIVATED", True)

# -- hubspot
HUBSPOT_API_KEY = env.str("HUBSPOT_API_KEY", "set-it")
HUBSPOT_IS_ACTIVATED = env.bool("HUBSPOT_IS_ACTIVATED", False)

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

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", False)

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

CSRF_FAILURE_VIEW = "lemarche.www.pages.views.csrf_failure"


# S3 uploads
# ------------------------------------------------------------------------------

S3_STORAGE_ACCESS_KEY_ID = env.str("CELLAR_ADDON_KEY_ID", "123")
S3_STORAGE_SECRET_ACCESS_KEY = env.str("CELLAR_ADDON_KEY_SECRET", "secret")
S3_STORAGE_ENDPOINT_DOMAIN = env.str("CELLAR_ADDON_HOST", "http://set-var-env.com/")
S3_STORAGE_BUCKET_NAME = env.str("S3_STORAGE_BUCKET_NAME", "set-bucket-name")
S3_STORAGE_BUCKET_REGION = env.str("S3_STORAGE_BUCKET_REGION", "fr")
AWS_DEFAULT_ACL = env.str("AWS_DEFAULT_ACL", "public-read")
AWS_S3_USE_SSL = env.bool("AWS_S3_USE_SSL", False)

SIAE_LOGO_FOLDER_NAME = "siae_logo"
SIAE_IMAGE_FOLDER_NAME = "siae_image"
SIAE_CLIENT_REFERENCE_LOGO_FOLDER_NAME = "client_reference_logo"
USER_IMAGE_FOLDER_NAME = "user_image"
SIAE_EXPORT_FOLDER_NAME = "siae_export"
STAT_EXPORT_FOLDER_NAME = "stat_export"

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

# API Mailjet
# We also use the master api key (with the second api key), because we separate the sending message from application
#   and from human peoples.
MAILJET_MASTER_API_KEY = env.str("MAILJET_MASTER_API_KEY", "")
MAILJET_MASTER_API_SECRET = env.str("MAILJET_MASTER_API_SECRET", "")
# ID of buyers contact list
MAILJET_NL_CL_BUYER_ID = env.int("MAILJET_NL_CL_BUYER_ID", 2546565)
MAILJET_NL_CL_BUYER_TENDER_ID = env.int("MAILJET_NL_CL_BUYER_TENDER_ID", 2546564)
MAILJET_NL_CL_BUYER_TALLY_ID = env.int("MAILJET_NL_CL_BUYER_TALLY_ID", 2546566)
MAILJET_NL_CL_SIAE_ID = env.int("MAILJET_NL_CL_SIAE_ID", 2500034)
# contact list "Facilitateurs des clauses sociales"
MAILJET_NL_CL_PARTNER_FACILITATORS_ID = env.int("MAILJET_NL_CL_PARTNER_FACILITATORS_ID", 2500034)
# contact list "Réseaux IAE" et "Réseau secteur handicap"
MAILJET_NL_CL_PARTNER_NETWORKS_IAE_HANDICAP_ID = env.int("MAILJET_NL_CL_PARTNER_NETWORKS_IAE_HANDICAP_ID", 2500034)
# contact list "DREETS/DDETS"
MAILJET_NL_CL_PARTNER_DREETS_ID = env.int("MAILJET_NL_CL_PARTNER_DREETS_ID", 2500034)
# contact list "acheteurs ayant téléchargés la liste excel des structures"
MAILJET_NL_CL_BUYER_DOWNLOAD_SIAE_LIST_ID = env.int("MAILJET_NL_CL_BUYER_DOWNLOAD_SIAE_LIST_ID", 2500034)
# contact list "acheteurs ayant recherchés des structures"
MAILJET_NL_CL_BUYER_SEARCH_SIAE_LIST_ID = env.int("MAILJET_NL_CL_BUYER_SEARCH_SIAE_LIST_ID", 2504377)
# contact list "acheteurs ayant recherchés des structures 'traiteur'"
MAILJET_NL_CL_BUYER_SEARCH_SIAE_TRAITEUR_LIST_ID = env.int("MAILJET_NL_CL_BUYER_SEARCH_SIAE_TRAITEUR_LIST_ID", 2543033)
# contact list "acheteurs ayant recherchés des structures 'nettoyage'"
MAILJET_NL_CL_BUYER_SEARCH_SIAE_NETTOYAGE_LIST_ID = env.int(
    "MAILJET_NL_CL_BUYER_SEARCH_SIAE_NETTOYAGE_LIST_ID", 2543034
)
# contact list import c1
MAILJET_NL_CL_IMPORT_C1_SIAE_LIST_ID = env.int("MAILJET_NL_CL_IMPORT_C1_SIAE_LIST_ID", 2502857)

# API Slack
SLACK_NOTIF_IS_ACTIVE = env.bool("SLACK_NOTIF_IS_ACTIVE", False)
SLACK_WEBHOOK_C4_CHANNEL = env.str("SLACK_WEBHOOK_C4_CHANNEL", "set-it")
SLACK_WEBHOOK_C4_SUPPORT_CHANNEL = env.str("SLACK_WEBHOOK_C4_SUPPORT_CHANNEL", "set-it")

# API Marché APProch
MARCHE_APPROCH_TOKEN_RECETTE = env.str("MARCHE_APPROCH_TOKEN_RECETTE", "set-it")


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
Une documentation alternative de l'API est aussi disponible
<a href="https://lemarche.inclusion.beta.gouv.fr/api/redoc/">ici</a>.

Certaines ressources nécessitent un <strong>token</strong> pour accéder complètement à la donnée.<br />
Plus de détails pour l'obtenir <a href="https://lemarche.inclusion.beta.gouv.fr/api/#auth">ici</a>.

Une initiative de <a href="https://inclusion.beta.gouv.fr/" target="_blank" rel="noopener">
la Plateforme de l'inclusion</a>

<a href="https://lemarche.inclusion.beta.gouv.fr/cgu-api/">Conditions générales d'utilisation</a>
"""

SPECTACULAR_SETTINGS = {
    "TITLE": "API du marché de l'inclusion",
    "DESCRIPTION": API_DESCRIPTION,
    "VERSION": "1.0",
    "CONTACT": {
        "name": "Une question ? Contactez-nous via notre formulaire",
        "url": "https://lemarche.inclusion.beta.gouv.fr/contact/",
    },
    "PREPROCESSING_HOOKS": ["lemarche.api.utils.custom_preprocessing_hook"],
    "ENUM_NAME_OVERRIDES": {
        "kind": "lemarche.siaes.constants.KIND_CHOICES",
        "department": "lemarche.siaes.models.Siae.DEPARTMENT_CHOICES",
    },
    "SWAGGER_UI_SETTINGS": {"defaultModelsExpandDepth": -1},  # hide model schemas
}


# Trackers
# ------------------------------------------------------------------------------

HOTJAR_ID = int(env.str("HOTJAR_ID", 0))
MATOMO_SITE_ID = int(env.str("MATOMO_SITE_ID", 0))
MATOMO_HOST = env.str("MATOMO_HOST", "")
MATOMO_TAG_MANAGER_CONTAINER_ID = env.str("MATOMO_TAG_MANAGER_CONTAINER_ID", "")
CRISP_ID = env.str("CRISP_ID", "")


# Metabase
# ------------------------------------------------------------------------------

METABASE_SITE_URL = "https://stats.inclusion.beta.gouv.fr"
METABASE_PUBLIC_DASHBOARD_UUID = "44326ea9-e67c-45fc-9603-831a7dad1c8c"
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


# Async Configuration Options: Huey
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
        "immediate": False,
        "connection": {"cache_mb": 8, "fsync": True},
    },
    # redis
    "redis": {
        "class_name": "huey.RedisHuey",
        "immediate": False,
        "connection": {"db": REDIS_DB, "host": REDIS_URL, "port": REDIS_PORT, "password": REDIS_PASSWORD},
    },
}

CONNECTION_MODE_TASKS = env.str("CONNECTION_MODE_TASKS", "direct")
CC_WORKER_ENV = env.str("CC_WORKER_COMMAND", None)

CONF_HUEY = CONNECTION_MODES_HUEY.get(CONNECTION_MODE_TASKS)

# Huey instance
# If any performance issue, increasing the number of workers *can* be a good idea
# Parameter `immediate` means `synchronous` (async here)
HUEY = {
    "name": "ITOU_MARCHE",
    # Don't store task results (see our Redis Post-Morten in documentation for more information)
    "immediate": CONF_HUEY.get("immediate") or not CC_WORKER_ENV,
    "results": False,
}

# if the sqlite mode or redis is set, we need to define the var env CC_WORKER to enable async jobs on CleverCloud
if CONNECTION_MODE_TASKS in ("sqlite", "redis") and CC_WORKER_ENV:
    HUEY |= {
        "huey_class": CONF_HUEY.get("class_name"),
        "connection": CONF_HUEY.get("connection"),
        "consumer": {"workers": 2, "worker_type": "thread"},
    }


# Caching
# https://docs.djangoproject.com/en/4.0/topics/cache/
# ------------------------------------------------------------------------------

# Simple DB caching, we need it for Select2 (don't ask me why...)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    }
}

SELECT2_CACHE_BACKEND = "default"


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

DEFAULT_CKEDITOR_CONFIG = {
    "toolbar": "Custom",
    "toolbar_Custom": [
        ["Format", "Bold", "Italic", "Underline"],
        ["NumberedList", "BulletedList"],
        ["Link", "Unlink"],
        ["SpecialChar"],
        # ['HorizontalRule', 'Smiley'],
        ["Undo", "Redo"],
        ["Image", "Flash", "Table", "HorizontalRule", "Smiley", "SpecialChar", "Iframe"],
        ["RemoveFormat", "Source"],
    ],
    # avoid special characters encoding
    "basicEntities": False,
    "entities": False,
}

CKEDITOR_CONFIGS = {
    "default": DEFAULT_CKEDITOR_CONFIG,
    "admin_note_text": DEFAULT_CKEDITOR_CONFIG | {"height": 100},
}


# External URLs
# (if you need these settings in the template, add them to settings_context_processor.expose_settings)
# ------------------------------------------------------------------------------

FACILITATOR_SLIDE = "https://docs.google.com/presentation/d/e/2PACX-1vRd5lfQWHNEiUNw8yQqBfBnkGyaud5g440IsBvZm9XLEuawQNOfG91MwBlP24Z66A/pub?start=false&loop=false&delayms=3000&slide=id.p1"  # noqa
FACILITATOR_LIST = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRtavj-NHym5wjgDu9KRTIDPVZtujFlaSL9Z_BYQ7nWrmkcbGRuL12-VxiNctaOTsgdjQURuPLr57R/pubhtml"  # noqa
TYPEFORM_BESOIN_ACHAT = "https://itou.typeform.com/to/KWViHaph"
TYPEFORM_BESOIN_ACHAT_RECHERCHE = "https://itou.typeform.com/to/nxG0HlYx"
TYPEFORM_GROUPEMENT_AJOUT = "https://itou.typeform.com/to/AENCiOWD"
FORM_PARTENAIRES = (
    "https://docs.google.com/forms/d/e/1FAIpQLScx1k-UJ-962_rSgPJGabc327gGjFUho6ypgcZHCubuwTl7Lg/viewform"
)
TALLY_NPS_FORM_ID = env.str("TALLY_NPS_FORM_ID", "")


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


# Wagtail
# ------------------------------------------------------------------------------

WAGTAIL_SITE_NAME = "Le Marché"

WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

SITE_ID = 1

WAGTAIL_RICHTEXT_FIELD_FEATURES = [
    "h2",
    "h3",
    "bold",
    "italic",
    "link",
    "image",
    "embed",
]

WAGTAILEMBEDS_RESPONSIVE_HTML = True

WAGTAILADMIN_BASE_URL = DEPLOY_URL or "http://localhost/"


# Shell Plus (django-extensions)
# ------------------------------------------------------------------------------

SHELL_PLUS_POST_IMPORTS = [
    "from lemarche.utils import constants",
    "from lemarche.siaes import constants as siae_constants",
    "from lemarche.tenders import constants as tender_constants",
]
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# MTCAPTCHA
# ------------------------------------------------------------------------------
MTCAPTCHA_PRIVATE_KEY = env.str("MTCAPTCHA_PRIVATE_KEY", "")
MTCAPTCHA_PUBLIC_KEY = env.str("MTCAPTCHA_PUBLIC_KEY", "")
