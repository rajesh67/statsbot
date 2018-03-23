"""
Django settings for statsbot_project project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import dj_database_url
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f57s+v#&#75*8)bxmiwr^#sk#=k$e%ef(-@65slmljx=p3ic+y'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '*', 'statsbot.org']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'shopping',
    'app',

    #third-party apps
    'graphos',
    'whitenoise',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'statsbot_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            "templates",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.static',
                'django.template.context_processors.csrf',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'statsbot_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

#=============lOCALHOST DATABSE CONFIGURATIONS===============
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'statsbotdb',
#         'USER' : 'rajeshmeena',
#         'PASSWORD' : '11cs30025',
#         'HOST' : 'localhost',
#         'PORT' : '',
#     }
# }
#=============lOCALHOST DATABSE =============================

#=============Heroku configuration DATABASE==================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.crowdfunding'),
    }
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
#==============================================================
# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT=os.path.join(BASE_DIR, "staticfiles/")
STATICFILES_DIRS=[
    os.path.join(BASE_DIR, "static/"),
]

MEDIA_URL = '/media/'
MEDIA_ROOT=os.path.join(BASE_DIR, "mediafiles/")
MEDIAFILES_DIRS=[
    os.path.join(BASE_DIR, "media/"),
]

# Access Tokens

FLIPKART_BASE_URL='https://affiliate-api.flipkart.net/affiliate/api/rajeshmee.json'
FLIPKART_SEARCH_URL='https://affiliate-api.flipkart.net/affiliate/1.0/search.json'
FLIPKART_OFFERS_XML_URL='https://affiliate-api.flipkart.net/affiliate/offers/v1/all/xml'
FLIPKART_OFFERS_JSON_URL='https://affiliate-api.flipkart.net/affiliate/offers/v1/all/json'
FLIPKART_DOTD_XML_URL='https://affiliate-api.flipkart.net/affiliate/offers/v1/dotd/xml'
FLIPKART_DOTD_JSON_URL='https://affiliate-api.flipkart.net/affiliate/offers/v1/dotd/json'
FLIPKART_DELTA_FEEDS_JSON_URL='https://affiliate-api.flipkart.net/affiliate/1.0/deltaFeeds/rajeshmee/category/{catId}/fromVersion/{version}.json'
FLIPKART_TOP_FEEDS_URL='https://affiliate-api.flipkart.net/affiliate/1.0/topFeeds/rajeshmee/category/{catId}.json'
