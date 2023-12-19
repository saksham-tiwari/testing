# Generated by Django 5.0 on 2023-12-19 03:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yoga', '0002_offer_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='yogabatch',
            name='yoga_users',
        ),
        migrations.AddField(
            model_name='yogabooking',
            name='yoga_batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='yoga_users', to='yoga.yogabatch'),
        ),
    ]