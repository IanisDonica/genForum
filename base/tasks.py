from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')
@app.task
def removebadge(badgeid):
    from .models import Badge
    badge = Badge.objects.get(id=badgeid)
    badge.delete()

