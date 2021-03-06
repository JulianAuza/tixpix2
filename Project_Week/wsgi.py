"""
WSGI config for Project_Week project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'Project_Week.settings'

from django.core.wsgi import get_wsgi_application
from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Project_Week.settings")

application = get_wsgi_application()
application = DjangoWhiteNoise(application)


