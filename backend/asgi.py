"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import pymysql
from dotenv import load_dotenv
from django.core.asgi import get_asgi_application

pymysql.install_as_MySQLdb()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

load_dotenv()
application = get_asgi_application()
