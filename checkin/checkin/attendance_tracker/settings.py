"""

Django settings for attendance_tracker project.

"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import ldap
#from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType
import django.utils.http

#DEBUG = <%= if @debug then 'True' else 'False' end %>
#TEMPLATE_DEBUG = DEBUG
#
#ADMINS = (
#<% (@admins or []).each do |email, name| %>
#  ('''<%= name %>''', '''<%= email %>'''),
#<% end %>
#)

#MANAGERS = ADMINS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'SECRET KEY'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['thethomasrea.dynu.com','192.168.2.212']

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
AUTO_LOGOUT_DELAY = 30

# Application definition

LOGIN_URL = 'loginURL'
LOGIN_REDIRECT_URL = 'studentSignInURL'

INSTALLED_APPS = (
    'attendance',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'attendance.middleware.AutoLogout',
)

AUTHENTICATION_BACKENDS = [
    #'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'attendance_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'attendance_tracker.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'NAME': 'YOUR_DB_NAME',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'YOUR_DB_USER',
        'PASSWORD': 'YOUR_DB_USER_PASSWORD',
	'HOST': 'postgres1.cs.clemson.edu',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'filters': {
  #  'suppress_unreadable_post': {
  #    '()': 'webhandin.handin.logging.SuppressUnreadablePost',
  #  },
  },
  'handlers': {
    'mail_admins': {
      'level': 'ERROR',
      'class': 'django.utils.log.AdminEmailHandler',
      'filters': [],
    }
  },
  'loggers': {
    'django.request': {
      'handlers': ['mail_admins'],
      'level': 'ERROR',
      'propagate': True,
    },
  }
}

#
# LDAP
#

AUTH_LDAP_SERVER_URI = 'LDAP_SERVER_URI'
AUTH_LDAP_BIND_DN = 'BINDING'
AUTH_LDAP_BIND_PASSWORD = 'PASSWORD'
AUTH_LDAP_USER_SEARCH = LDAPSearch('o=clemsonu', ldap.SCOPE_SUBTREE, '(&(objectClass=inetOrgPerson)(uid=%(user)s))')
AUTH_LDAP_USER_ATTR_MAP = {
  'first_name': 'givenName',
  'last_name': 'sn',
  'email': 'mail',
}
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
  'is_staff': 'cn=coes_socunix,ou=group,ou=SoC,ou=CES,o=CLEMSONU',
  'is_superuser': 'cn=coes_socunix_fulltime,ou=group,ou=SoC,ou=CES,o=CLEMSONU',
}
AUTH_LDAP_GROUP_SEARCH = LDAPSearch('ou=group,ou=SoC,ou=CES,o=clemsonu', ldap.SCOPE_ONELEVEL, '(objectClass=groupOfNames)')
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()

#
# CHECKIN
#

def GET_USER_BY_USERNAME(username):
  from django.contrib.auth.models import User
  from django_auth_ldap.backend import LDAPBackend

  for domain in ('@clemson.edu', '@g.clemson.edu', '@exchange.clemson.edu'):
    if username.lower().endswith(domain):
      username = username[:-len(domain)]
      break

  try:
    return User.objects.get(username=username)
  except User.DoesNotExist:
    backend = LDAPBackend()
    user = backend.populate_user(username)
    if user is None:
      raise User.DoesNotExist('%s not in LDAP or database' % username)
    return user
