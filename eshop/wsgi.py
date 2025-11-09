"""
WSGI config for eshop project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Use production settings if RAILWAY_ENVIRONMENT is set, otherwise development
default_settings = "eshop.settings.production" if os.environ.get('RAILWAY_ENVIRONMENT') else "eshop.settings.development"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings)

application = get_wsgi_application()
