# Generated by Django 4.1.4 on 2023-03-28 07:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0063_badgetype_unlock_post_perm'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='edited_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='edited_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='has_new_version',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='comment',
            name='previous',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.comment'),
        ),
    ]