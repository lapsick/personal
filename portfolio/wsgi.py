"""WSGI config for the portfolio project.

Exposes the WSGI callable as a module-level variable named ``application``.
This entrypoint is required by CodeRed Cloud's managed hosting.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfolio.settings.prod")

application = get_wsgi_application()
