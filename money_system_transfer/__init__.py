from __future__ import absolute_import, unicode_literals

# Importer l'instance Celery (important pour démarrer Celery avec Django)
from .celery import app as celery_app

__all__ = ("celery_app",)
