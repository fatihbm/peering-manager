# DO NOT EDIT THIS FILE!
#
# All configuration must be done in the `configuration.py` file.
# This file is part of the Peering Manager code and it will be overwritten with
# every code releases.


import os
import socket

from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured

try:
    from peering_manager import configuration
except ImportError:
    raise ImproperlyConfigured(
        "Configuration file is not present. Please define peering_manager/configuration.py per the documentation."
    )

VERSION = "v1.1.1-dev"
DEFAULT_LOGGING = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(asctime)s | %(levelname)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logs/peering-manager.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 5,
            "formatter": "simple",
        },
        "peeringdb_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logs/peeringdb.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 5,
            "formatter": "simple",
        },
        "napalm_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logs/napalm.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 5,
            "formatter": "simple",
        },
        "netbox_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logs/netbox.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 5,
            "formatter": "simple",
        },
    },
    "loggers": {
        "peering.manager.peering": {"handlers": ["file"], "level": "DEBUG"},
        "peering.manager.peeringdb": {"handlers": ["peeringdb_file"], "level": "DEBUG"},
        "peering.manager.napalm": {"handlers": ["napalm_file"], "level": "DEBUG"},
        "peering.manager.netbox": {"handlers": ["netbox_file"], "level": "DEBUG"},
    },
}

DATABASE = SECRET_KEY = ALLOWED_HOSTS = MY_ASN = None
for setting in ["DATABASE", "SECRET_KEY", "ALLOWED_HOSTS", "MY_ASN"]:
    try:
        globals()[setting] = getattr(configuration, setting)
    except AttributeError:
        raise ImproperlyConfigured(
            "Mandatory setting {} is not in the configuration.py file.".format(setting)
        )

CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS

BASE_PATH = getattr(configuration, "BASE_PATH", "")
if BASE_PATH:
    BASE_PATH = BASE_PATH.strip("/") + "/"  # Enforce trailing slash only
DEBUG = getattr(configuration, "DEBUG", False)
LOGGING = getattr(configuration, "LOGGING", DEFAULT_LOGGING)
CHANGELOG_RETENTION = getattr(configuration, "CHANGELOG_RETENTION", 90)
LOGIN_REQUIRED = getattr(configuration, "LOGIN_REQUIRED", False)
NAPALM_USERNAME = getattr(configuration, "NAPALM_USERNAME", "")
NAPALM_PASSWORD = getattr(configuration, "NAPALM_PASSWORD", "")
NAPALM_TIMEOUT = getattr(configuration, "NAPALM_TIMEOUT", 30)
NAPALM_ARGS = getattr(configuration, "NAPALM_ARGS", {})
PAGINATE_COUNT = getattr(configuration, "PAGINATE_COUNT", 20)
TIME_ZONE = getattr(configuration, "TIME_ZONE", "UTC")
EMAIL = getattr(configuration, "EMAIL", {})
BGPQ3_PATH = getattr(configuration, "BGPQ3_PATH", "bgpq3")
BGPQ3_HOST = getattr(configuration, "BGPQ3_HOST", "rr.ntt.net")
BGPQ3_SOURCES = getattr(
    configuration,
    "BGPQ3_SOURCES",
    "RIPE,APNIC,AFRINIC,ARIN,NTTCOM,ALTDB,BBOI,BELL,JPIRR,LEVEL3,RADB,RGNET,TC",
)
BGPQ3_ARGS = getattr(
    configuration,
    "BGPQ3_ARGS",
    {"ipv6": ["-r", "16", "-R", "48"], "ipv4": ["-r", "8", "-R", "24"]},
)

# Pagination
PER_PAGE_SELECTION = [25, 50, 100, 250, 500, 1000]
if PAGINATE_COUNT not in PER_PAGE_SELECTION:
    PER_PAGE_SELECTION.append(PAGINATE_COUNT)
    PER_PAGE_SELECTION = sorted(PER_PAGE_SELECTION)


