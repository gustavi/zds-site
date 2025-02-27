from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger
import sentry_sdk

from .abstract_base import *

# For secrets, prefer `config[key]` over `config.get(key)` in this
# file because we really want to raise an error if a secret is not
# defined.


###############################################################################
# DJANGO SETTINGS


DEBUG = False

USE_L10N = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config["databases"]["default"].get("name", "zdsdb"),
        "USER": config["databases"]["default"].get("user", "zds"),
        "PASSWORD": config["databases"]["default"]["password"],
        "HOST": "localhost",
        "PORT": "",
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    },
}

ALLOWED_HOSTS = [
    "beta.zestedesavoir.com",
    "scaleway.zestedesavoir.com",
    "zdsappserver",
    "gandi.zestedesavoir.com",
    "gandi.zestedesavoir.com.",
    ".zestedesavoir.com",
    ".zestedesavoir.com.",
    "127.0.0.1",
    "localhost",
    "163.172.171.246",
]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = False
EMAIL_HOST = "localhost"
EMAIL_PORT = 25

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 4

MEDIA_ROOT = Path("/opt/zds/data/media")

STATIC_ROOT = Path("/opt/zds/data/static")
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

django_template_engine["APP_DIRS"] = False
django_template_engine["OPTIONS"]["loaders"] = [
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    ),
]


def _get_version():
    from zds import __version__, git_version

    if git_version is None:
        return __version__
    else:
        return "{}/{}".format(__version__, git_version[:7])


sentry_sdk.init(
    dsn=config["sentry"]["dsn"],
    integrations=[DjangoIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    # By default the SDK will try to use the SENTRY_RELEASE
    # environment variable, or infer a git commit
    # SHA as release, however you may want to set
    # something more human-readable.
    release=_get_version().replace("/", "#"),
    # /!\ It cannot contain slashes
    environment=config["sentry"]["environment"],
)

# Ignoring emarkdown logging because it is too noisy
ignore_logger("zds.utils.templatetags.emarkdown")


###############################################################################
# REQUIREMENTS SETTINGS


# easy-thumbnails
# http://easy-thumbnails.readthedocs.io/en/2.1/ref/optimize/
THUMBNAIL_OPTIMIZE_COMMAND = {
    "png": "/usr/bin/optipng {filename}",
    "gif": "/usr/bin/optipng {filename}",
    "jpeg": "/usr/bin/jpegoptim {filename}",
}


# python-social-auth
# http://psa.matiasaguirre.net/docs/configuration/django.html
SOCIAL_AUTH_PIPELINE = (
    "social.pipeline.social_auth.social_details",
    "social.pipeline.social_auth.social_uid",
    "social.pipeline.social_auth.auth_allowed",
    "social.pipeline.social_auth.social_user",
    "social.pipeline.user.get_username",
    "social.pipeline.social_auth.associate_by_email",
    "social.pipeline.user.create_user",
    "zds.member.models.save_profile",
    "social.pipeline.social_auth.associate_user",
    "social.pipeline.social_auth.load_extra_data",
    "social.pipeline.user.user_details",
)


###############################################################################
# ZESTE DE SAVOIR SETTINGS


ES_SEARCH_INDEX["shards"] = config["elasticsearch"].get("shards", 3)


ZDS_APP["site"]["association"]["email"] = "communication@zestedesavoir.com"

# content
# ZDS_APP['content']['build_pdf_when_published'] = False
ZDS_APP["article"]["repo_path"] = "/opt/zds/data/articles-data"
ZDS_APP["content"]["repo_private_path"] = "/opt/zds/data/contents-private"
ZDS_APP["content"]["repo_public_path"] = "/opt/zds/data/contents-public"
ZDS_APP["content"]["extra_content_generation_policy"] = "WATCHDOG"

ZDS_APP["visual_changes"] = zds_config.get("visual_changes", [])

ZDS_APP["very_top_banner"] = config.get("very_top_banner", False)
