from __future__ import absolute_import, unicode_literals
from celery import Celery
from django.utils import timezone

app = Celery('tasks', broker='pyamqp://guest@localhost//')
@app.task
def removebadges():
    from .models import Badge
    import datetime
    from django.db.models import F

    badges = Badge.objects.filter(
        date_applied__lt=timezone.now() - F('badge_duration'),  # Filter based on creation date + duration
        badge_duration__gt=datetime.timedelta(seconds=0)  # Exclude badges with timedelta 0
    )
    badges.delete()
