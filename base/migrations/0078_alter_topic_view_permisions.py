# Generated by Django 4.1.4 on 2023-04-07 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0077_alter_topic_view_permisions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='view_permisions',
            field=models.ManyToManyField(blank=True, to='base.badgetype'),
        ),
    ]
