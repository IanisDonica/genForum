# Generated by Django 4.1.4 on 2023-04-03 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0071_alter_notification_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='action_type',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='notification',
            name='message',
            field=models.CharField(blank=True, max_length=99999, null=True),
        ),
    ]