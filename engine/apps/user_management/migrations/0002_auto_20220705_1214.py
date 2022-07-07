# Generated by Django 3.2.13 on 2022-07-05 12:14

import apps.user_management.models.user
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0001_squashed_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='_timezone',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='working_hours',
            field=models.JSONField(default=apps.user_management.models.user.default_working_hours, null=True),
        ),
    ]
