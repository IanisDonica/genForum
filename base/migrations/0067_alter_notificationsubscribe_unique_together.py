# Generated by Django 4.1.4 on 2023-04-02 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('base', '0066_notificationsubscribe_notification'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='notificationsubscribe',
            unique_together={('user', 'content_type', 'object_id')},
        ),
    ]