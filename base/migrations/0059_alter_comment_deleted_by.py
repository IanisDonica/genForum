# Generated by Django 4.1.4 on 2023-03-25 15:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0058_badgetype_delete_comments_perm_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='deleted_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_by', to=settings.AUTH_USER_MODEL),
        ),
    ]