# Generated by Django 4.1.4 on 2023-03-24 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0045_remove_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]