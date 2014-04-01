"""
Django settings for openreview project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# This function is used to convert environment variables to booleans
def get_bool(var, default=None, err_empty=False):
    """
    Gets the value of variable `var` from environment variables and tries to convert
    it to a boolean. Valid values are: {True, False, 0, 1}.

    @param var: environment value to interpret
    @type var: str

    @param default: if no (valid) value is found, use this one
    @type default: all

    @rtype: bool
    """
    value = os.environ.get(var, "").lower().strip()

    if value in ["true", "1"]:
        return True

    if value in ["false", "0"]:
        return False

    if len(value):
        # You shouldn't use print in 'normal' code, however upon importing
        # settings cryptic (and generally unhelpful) error messages are displayed
        # in case of exceptions.
        errmsg = "Could not interpret environment variable {value!r} as boolean value.".format(**locals())
        print(errmsg)
        raise ValueError(errmsg)

    if err_empty:
        errmsg = "Environment variable {var!r} must be specified.".format(**locals())
        print(errmsg)
        raise ValueError(errmsg)

    return default

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool("DJANGO_DEBUG", True)
FORCE_STATICFILES = get_bool("DJANGO_FORCE_STATICFILES", False)

if not DEBUG:
    TEMPLATE_DEBUG = False
else:
    get_bool("DJANGO_TEMPLATE_DEBUG", DEBUG)

if not DEBUG:
    SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
    if not SECRET_KEY:
        errmsg = "Environment variable DJANGO_SECRET_KEY must be specified."
        print(errmsg)
        raise ValueError(errmsg)
else:
    SECRET_KEY = "longhairdontcare"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split()

# Overriding default User object
AUTH_USER_MODEL = 'accounts.User'

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'south',
    'haystack',
    'openreview.apps.accounts',
    'openreview.apps.papers',
    'openreview.apps.main',
    'openreview.apps.tools',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)

ROOT_URLCONF = 'openreview.urls'
WSGI_APPLICATION = 'openreview.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get("DJANGO_DB_ENGINE", 'django.db.backends.postgresql_psycopg2'),
        'NAME': os.environ.get("DJANGO_DB_NAME", 'openreview'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}

if DEBUG:
    CACHE_MIDDLEWARE_KEY_PREFIX = "DEBUG_"

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_ROOT = os.path.join(BASE_DIR, "collected_static")

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_ENABLED = get_bool("DJANGO_COMPRESS", not DEBUG)
COMPRESS_PARSER = 'compressor.parser.LxmlParser'

COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', 'coffee --compile --stdio'),
)
