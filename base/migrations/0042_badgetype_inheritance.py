# Generated by Django 4.1.4 on 2023-03-21 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0041_badgetype_edit_comments_perm'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgetype',
            name='inheritance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.badgetype'),
        ),
    ]