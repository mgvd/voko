"""
Django settings for vokou project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'da)=ydvhyj*u6%ldu_8hf%1op2efv!3q*%(ks=j19dvi$fu0oh'

DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'

INSTALLED_APPS += ['debug_toolbar',]
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
INTERNAL_IPS = ['127.0.0.1']

CAPTCHA_ENABLED = False

try:
    from .local import *
except ImportError:
    pass
