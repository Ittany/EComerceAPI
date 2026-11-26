from pathlib import Path
import os
BASE_DIR=Path(__file__).resolve().parent
SECRET_KEY=os.getenv('SECRET_KEY','local-development-only')
DEBUG=os.getenv('DEBUG','1')=='1'
ALLOWED_HOSTS=['localhost','127.0.0.1']
ROOT_URLCONF='urls'
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','rest_framework','rest_framework.authtoken','django_filters','corsheaders','drf_spectacular','api']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','corsheaders.middleware.CorsMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware']
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
STATIC_URL='static/'
LANGUAGE_CODE='es-pe'
TIME_ZONE='America/Lima'
USE_TZ=True
CORS_ALLOWED_ORIGINS=['https://tecnomarket.pe', 'https://app.tecnomarket.pe', 'https://admin.tecnomarket.pe']
CORS_ALLOW_CREDENTIALS=True
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.TokenAuthentication','rest_framework.authentication.SessionAuthentication'],'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticatedOrReadOnly'],'DEFAULT_FILTER_BACKENDS':['django_filters.rest_framework.DjangoFilterBackend','rest_framework.filters.SearchFilter','rest_framework.filters.OrderingFilter'],'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination','PAGE_SIZE':24,'DEFAULT_SCHEMA_CLASS':'drf_spectacular.openapi.AutoSchema','DEFAULT_THROTTLE_CLASSES':['rest_framework.throttling.AnonRateThrottle','rest_framework.throttling.UserRateThrottle'],'DEFAULT_THROTTLE_RATES':{'anon':'60/hour','user':'2000/hour','checkout':'10/hour','burst':'20/min','search':'100/hour'}}
SPECTACULAR_SETTINGS={'TITLE':'TecnoMarketAPI','VERSION':'1.0.0'}
INSTALLED_APPS += ['drf_spectacular_sidecar']
SPECTACULAR_SETTINGS.update(SWAGGER_UI_DIST='SIDECAR',SWAGGER_UI_FAVICON_HREF='SIDECAR',REDOC_DIST='SIDECAR')
