# Generated by Django 4.2 on 2023-04-24 15:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0083_badgetype_see_deleted_post_perm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(verbose_name=datetime.datetime(2023, 4, 24, 15, 53, 24, 478921, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='post',
            name='created',
            field=models.DateTimeField(verbose_name=datetime.datetime(2023, 4, 24, 15, 53, 24, 477796, tzinfo=datetime.timezone.utc)),
        ),
    ]
