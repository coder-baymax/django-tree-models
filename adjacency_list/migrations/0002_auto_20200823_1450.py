# Generated by Django 3.1 on 2020-08-23 14:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adjacency_list', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime.utcnow),
        ),
        migrations.AlterField(
            model_name='node',
            name='update_time',
            field=models.DateTimeField(default=datetime.datetime.utcnow),
        ),
    ]
