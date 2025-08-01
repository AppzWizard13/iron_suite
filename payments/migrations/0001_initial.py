# Generated by Django 5.1.2 on 2025-05-11 12:50

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0009_temporder_processed'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentAPILog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('INITIATE', 'Initiate Payment'), ('FETCH_SESSION', 'Fetch Session'), ('GET_ORDER', 'Get Existing Order'), ('ERROR', 'Error')], max_length=50)),
                ('request_url', models.URLField(max_length=500)),
                ('request_payload', models.TextField(blank=True, null=True)),
                ('response_status', models.IntegerField(blank=True, null=True)),
                ('response_body', models.TextField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.order')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
