# Generated by Django 4.1.4 on 2023-04-06 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0076_alter_notification_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='view_permisions',
            field=models.ManyToManyField(blank=True, null=True, to='base.badgetype'),
        ),
    ]
