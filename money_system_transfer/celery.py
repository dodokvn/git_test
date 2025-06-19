from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Définir le module de configuration Django par défaut pour 'celery'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "money_system_transfer.settings")

app = Celery("money_system_transfer")

# Utilise les paramètres de configuration définis dans settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Recherche automatiquement les tâches dans tous les fichiers tasks.py des apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
