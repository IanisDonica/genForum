# Generated by Django 4.1.4 on 2023-01-31 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_alter_user_registration_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='registration_id',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
