# Generated by Django 4.2 on 2023-05-03 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0089_badgetype_move_threads_perm'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgetype',
            name='delete_post_perm',
            field=models.BooleanField(default=None, null=True),
        ),
    ]
