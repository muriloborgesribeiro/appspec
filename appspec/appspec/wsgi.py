# appspec/wsgi.py — WSGI config for APPSPEC project
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appspec.settings')
application = get_wsgi_application()
