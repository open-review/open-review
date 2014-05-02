"""
Django settings for openreview project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from openreview.apps.tools.string import get_bool

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

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
    'rest_framework',
    'openreview.apps.accounts',
    'openreview.apps.papers',
    'openreview.apps.main',
    'openreview.apps.tools',
    'openreview.apps.api',
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

"""
Unfortunatly, it is necassary to explicitly define another database for testing
To garantuee test isolation. http://bwreilly.github.io/blog/2013/07/21/testing-search-haystack-in-django/
"""
HAYSTACK_TESTING_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': '127.0.0.1:9200/',
        'INDEX_NAME': 'haystack_test',
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

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

REST_FRAMEWORK = {
    # Use hyperlinked styles by default. Only used if the `serializer_class`
    # attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS': 'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        'openreview.apps.api.permissions.ObjectPermissions',
    ],

    'DEFAULT_PAGINATION_SERIALIZER_CLASS': 'rest_framework.pagination.PaginationSerializer',

    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100
}
