import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dummy_secret")
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'profiles.apps.ProfilesConfig', 
    "rest_framework",
    "corsheaders",
    "users",
    'posts',
    'profile',
    'followers',
    'engagement',
    'feed',
    'notifications',
    'admin_api',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "socialconnect.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "socialconnect.wsgi.application"

fallback_url = (
    f"postgresql://{os.getenv('PGUSER', 'postgres')}:"
    f"{os.getenv('PGPASSWORD', 'Deanambrose%4012345')}@"
    f"{os.getenv('PGHOST', 'db.rwocivhozcmfswyilrwy.supabase.co')}:"
    f"{os.getenv('PGPORT', '5432')}/"
    f"{os.getenv('PGDATABASE', 'postgres')}?sslmode=require"
)

# Use DATABASE_URL if available, otherwise fallback
DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DATABASE_URL", fallback_url),
        conn_max_age=600,
        ssl_require=True
    )
}



LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------- Supabase ----------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")




REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"]
}


AUTH_USER_MODEL = 'users.CustomUser'

CORS_ALLOW_ALL_ORIGINS = True
