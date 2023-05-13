# Generated by Django 4.1.4 on 2023-03-25 08:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0048_badgetype_edit_posts_perm'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='view_permisions',
            field=models.ManyToManyField(blank=True, to='base.badgetype'),
        ),
        migrations.AlterField(
            model_name='post',
            name='profile',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