# Django filters
FILTERS_NULL_CHOICE_LABEL = "-- None --"
FILTERS_NULL_CHOICE_VALUE = "null"


# Use major.minor as API version
REST_FRAMEWORK_VERSION = VERSION[0:3]
REST_FRAMEWORK = {
    "DEFAULT_VERSION": REST_FRAMEWORK_VERSION,
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.AcceptHeaderVersioning",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "peering_manager.api.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["peering_manager.api.TokenPermissions"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": PAGINATE_COUNT,
}


# Case insensitive search for tags
TAGGIT_CASE_INSENSITIVE = True


# NetBox API configuration
NETBOX_API = getattr(configuration, "NETBOX_API", "")
NETBOX_API_TOKEN = getattr(configuration, "NETBOX_API_TOKEN", "")
NETBOX_DEVICE_ROLES = getattr(
    configuration, "NETBOX_DEVICE_ROLES", ["router", "firewall"]
)

# PeeringDB URLs
PEERINGDB_API = "https://peeringdb.com/api/"
PEERINGDB = "https://peeringdb.com/asn/"
PEERINGDB_USERNAME = getattr(configuration, "PEERINGDB_USERNAME", "")
PEERINGDB_PASSWORD = getattr(configuration, "PEERINGDB_PASSWORD", "")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


try:
    from peering_manager.ldap_config import *

    LDAP_CONFIGURED = True
except ImportError:
    LDAP_CONFIGURED = False

# If LDAP is configured, load the config
if LDAP_CONFIGURED:
    try:
        import ldap
        import django_auth_ldap

        # Prepend LDAPBackend to the default ModelBackend
        AUTHENTICATION_BACKENDS = [
            "django_auth_ldap.backend.LDAPBackend",
            "django.contrib.auth.backends.ModelBackend",
        ]
    except ImportError:
        raise ImproperlyConfigured(
            "LDAP authentication has been configured, but django-auth-ldap is not installed. You can remove peering_manager/ldap_config.py to disable LDAP."
        )


# Force PostgreSQL to be used as database backend
configuration.DATABASE.update({"ENGINE": "django.db.backends.postgresql"})
# Actually set the database's settings
DATABASES = {"default": configuration.DATABASE}


# Email
if EMAIL:
    EMAIL_HOST = EMAIL.get("SERVER")
    EMAIL_PORT = EMAIL.get("PORT", 25)
    EMAIL_HOST_USER = EMAIL.get("USERNAME")
    EMAIL_HOST_PASSWORD = EMAIL.get("PASSWORD")
    EMAIL_TIMEOUT = EMAIL.get("TIMEOUT", 10)
    SERVER_EMAIL = EMAIL.get("FROM_ADDRESS")
    EMAIL_SUBJECT_PREFIX = EMAIL.get("SUBJECT_PREFIX")


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cacheops",
    "debug_toolbar",
    "django_filters",
    "django_tables2",
    "rest_framework",
    "netfields",
    "taggit",
    "taggit_serializer",
    "peering",
    "peeringdb",
    "users",
    "utils",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "users.middleware.LastSearchMiddleware",
    "utils.middleware.ExceptionCatchingMiddleware",
    "utils.middleware.ObjectChangeMiddleware",
    "utils.middleware.RequireLoginMiddleware",
]

ROOT_URLCONF = "peering_manager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR + "/templates/"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "utils.context_processors.settings",
            ]
        },
    }
]

WSGI_APPLICATION = "peering_manager.wsgi.application"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Authentication URL
LOGIN_URL = "/{}login/".format(BASE_PATH)


# Messages
MESSAGE_TAGS = {messages.ERROR: "danger"}


# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR + "/static/"
STATIC_URL = "/{}static/".format(BASE_PATH)
STATICFILES_DIRS = (os.path.join(BASE_DIR, "project-static"),)

# Django debug toolbar
INTERNAL_IPS = ["127.0.0.1", "::1"]

try:
    HOSTNAME = socket.gethostname()
except Exception:
    HOSTNAME = "localhost"
