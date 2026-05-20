from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")


def parse_list_env(name, default=""):
    value = env(name, default=default)
    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = env("SECRET_KEY", default="dev-only-secret-key")
DEBUG = env("DEBUG", default=False)
ALLOWED_HOSTS = parse_list_env("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = parse_list_env("CSRF_TRUSTED_ORIGINS")

railway_public_domain = env("RAILWAY_PUBLIC_DOMAIN", default="")
if railway_public_domain:
    ALLOWED_HOSTS.append(railway_public_domain)
    CSRF_TRUSTED_ORIGINS.append(f"https://{railway_public_domain}")

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
]

LOCAL_APPS = [
    "core.apps.CoreConfig",
    "applications.accounts.apps.AccountsConfig",
    "applications.properties.apps.PropertiesConfig",
    "applications.bookings.apps.BookingsConfig",
    "applications.pages.apps.PagesConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.LanguagePreferenceMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

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
                "core.context_processors.site_language",
            ],
        },
    },
]

DATABASE_URL = env("DATABASE_URL", default="")
if DATABASE_URL:
    DATABASES = {"default": env.db("DATABASE_URL")}
    DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=600)
else:
    DB_ENGINE = env("DB_ENGINE", default="django.db.backends.postgresql")

if not DATABASE_URL and DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": BASE_DIR / env("DB_NAME", default="db.sqlite3"),
        }
    }
elif not DATABASE_URL:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": env("DB_NAME", default="wynwood"),
            "USER": env("DB_USER", default="postgres"),
            "PASSWORD": env("DB_PASSWORD", default="postgres"),
            "HOST": env("DB_HOST", default="localhost"),
            "PORT": env("DB_PORT", default="5432"),
        }
    }

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "staticfiles"]
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "pages:home"
LOGOUT_REDIRECT_URL = "pages:home"

EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="reservas@wynwood-house.test")

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}
