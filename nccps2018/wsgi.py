"""
WSGI config for nccps2018 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys



sys.path.append('/Sites/nccps_2018/nccps-2018')
sys.path.insert(1, '/Sites/nccps_2018/nccps-2018')
sys.path.insert(1, '/Sites/nccps_2018/env_nccps/lib/python3.6/site-packages')

activate_this = '/Sites/nccps_2018/env_nccps/bin/activate_this.py'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nccps2018.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

