from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'forum.settings')

app = Celery('forum')


app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

from .settings import PERIODIC_TAKSK_INTERVAL

app.conf.beat_schedule = {
    'do-this-every-2-seconds': {
        'task': 'base.tasks.removebadges',
        'schedule': PERIODIC_TAKSK_INTERVAL
    },
}