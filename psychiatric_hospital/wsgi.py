"""
WSGI config for psychiatric_hospital project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychiatric_hospital.settings')

application = get_wsgi_application()