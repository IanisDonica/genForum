# Generated by Django 4.1.4 on 2023-02-17 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_reactiontypes_alter_reaction_reaction_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_locked',
            field=models.BooleanField(default=False),
        ),
    ]