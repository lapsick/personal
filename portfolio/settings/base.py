"""Shared Django + Wagtail settings for all environments.

Environment-specific modules (``dev``, ``prod``) import ``*`` from here and
override what differs. Nothing secret or environment-specific lives in this file.
"""

from pathlib import Path

# portfolio/settings/base.py -> repo root is three parents up.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Wagtail requires a project name for its admin branding.
WAGTAIL_SITE_NAME = "Personal Professional Website"

# -- Applications ------------------------------------------------------------

INSTALLED_APPS = [
    # Local apps.
    "core",
    "home",
    "projects",
    "blog",
    "contact",
    # Wagtail.
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.sitemaps",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    # Wagtail dependencies.
    "modelcluster",
    "taggit",
    # Django.
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

MIDDLEWARE = [
    # Must be first so security headers/redirects apply to every response.
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # WhiteNoise serves static files (inert under CodeRed's native serving).
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "portfolio.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                "core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "portfolio.wsgi.application"

# -- Password validation -----------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -- Internationalization ----------------------------------------------------

# Single English locale for v1; drives the ``<html lang>`` attribute.
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -- Static & media ----------------------------------------------------------

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # Plain storage locally/in tests (no collectstatic manifest required);
        # production overrides this with WhiteNoise's compressed manifest
        # storage for hashed, long-cache, cache-busting static files.
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Local-memory cache backing template-fragment caching (nav/list fragments).
# Production may swap this for a shared backend without code changes.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "portfolio-default",
    }
}

# django-treebeard 5.x emits a forward-compat warning about Wagtail's page/
# collection managers not subclassing MP_NodeManager (only an error under a
# future Treebeard 6). Runtime is unaffected; silence the noise.
SILENCED_SYSTEM_CHECKS = ["treebeard.E001"]

# -- Wagtail -----------------------------------------------------------------

WAGTAILADMIN_BASE_URL = "http://localhost:8000"
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}
# Restrict resume/document uploads to safe, expected formats.
WAGTAILDOCS_EXTENSIONS = ["pdf", "doc", "docx", "odt", "txt"]

# -- Contact form spam protection (D5) ---------------------------------------

# Minimum seconds a genuine visitor needs to fill the contact form; faster
# submissions are treated as bots (time-trap). Overridable per environment.
CONTACT_FORM_MIN_FILL_SECONDS = 2
# Max age of a signed form-render timestamp before it is considered expired.
CONTACT_FORM_MAX_AGE_SECONDS = 60 * 60  # 1 hour

# Data-minimisation retention limit for stored contact submissions (D11).
# The ``prune_contact_submissions`` management command deletes older rows.
CONTACT_SUBMISSION_RETENTION_DAYS = 365
