# Generated by Django 5.1.2 on 2025-07-29 17:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_customuser_gym'),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationconfig',
            name='gym',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='notification_config', to='accounts.gym'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notificationlog',
            name='gym',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='notification_log', to='accounts.gym'),
            preserve_default=False,
        ),
    ]
