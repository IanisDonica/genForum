# Generated by Django 4.1.4 on 2023-03-21 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0037_badge_badge_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='badges',
            field=models.ManyToManyField(to='base.badgetype'),
        ),
        migrations.DeleteModel(
            name='Badge',
        ),
    ]
